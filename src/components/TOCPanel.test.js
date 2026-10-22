import { afterEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import TOCPanel from './TOCPanel.vue';

let wrapper;
afterEach(() => {
    wrapper?.unmount(); wrapper = null;
    document.body.innerHTML = '';
    vi.useRealTimers(); vi.unstubAllGlobals();
});

describe('table of contents lifecycle', () => {
    it('stops polling for an article when unmounted while the article is still loading', () => {
        vi.useFakeTimers();
        wrapper = mount(TOCPanel);
        expect(vi.getTimerCount()).toBe(1);
        wrapper.unmount(); wrapper = null;
        expect(vi.getTimerCount()).toBe(0);
        vi.advanceTimersByTime(2000);
        expect(vi.getTimerCount()).toBe(0);
    });

    it('still displays clickable headings without IntersectionObserver', async () => {
        vi.stubGlobal('IntersectionObserver', undefined);
        document.body.innerHTML = '<article class="post-content markdown"><h2>Heading</h2></article>';
        const scroll = vi.fn();
        vi.stubGlobal('scrollTo', scroll);
        wrapper = mount(TOCPanel);
        await wrapper.vm.$nextTick();
        expect(wrapper.find('.toc-link').text()).toBe('Heading');
        await wrapper.find('.toc-link').trigger('click');
        expect(scroll).toHaveBeenCalled();
    });

    it('coalesces content mutations into one frame and cancels it on unmount', async () => {
        vi.stubGlobal('IntersectionObserver', undefined);
        const raf = vi.fn(() => 42);
        const cancel = vi.fn();
        vi.stubGlobal('requestAnimationFrame', raf);
        vi.stubGlobal('cancelAnimationFrame', cancel);
        document.body.innerHTML = '<article class="post-content markdown"><h2>One</h2></article>';
        wrapper = mount(TOCPanel);
        const container = document.querySelector('article');
        container.appendChild(document.createElement('p'));
        await Promise.resolve();
        container.appendChild(document.createElement('p'));
        await Promise.resolve();
        expect(raf).toHaveBeenCalledTimes(1);
        wrapper.unmount(); wrapper = null;
        expect(cancel).toHaveBeenCalledWith(42);
    });
});
