import { mount, flushPromises } from '@vue/test-utils';
import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
const state = vi.hoisted(() => ({ models: [], editor: null, onChange: null, actions: [] }));
vi.mock('monaco-editor/esm/vs/editor/editor.worker?worker', () => ({ default: class {} }));
vi.mock('monaco-editor', () => ({
    KeyMod: { CtrlCmd: 1, Shift: 2 }, KeyCode: {},
    editor: {
        TrackedRangeStickiness: { NeverGrowsWhenTypingAtEdges: 1 },
        setTheme: vi.fn(), setModelLanguage: vi.fn(),
        createModel: (value) => {
            const model = { value, disposed: false, getValue() { return this.value; }, setValue(value) { this.value = value; }, dispose() { this.disposed = true; }, isDisposed() { return this.disposed; }, deltaDecorations: () => ['marker'], getDecorationRange: () => ({}), getFullModelRange: () => ({}) };
            state.models.push(model);
            return model;
        },
        create: (node) => {
            state.editor = {
                model: null, setModel(model) { this.model = model; }, getModel() { return this.model; }, getValue() { return this.model.value; },
                getPosition: () => ({ lineNumber: 1, column: 1 }), getSelection: () => ({}), getDomNode: () => node,
                saveViewState: () => ({ cursor: 1 }), restoreViewState: vi.fn(), updateOptions: vi.fn(),
                addAction: action => state.actions.push(action), onDidChangeCursorPosition: vi.fn(),
                onDidChangeModelContent: listener => { state.onChange = listener; }, onDidScrollChange: vi.fn(),
                pushUndoStop: vi.fn(), executeEdits: vi.fn((source, edits) => { state.editor.model.value += edits[0].text; state.onChange?.(); }),
                dispose: vi.fn(), layout: vi.fn(), focus: vi.fn()
            };
            return state.editor;
        }
    }
}));
import MonacoEditor from './MonacoEditor.vue';
let wrapper;
beforeEach(() => { state.models = []; state.actions = []; state.onChange = null; });
afterEach(() => { wrapper?.unmount(); vi.unstubAllGlobals(); });
const start = () => wrapper = mount(MonacoEditor, { props: { documentKey: 'a', modelValue: 'original', currentFileName: 'a.md' } });
const pasteImage = () => {
    const event = new Event('paste', { bubbles: true, cancelable: true });
    Object.defineProperty(event, 'clipboardData', { value: { items: [{ type: 'image/png', getAsFile: () => new File(['image'], 'a.png', { type: 'image/png' }) }] } });
    wrapper.element.dispatchEvent(event);
};
describe('Monaco editor session', () => {
    it('reuses the original document model and view state on return', async () => {
        start();
        const original = state.editor.getModel();
        await wrapper.setProps({ documentKey: 'b', modelValue: 'other' });
        expect(state.editor.getModel()).not.toBe(original);
        await wrapper.setProps({ documentKey: 'a', modelValue: 'original' });
        expect(state.editor.getModel()).toBe(original);
        expect(state.editor.restoreViewState).toHaveBeenCalled();
    });
    it('routes save and file-search shortcuts to the workspace', () => {
        start();
        state.actions.find(action => action.id === 'save-document').run();
        state.actions.find(action => action.id === 'search-files').run();
        expect(wrapper.emitted('save')).toHaveLength(1);
        expect(wrapper.emitted('search-files')).toHaveLength(1);
    });
    it('inserts each pasted image once using an undoable edit', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ path: 'a/image.png' }) }));
        start();
        pasteImage();
        await flushPromises();
        expect(fetch).toHaveBeenCalledTimes(1);
        expect(state.editor.executeEdits).toHaveBeenCalledExactlyOnceWith('paste-image', [{ range: {}, text: '![图片](<a/image.png>)' }]);
        expect(state.editor.pushUndoStop).toHaveBeenCalledTimes(2);
    });
    it('cancels insertion when the user switches files during upload', async () => {
        let finish;
        vi.stubGlobal('fetch', vi.fn(() => new Promise(resolve => { finish = resolve; })));
        start();
        pasteImage();
        const signal = fetch.mock.calls[0][1].signal;
        await wrapper.setProps({ documentKey: 'b', modelValue: 'other' });
        expect(signal.aborted).toBe(true);
        finish({ ok: true, json: async () => ({ path: 'a/image.png' }) });
        await flushPromises();
        expect(state.editor.executeEdits).not.toHaveBeenCalled();
        expect(state.editor.getValue()).toBe('other');
    });
    it('bounds the recent model cache and disposes every model on unmount', async () => {
        start();
        for (let index = 0; index < 10; index++) await wrapper.setProps({ documentKey: String(index), modelValue: String(index) });
        expect(state.models.filter(model => !model.disposed)).toHaveLength(8);
        wrapper.unmount();
        expect(state.models.every(model => model.disposed)).toBe(true);
    });
});
