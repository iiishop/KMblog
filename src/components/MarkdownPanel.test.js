import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import axios from 'axios';
import { renderDynamicComponents, unmountDynamicComponents } from './MarkdownPanelComps/DynamicComponentRenderer';

vi.mock('axios', () => ({ default: { get: vi.fn(), isCancel: vi.fn(() => false) } }));
vi.mock('./MarkdownPanelComps/MarkdownRenender.js', () => ({ default: { render: (body) => `<p>${body}</p>` } }));
vi.mock('./MarkdownPanelComps/DynamicComponentRenderer.js', () => ({
    renderDynamicComponents: vi.fn(), unmountDynamicComponents: vi.fn()
}));
vi.mock('mermaid', () => ({ default: { mermaidAPI: { reset: vi.fn() }, run: vi.fn() } }));
import MarkdownPanel from './MarkdownPanel.vue';

const article = (title) => `---\ntitle: ${title}\ndate: 2026-01-01\n---\n${title}`;
const deferred = () => {
    let resolve;
    const promise = new Promise(r => { resolve = r; });
    return { promise, resolve };
};
let wrapper;
const create = (props = {}) => mount(MarkdownPanel, {
    props: { markdownUrl: '/first.md', ...props },
    global: { stubs: { ImageViewer: true, UtterancesComments: true, RouterLink: true } }
});

describe('Markdown article lifecycle', () => {
    beforeEach(() => { axios.get.mockReset(); });
    afterEach(() => { wrapper?.unmount(); wrapper = null; });

    it('requests and renders the initial article only once', async () => {
        axios.get.mockResolvedValue({ data: article('First') });
        wrapper = create();
        await flushPromises();
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(renderDynamicComponents).toHaveBeenCalledTimes(1);
        expect(wrapper.find('.post-content').text()).toBe('First');
    });

    it('cancels old requests and ignores a late response after navigating', async () => {
        const first = deferred();
        const second = deferred();
        axios.get.mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise);
        wrapper = create();
        const signal = axios.get.mock.calls[0][1].signal;
        await wrapper.setProps({ markdownUrl: '/second.md' });
        expect(signal.aborted).toBe(true);
        second.resolve({ data: article('Second') });
        await flushPromises();
        first.resolve({ data: article('First') });
        await flushPromises();
        expect(wrapper.find('.post-content').text()).toBe('Second');
        expect(renderDynamicComponents).toHaveBeenCalledTimes(1);
    });

    it('cancels loading and releases embedded apps before unmount', async () => {
        const pending = deferred();
        axios.get.mockReturnValue(pending.promise);
        wrapper = create();
        const signal = axios.get.mock.calls[0][1].signal;
        const container = wrapper.find('.post-content').element;
        wrapper.unmount();
        wrapper = null;
        expect(signal.aborted).toBe(true);
        expect(unmountDynamicComponents).toHaveBeenCalledWith(container);
        pending.resolve({ data: article('Late') });
        await flushPromises();
        expect(renderDynamicComponents).not.toHaveBeenCalled();
    });

    it('accepts an empty decrypted article without fetching its encrypted source', async () => {
        wrapper = create({ decryptedContent: '' });
        await flushPromises();
        expect(axios.get).not.toHaveBeenCalled();
    });
});
