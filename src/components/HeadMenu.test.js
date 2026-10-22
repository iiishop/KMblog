import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import HeadMenu from './HeadMenu.vue';

vi.mock('@/composables/useTheme', async () => {
    const { ref } = await import('vue');
    return { themeManager: { currentMode: ref('light'), toggleTheme: vi.fn() } };
});
let wrapper;
let frames;
beforeEach(() => {
    frames = new Map();
    let nextFrame = 0;
    vi.stubGlobal('requestAnimationFrame', vi.fn(callback => { frames.set(++nextFrame, callback); return nextFrame; }));
    vi.stubGlobal('cancelAnimationFrame', vi.fn(id => frames.delete(id)));
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(null);
    wrapper = mount(HeadMenu, { global: { stubs: { RouterLink: true } } });
});
afterEach(() => { wrapper?.unmount(); wrapper = null; vi.restoreAllMocks(); vi.unstubAllGlobals(); });

describe('header animation scheduling', () => {
    it('reads the captured element after a native mouse event has finished dispatching', async () => {
        const header = wrapper.find('header').element;
        vi.spyOn(header, 'getBoundingClientRect').mockReturnValue({ left: 10, top: 20, width: 100, height: 50 });
        const event = new MouseEvent('mousemove', { clientX: 60, clientY: 45, bubbles: true });
        header.dispatchEvent(event);
        expect(event.currentTarget).toBeNull();
        expect(frames.size).toBe(1);
        const callback = [...frames.values()][0];
        frames.clear();
        expect(() => callback()).not.toThrow();
        await wrapper.vm.$nextTick();
        expect(header.style.getPropertyValue('--mouse-x')).toBe('0.5');
        expect(header.style.getPropertyValue('--mouse-y')).toBe('0.5');
    });

    it('cancels queued mouse and scroll frames on unmount', async () => {
        await wrapper.find('header').trigger('mousemove');
        window.dispatchEvent(new Event('scroll'));
        expect(frames.size).toBe(2);
        wrapper.unmount(); wrapper = null;
        expect(frames.size).toBe(0);
    });

    it('keeps scroll progress finite on a page without scrollable height', async () => {
        vi.spyOn(document.documentElement, 'scrollHeight', 'get').mockReturnValue(window.innerHeight);
        window.dispatchEvent(new Event('scroll'));
        [...frames.values()].forEach(callback => callback());
        frames.clear();
        await wrapper.vm.$nextTick();
        expect(wrapper.find('.scroll-progress').attributes('style')).toContain('scaleX(0)');
    });
});
