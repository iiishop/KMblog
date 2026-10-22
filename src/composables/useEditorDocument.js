import { computed, onScopeDispose, ref, shallowRef, watch } from 'vue';

export function useEditorDocument({ api, normalizePath, storageKey, onSaved = () => {}, describeError }) {
    const currentFile = shallowRef(null);
    const content = ref('');
    const version = shallowRef(null);
    const savedContent = ref('');
    const isNew = ref(false);
    const isSaving = ref(false);
    const isOpening = ref(false);
    const lastSaveTime = ref(null);
    const issue = shallowRef(null);
    const draft = shallowRef(null);
    const draftWarning = ref('');
    const leavePrompt = ref(false);
    const isDirty = computed(() => !!currentFile.value && (isNew.value || content.value !== savedContent.value));
    const saveStatus = computed(() => isSaving.value ? 'saving' : issue.value?.kind === 'conflict' ? 'conflict' :
        issue.value?.kind === 'save' ? 'error' : isDirty.value ? 'unsaved' : 'saved');
    let savePromise = null;
    let loadController = null;
    let saveTimer;
    let draftTimer;
    let generation = 0;
    let hydrating = false;
    let disposed = false;
    let resolveLeave;
    let leavePromise;

    const keyFor = file => `${storageKey}:${normalizePath(file.path)}`;
    const messageFor = error => describeError?.(error) || error.message || '操作失败，请重试。';
    function removeDraft(file = currentFile.value) {
        if (!file) return;
        try { localStorage.removeItem(keyFor(file)); } catch { /* Storage may be disabled. */ }
    }
    function persistDraft() {
        clearTimeout(draftTimer);
        if (!currentFile.value || draft.value) return;
        if (!isDirty.value) { removeDraft(); return; }
        try {
            localStorage.setItem(keyFor(currentFile.value), JSON.stringify({
                content: content.value, version: version.value, savedAt: Date.now()
            }));
            draftWarning.value = '';
        } catch {
            draftWarning.value = '浏览器无法保存本地草稿，请及时保存文件或下载副本。';
        }
    }
    function scheduleSave() {
        clearTimeout(saveTimer);
        if (isDirty.value && !issue.value && !draft.value && !isOpening.value) {
            saveTimer = setTimeout(() => { void save(); }, 1500);
        }
    }
    watch(content, () => {
        if (hydrating || !currentFile.value) return;
        clearTimeout(draftTimer);
        draftTimer = setTimeout(persistDraft, 250);
        scheduleSave();
    }, { flush: 'sync' });

    async function save({ force = false } = {}) {
        clearTimeout(saveTimer);
        if (!currentFile.value || disposed || draft.value) return false;
        // Repeated shortcuts and autosave share one request, never race versions.
        if (savePromise) return savePromise;
        if (issue.value?.kind === 'conflict' && !force) return false;
        if (!isDirty.value && !force) return true;
        persistDraft();
        const snapshot = { file: currentFile.value, content: content.value, version: version.value, generation };
        isSaving.value = true;
        issue.value = null;
        savePromise = (async () => {
            try {
                const response = await api.post('/files/save', {
                    path: normalizePath(snapshot.file.path), content: snapshot.content,
                    ...(force ? {} : { expectedVersion: snapshot.version })
                });
                if (disposed || snapshot.generation !== generation) return false;
                version.value = response.data.version;
                savedContent.value = snapshot.content;
                isNew.value = false;
                lastSaveTime.value = Date.now();
                persistDraft();
                onSaved();
                return !isDirty.value;
            } catch (error) {
                if (!disposed && snapshot.generation === generation) {
                    issue.value = error.response?.status === 409
                        ? { kind: 'conflict', message: '磁盘文件已被其他程序修改。当前内容和本地草稿都已保留，请选择如何处理。' }
                        : { kind: 'save', message: `保存失败：${messageFor(error)}` };
                }
                return false;
            } finally {
                savePromise = null;
                if (!disposed && snapshot.generation === generation) {
                    isSaving.value = false;
                    // Edits typed during the request still need a later save.
                    scheduleSave();
                }
            }
        })();
        return savePromise;
    }

    function answerLeave(choice) {
        leavePrompt.value = false;
        resolveLeave?.(choice);
        resolveLeave = null;
    }
    async function canLeave() {
        if (leavePromise) return leavePromise;
        clearTimeout(saveTimer);
        persistDraft();
        if (savePromise) await savePromise;
        clearTimeout(saveTimer);
        if (disposed) return false;
        if (!isDirty.value) return true;
        leavePromise = (async () => {
            const choice = await new Promise(resolve => { resolveLeave = resolve; leavePrompt.value = true; });
            if (choice === 'save') return save();
            if (choice === 'discard') { removeDraft(); return true; }
            return false;
        })();
        try { return await leavePromise; }
        finally { leavePromise = null; }
    }
    function applyDocument(file, data, newFile = false) {
        generation++;
        clearTimeout(saveTimer);
        clearTimeout(draftTimer);
        hydrating = true;
        currentFile.value = { ...file };
        content.value = data.content;
        savedContent.value = newFile ? '' : data.content;
        version.value = data.version || null;
        isNew.value = newFile;
        lastSaveTime.value = null;
        issue.value = null;
        draft.value = null;
        hydrating = false;
        try {
            const stored = JSON.parse(localStorage.getItem(keyFor(file)) || 'null');
            if (stored && typeof stored.content === 'string' && stored.content !== data.content) draft.value = stored;
            else if (stored) removeDraft(file);
        } catch { /* Ignore a corrupt or inaccessible draft. */ }
        if (newFile) persistDraft();
    }
    async function open(file, { createContent, reload = false } = {}) {
        if (isOpening.value || disposed || !file) return false;
        if (!reload && currentFile.value?.path === file.path) return true;
        isOpening.value = true;
        clearTimeout(saveTimer);
        try {
            if (!await canLeave() || disposed) return false;
            loadController = new AbortController();
            let data;
            let newFile = false;
            try {
                const response = await api.get('/files/read', {
                    params: { path: normalizePath(file.path) }, signal: loadController.signal
                });
                data = response.data;
            } catch (error) {
                if (!createContent || error.response?.status !== 404) throw error;
                data = { content: createContent(), version: null };
                newFile = true;
            }
            if (disposed) return false;
            applyDocument(file, data, newFile);
            return true;
        } catch (error) {
            if (!disposed && !loadController?.signal.aborted) issue.value = { kind: 'load', message: `打开失败：${messageFor(error)}` };
            return false;
        } finally {
            isOpening.value = false;
            loadController = null;
            if (!disposed) scheduleSave();
        }
    }
    function restoreDraft() {
        if (!draft.value) return;
        const recovered = draft.value;
        draft.value = null;
        // Restoring never writes to disk until the user explicitly saves.
        issue.value = JSON.stringify(recovered.version) !== JSON.stringify(version.value)
            ? { kind: 'conflict', message: '草稿对应的磁盘版本已变化。已恢复草稿，请核对内容后再决定是否覆盖保存。' }
            : { kind: 'draft', message: '已恢复本地草稿。检查内容后保存到文件。' };
        content.value = recovered.content;
        persistDraft();
    }
    function dismissDraft() { draft.value = null; removeDraft(); }
    function reset() {
        generation++;
        clearTimeout(saveTimer); clearTimeout(draftTimer);
        removeDraft();
        currentFile.value = null;
        content.value = savedContent.value = '';
        version.value = null;
        isNew.value = false;
        issue.value = draft.value = null;
        lastSaveTime.value = null;
        isSaving.value = false;
    }
    function relocate(path, name) {
        if (!currentFile.value) return;
        removeDraft();
        currentFile.value = { ...currentFile.value, path, name: name || currentFile.value.name };
        persistDraft();
    }
    onScopeDispose(() => {
        persistDraft();
        disposed = true;
        generation++;
        clearTimeout(saveTimer); clearTimeout(draftTimer);
        loadController?.abort();
        answerLeave('cancel');
    });
    return {
        currentFile, content, version, isDirty, isSaving, isOpening, lastSaveTime, saveStatus,
        issue, draft, draftWarning, leavePrompt, save, open, reset, relocate, canLeave, answerLeave,
        restoreDraft, dismissDraft, persistDraft
    };
}
