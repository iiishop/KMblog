import { effectScope } from 'vue';
import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
import { useEditorDocument } from './useEditorDocument';

const file = name => ({ name, path: `/Posts/Markdowns/${name}`, type: 'file' });
const deferred = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b; }); return { promise, resolve, reject }; };
let scope, api, doc;
beforeEach(() => {
    vi.useFakeTimers();
    const stored = new Map();
    localStorage.getItem.mockImplementation(key => stored.get(key) ?? null);
    localStorage.setItem.mockImplementation((key, value) => stored.set(key, value));
    localStorage.removeItem.mockImplementation(key => stored.delete(key));
    api = { get: vi.fn().mockResolvedValue({ data: { content: 'original', version: { etag: 'v1' } } }), post: vi.fn().mockResolvedValue({ data: { version: { etag: 'v2' } } }) };
    scope = effectScope();
    doc = scope.run(() => useEditorDocument({ api, normalizePath: path => path.replace('/Posts/', ''), storageKey: 'draft' }));
});
afterEach(() => { scope.stop(); vi.useRealTimers(); vi.restoreAllMocks(); });

describe('editor document reliability', () => {
    it('debounces autosave and uses the loaded disk version', async () => {
        await doc.open(file('a.md'));
        doc.content.value = 'first';
        await vi.advanceTimersByTimeAsync(1000);
        doc.content.value = 'second';
        await vi.advanceTimersByTimeAsync(1000);
        expect(api.post).not.toHaveBeenCalled();
        await vi.advanceTimersByTimeAsync(500);
        expect(api.post).toHaveBeenCalledExactlyOnceWith('/files/save', { path: 'Markdowns/a.md', content: 'second', expectedVersion: { etag: 'v1' } });
        expect(doc.isDirty.value).toBe(false);
    });

    it('keeps edits made during a save dirty and serializes requests', async () => {
        await doc.open(file('a.md'));
        const pending = deferred();
        api.post.mockReturnValueOnce(pending.promise);
        doc.content.value = 'snapshot';
        const saving = doc.save();
        doc.content.value = 'newer edits';
        void doc.save();
        expect(api.post).toHaveBeenCalledTimes(1);
        pending.resolve({ data: { version: { etag: 'v2' } } });
        expect(await saving).toBe(false);
        expect(doc.isDirty.value).toBe(true);
        expect(JSON.parse(localStorage.getItem('draft:Markdowns/a.md')).content).toBe('newer edits');
        await vi.advanceTimersByTimeAsync(1500);
        expect(api.post).toHaveBeenLastCalledWith('/files/save', { path: 'Markdowns/a.md', content: 'newer edits', expectedVersion: { etag: 'v2' } });
        expect(doc.isDirty.value).toBe(false);
    });

    it('does not navigate away when saving fails', async () => {
        await doc.open(file('a.md'));
        doc.content.value = 'keep me';
        api.post.mockRejectedValue(new Error('offline'));
        const opening = doc.open(file('b.md'));
        expect(doc.leavePrompt.value).toBe(true);
        doc.answerLeave('save');
        expect(await opening).toBe(false);
        expect(doc.currentFile.value.name).toBe('a.md');
        expect(doc.content.value).toBe('keep me');
        expect(doc.saveStatus.value).toBe('error');
        expect(api.get).toHaveBeenCalledTimes(1);
        await vi.advanceTimersByTimeAsync(6000);
        expect(api.post).toHaveBeenCalledTimes(1);
    });

    it('requires explicit overwrite after a version conflict', async () => {
        await doc.open(file('a.md'));
        doc.content.value = 'mine';
        api.post.mockRejectedValueOnce({ response: { status: 409 } });
        expect(await doc.save()).toBe(false);
        doc.content.value += '!';
        await vi.advanceTimersByTimeAsync(6000);
        expect(await doc.save()).toBe(false);
        expect(api.post).toHaveBeenCalledTimes(1);
        expect(await doc.save({ force: true })).toBe(true);
        expect(api.post).toHaveBeenLastCalledWith('/files/save', { path: 'Markdowns/a.md', content: 'mine!' });
    });

    it('restores a draft without silently overwriting a newer disk version', async () => {
        localStorage.setItem('draft:Markdowns/a.md', JSON.stringify({ content: 'recovered', version: { etag: 'old' }, savedAt: 1 }));
        await doc.open(file('a.md'));
        expect(doc.content.value).toBe('original');
        doc.restoreDraft();
        expect(doc.content.value).toBe('recovered');
        expect(doc.issue.value.kind).toBe('conflict');
        await vi.advanceTimersByTimeAsync(6000);
        expect(api.post).not.toHaveBeenCalled();
    });

    it('cancels navigation without discarding changes', async () => {
        await doc.open(file('a.md'));
        doc.content.value = 'mine';
        const opening = doc.open(file('b.md'));
        doc.answerLeave('cancel');
        expect(await opening).toBe(false);
        expect(doc.currentFile.value.name).toBe('a.md');
        expect(doc.content.value).toBe('mine');
    });

    it('discards only the old draft and never autosaves it to the next file', async () => {
        await doc.open(file('a.md'));
        doc.content.value = 'discarded';
        const opening = doc.open(file('b.md'));
        doc.answerLeave('discard');
        expect(await opening).toBe(true);
        await vi.advanceTimersByTimeAsync(6000);
        expect(localStorage.getItem('draft:Markdowns/a.md')).toBeNull();
        expect(api.post).not.toHaveBeenCalled();
    });

    it('preserves the current file on a read error', async () => {
        await doc.open(file('a.md'));
        api.get.mockRejectedValueOnce(new Error('offline'));
        expect(await doc.open(file('b.md'))).toBe(false);
        expect(doc.currentFile.value.name).toBe('a.md');
        expect(doc.issue.value.kind).toBe('load');
    });

    it('does not carry discarded edits into a renamed document', async () => {
        await doc.open(file('a.md'));
        doc.content.value = 'discarded';
        const leaving = doc.canLeave();
        doc.answerLeave('discard');
        expect(await leaving).toBe(true);
        doc.relocate('/Posts/Markdowns/renamed.md', 'renamed.md');
        expect(doc.content.value).toBe('original');
        expect(doc.isDirty.value).toBe(false);
        expect(localStorage.getItem('draft:Markdowns/renamed.md')).toBeNull();
    });

    it('persists pending edits and cancels timers when disposed', async () => {
        await doc.open(file('a.md'));
        doc.content.value = 'last keystroke';
        scope.stop();
        expect(JSON.parse(localStorage.getItem('draft:Markdowns/a.md')).content).toBe('last keystroke');
        await vi.advanceTimersByTimeAsync(6000);
        expect(api.post).not.toHaveBeenCalled();
    });

    it('reports unavailable draft storage while disk saving still works', async () => {
        await doc.open(file('a.md'));
        localStorage.setItem.mockImplementation(() => { throw new Error('quota'); });
        doc.content.value = 'mine';
        doc.persistDraft();
        expect(doc.draftWarning.value).toContain('无法保存');
        expect(await doc.save()).toBe(true);
    });
});
