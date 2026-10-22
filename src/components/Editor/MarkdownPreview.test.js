import { mount, flushPromises } from '@vue/test-utils';
import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
const mocks = vi.hoisted(() => ({ render: vi.fn(text => `<p>${text}</p>`), mount: vi.fn(), unmount: vi.fn(), charts: vi.fn().mockResolvedValue(undefined) }));
vi.mock('@/components/MarkdownPanelComps/MarkdownRenender.js', () => ({ default: { render: mocks.render } }));
vi.mock('@/components/MarkdownPanelComps/DynamicComponentRenderer.js', () => ({ renderDynamicComponents: mocks.mount, unmountDynamicComponents: mocks.unmount }));
vi.mock('@/components/UtterancesComments.vue', () => ({ default: { template: '<div />' } }));
vi.mock('mermaid', () => ({ default: { run: mocks.charts } }));
import MarkdownPreview from './MarkdownPreview.vue';
let wrapper;
beforeEach(() => { vi.useFakeTimers(); });
afterEach(() => { wrapper?.unmount(); vi.useRealTimers(); });
describe('live preview scheduling', () => {
    it('renders once for a typing burst and skips front matter', async () => {
        wrapper = mount(MarkdownPreview, { props: { content: 'first' } });
        await wrapper.setProps({ content: 'second' });
        await wrapper.setProps({ content: '---\ntitle: Draft\n---\nlatest' });
        await vi.advanceTimersByTimeAsync(180);
        expect(mocks.render).toHaveBeenCalledTimes(1);
        expect(wrapper.get('article').text()).toBe('latest');
        expect(wrapper.get('.post-title').text()).toBe('Draft');
        expect(mocks.charts).not.toHaveBeenCalled();
    });
    it('suspends hidden previews and resumes with the latest content', async () => {
        wrapper = mount(MarkdownPreview, { props: { content: 'old', active: false } });
        await wrapper.setProps({ content: 'new' });
        await vi.advanceTimersByTimeAsync(500);
        expect(mocks.render).not.toHaveBeenCalled();
        await wrapper.setProps({ active: true });
        await vi.advanceTimersByTimeAsync(180);
        expect(wrapper.get('article').text()).toBe('new');
    });
    it('retains the last valid preview while YAML is incomplete', async () => {
        wrapper = mount(MarkdownPreview, { props: { content: 'valid' } });
        await vi.advanceTimersByTimeAsync(180);
        await wrapper.setProps({ content: '---\ntitle: [broken\n---\nbody' });
        await vi.advanceTimersByTimeAsync(180);
        expect(wrapper.get('article').text()).toBe('valid');
        expect(wrapper.get('[role="status"]').text()).toContain('检查文章头部格式');
    });
    it('unmounts embedded apps and cancels pending work on disposal', async () => {
        wrapper = mount(MarkdownPreview, { props: { content: 'draft' } });
        await vi.advanceTimersByTimeAsync(180);
        await wrapper.setProps({ content: 'pending' });
        mocks.render.mockClear();
        wrapper.unmount();
        await vi.advanceTimersByTimeAsync(500);
        await flushPromises();
        expect(mocks.render).not.toHaveBeenCalled();
        expect(mocks.unmount).toHaveBeenCalled();
    });
});
