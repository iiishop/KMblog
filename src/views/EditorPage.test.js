import { mount, flushPromises } from '@vue/test-utils';
import { ref } from 'vue';
import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), delete: vi.fn() }));
vi.mock('axios', () => ({ default: { create: () => api, isCancel: () => false } }));
vi.mock('vue-router', () => ({ onBeforeRouteLeave: vi.fn() }));
vi.mock('@/composables/useTheme', () => ({ useTheme: () => ({ isDarkMode: ref(false), currentMode: ref('light'), toggleTheme: vi.fn() }) }));
vi.mock('@/components/Editor/MonacoEditor.vue', () => ({ default: { name: 'MonacoEditor', props: ['modelValue', 'options'], emits: ['update:modelValue','save'], template: '<textarea aria-label="正文" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)"></textarea>', methods: { focus() {} } } }));
vi.mock('@/components/Editor/MarkdownPreview.vue', () => ({ default: { props: ['content','active'], template: '<div class="preview-mock">{{ content }}</div>' } }));
vi.mock('@/components/WaterfallPanelComps/Graph.vue', () => ({ default: { template: '<div />' } }));
vi.mock('@/components/PostPanelComps/Post.vue', () => ({ default: { name: 'Post', props: ['previewMetadata', 'imageUrl', 'markdownUrl'], template: '<div class="post-card-mock">{{ previewMetadata.title }} {{ previewMetadata.pre }}</div>' } }));
import EditorPage from './EditorPage.vue';
let wrapper;
const file = { name: 'a.md', path: '/Posts/Markdowns/a.md', type: 'file' };
beforeEach(() => {
    vi.useFakeTimers();
    api.get.mockImplementation(url => Promise.resolve({ data: url === '/files/tree' ? { tree: [{ name: 'Markdowns', path: '/Posts/Markdowns', type: 'folder', children: [file] }] } : { content: '# Original', version: { etag: '1' } } }));
    api.post.mockResolvedValue({ data: { version: { etag: '2' } } });
    window.location.hash = '#/editor?token=test&api_port=18000';
});
afterEach(() => { wrapper?.unmount(); vi.useRealTimers(); vi.restoreAllMocks(); });
const openArticle = async () => {
    wrapper = mount(EditorPage, { attachTo: document.body });
    await flushPromises();
    wrapper.findComponent({ name: 'FileTreeSidebar' }).vm.$emit('file-select', file);
    await flushPromises();
};
describe('editor workspace', () => {
    it('starts with an actionable empty state', async () => {
        wrapper = mount(EditorPage);
        await flushPromises();
        expect(wrapper.text()).toContain('选择文章，开始写作');
        expect(wrapper.find('textarea').exists()).toBe(false);
    });
    it('opens a document and saves through the keyboard shortcut', async () => {
        await openArticle();
        await wrapper.get('textarea').setValue('# Changed');
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 's', ctrlKey: true, cancelable: true }));
        await flushPromises();
        expect(api.post).toHaveBeenCalledWith('/files/save', { path: 'Markdowns/a.md', content: '# Changed', expectedVersion: { etag: '1' } });
        expect(wrapper.text()).toContain('已与磁盘同步');
    });
    it('retains the editor after failed save on file switch', async () => {
        await openArticle();
        await wrapper.get('textarea').setValue('unsaved');
        api.post.mockRejectedValueOnce(new Error('offline'));
        wrapper.findComponent({ name: 'FileTreeSidebar' }).vm.$emit('file-select', { ...file, name: 'b.md', path: '/Posts/Markdowns/b.md' });
        await flushPromises();
        const buttons = wrapper.findAll('[role="dialog"] button');
        await buttons.find(button => button.text() === '保存并继续').trigger('click');
        await flushPromises();
        expect(wrapper.get('textarea').element.value).toBe('unsaved');
        expect(wrapper.text()).toContain('保存失败');
    });
    it('focus mode hides preview work and exits via Escape', async () => {
        await openArticle();
        await wrapper.findAll('button').find(button => button.text() === '专注').trigger('click');
        expect(wrapper.findComponent({ name: 'MarkdownPreview' }).props('active')).toBe(false);
        expect(wrapper.classes()).toContain('focus-mode');
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
        await wrapper.vm.$nextTick();
        expect(wrapper.classes()).not.toContain('focus-mode');
    });
    it('allows keyboard resizing and exposes the resulting width', async () => {
        await openArticle();
        const separator = wrapper.get('[role="separator"]');
        await separator.trigger('keydown', { key: 'ArrowRight' });
        expect(separator.attributes('aria-valuenow')).toBe('55');
        await separator.trigger('keydown', { key: 'Home' });
        expect(separator.attributes('aria-valuenow')).toBe('50');
    });
    it('shows the actual card component above the body and updates it from unsaved edits', async () => {
        await openArticle();
        const card = wrapper.findComponent({ name: 'Post' });
        const instance = card.vm;
        expect(wrapper.get('.post-preview-section').attributes('open')).toBeDefined();
        expect(card.props('markdownUrl')).toBe(file.path);
        expect(card.props('previewMetadata').title).toBe('a');
        await wrapper.get('textarea').setValue('---\ntitle: 草稿标题\npre: 首页卡片摘要\nimg: cover.png\ntags: [Vue]\ncategories: [技术]\n---\n正文');
        await vi.advanceTimersByTimeAsync(180);
        expect(card.vm).toBe(instance);
        expect(card.props('previewMetadata')).toMatchObject({ title: '草稿标题', pre: '首页卡片摘要', tags: ['Vue'], categories: ['技术'] });
        expect(card.props('imageUrl')).toBe('/Posts/Images/cover.png');
        expect(api.post).not.toHaveBeenCalled();
        expect(wrapper.find('.preview-mock').exists()).toBe(true);
    });
});
