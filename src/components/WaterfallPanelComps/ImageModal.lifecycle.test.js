import { afterEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { renderDynamicComponents, unmountDynamicComponents } from '../MarkdownPanelComps/DynamicComponentRenderer';
import ImageModal from './ImageModal.vue';

vi.mock('../MarkdownPanelComps/MarkdownRenender.js', () => ({ default: { render: body => `<p>${body}</p>` } }));
vi.mock('../MarkdownPanelComps/DynamicComponentRenderer.js', () => ({
    renderDynamicComponents: vi.fn(), unmountDynamicComponents: vi.fn()
}));
let wrapper;
afterEach(() => { wrapper?.unmount(); vi.unstubAllGlobals(); });
const create = (props = {}) => mount(ImageModal, {
    props: { image: { src: '/test.jpg', title: 'Test' }, ...props },
    global: { stubs: { UtterancesComments: true, Teleport: true } }
});

describe('gallery description lifecycle', () => {
    it('mounts an initial description and cleans it up when replaced or closed', async () => {
        wrapper = create({ description: 'Initial' });
        await flushPromises();
        expect(renderDynamicComponents).toHaveBeenCalledTimes(1);
        const container = wrapper.find('.description-content').element;
        await wrapper.setProps({ description: 'Updated' });
        await flushPromises();
        expect(unmountDynamicComponents).toHaveBeenCalledWith(container);
        expect(wrapper.find('.description-content').text()).toBe('Updated');
        const updatedContainer = wrapper.find('.description-content').element;
        unmountDynamicComponents.mockClear();
        wrapper.unmount();
        wrapper = null;
        expect(unmountDynamicComponents).toHaveBeenCalledWith(updatedContainer);
    });

    it('only fetches an associated description once on mount', async () => {
        const fetchMock = vi.fn().mockResolvedValue({ ok: false });
        vi.stubGlobal('fetch', fetchMock);
        wrapper = create({ image: { src: '/test.jpg', title: 'Test', mdPath: '/description.md' } });
        await flushPromises();
        expect(fetchMock).toHaveBeenCalledTimes(1);
    });
});
