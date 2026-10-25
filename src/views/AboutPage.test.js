import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import axios from 'axios';
import globalVar from '@/globalVar';
import AboutPage from './AboutPage.vue';

vi.mock('axios', () => ({ default: { get: vi.fn() } }));
vi.mock('./BaseLayout.vue', () => ({ default: { template: '<main><slot name="main" /></main>' } }));
vi.mock('@/components/MarkdownPanelComps/MarkdownRenender.js', () => ({ default: { render: body => `<p>${body}</p>` } }));
let wrapper;
const savedMarkdowns = globalVar.markdowns;
beforeEach(() => {
    axios.get.mockReset();
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(null);
});
afterEach(() => {
    wrapper?.unmount(); wrapper = null;
    globalVar.markdowns = savedMarkdowns;
    vi.restoreAllMocks(); vi.unstubAllGlobals();
});

describe('About page performance', () => {
    it('fetches only the indexed About article regardless of the total post count', async () => {
        globalVar.markdowns = Object.fromEntries(Array.from({ length: 1000 }, (_, i) => [`/${i}.md`, { title: `Post ${i}` }]));
        globalVar.markdowns['/about.md'] = { title: 'About' };
        axios.get.mockResolvedValue({ data: '---\ntitle: About\nname: Test Author\navatar: https://example.com/avatar.png\n---\nBiography' });
        wrapper = mount(AboutPage);
        await flushPromises();
        expect(axios.get).toHaveBeenCalledTimes(1);
        expect(axios.get).toHaveBeenCalledWith('/about.md', expect.objectContaining({ signal: expect.any(AbortSignal) }));
        expect(wrapper.find('.display-title').text()).toBe('Test Author');
        expect(wrapper.find('.avatar-image').attributes('src')).toBe('https://example.com/avatar.png');
    });

    it('uses default content without fetching posts when no About title is indexed', async () => {
        globalVar.markdowns = { '/post.md': { title: 'Post' } };
        wrapper = mount(AboutPage);
        await flushPromises();
        expect(axios.get).not.toHaveBeenCalled();
        expect(wrapper.find('.display-title').text()).toBe('Creative Developer');
    });

    it('aborts a pending load when leaving before the article arrives', async () => {
        globalVar.markdowns = { '/about.md': { title: 'About' } };
        let resolve;
        axios.get.mockReturnValue(new Promise(done => { resolve = done; }));
        const addListener = vi.spyOn(window, 'addEventListener');
        wrapper = mount(AboutPage);
        const signal = axios.get.mock.calls[0][1].signal;
        wrapper.unmount(); wrapper = null;
        expect(signal.aborted).toBe(true);
        resolve({ data: '---\ntitle: About\n---\nLate' });
        await flushPromises();
        expect(addListener.mock.calls.filter(([event]) => event === 'resize')).toHaveLength(0);
    });

    it('removes the canvas resize listener and cancels animation on unmount', async () => {
        globalVar.markdowns = {};
        vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({ clearRect: vi.fn() });
        vi.stubGlobal('requestAnimationFrame', vi.fn(() => 27));
        const cancel = vi.fn();
        vi.stubGlobal('cancelAnimationFrame', cancel);
        const add = vi.spyOn(window, 'addEventListener');
        const remove = vi.spyOn(window, 'removeEventListener');
        wrapper = mount(AboutPage);
        await flushPromises();
        const handler = add.mock.calls.find(([event]) => event === 'resize')[1];
        wrapper.unmount(); wrapper = null;
        expect(remove).toHaveBeenCalledWith('resize', handler);
        expect(cancel).toHaveBeenCalledWith(27);
    });
});
