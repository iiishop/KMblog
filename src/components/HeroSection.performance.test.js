import { mount } from '@vue/test-utils';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import HeroSection from './HeroSection.vue';

vi.mock('@/composables/useTheme', () => ({ themeManager: { currentTheme: { value: 'day' } } }));

let wrapper, visibilityChanged, frames, nextFrame, drawing;
const tick = () => {
    const pending = [...frames.values()];
    frames.clear();
    pending.forEach(callback => callback(0));
};
beforeEach(() => {
    vi.useFakeTimers();
    frames = new Map();
    nextFrame = 0;
    vi.stubGlobal('requestAnimationFrame', callback => { frames.set(++nextFrame, callback); return nextFrame; });
    vi.stubGlobal('cancelAnimationFrame', id => frames.delete(id));
    vi.stubGlobal('IntersectionObserver', class {
        constructor(callback) { visibilityChanged = callback; }
        observe() {}
        disconnect() {}
    });
    vi.spyOn(document, 'hidden', 'get').mockReturnValue(false);
    drawing = { clearRect: vi.fn(), beginPath() {}, arc() {}, fill() {} };
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(drawing);
    wrapper = mount(HeroSection, { global: { stubs: { TypewriterText: true } } });
    tick();
});
afterEach(() => {
    wrapper.unmount();
    vi.useRealTimers();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
});

describe('hero background work', () => {
    it('pauses particles only when offscreen and resumes them when visible', () => {
        vi.advanceTimersByTime(300);
        tick();
        expect(drawing.clearRect).toHaveBeenCalledTimes(1);
        visibilityChanged([{ isIntersecting: false }]);
        tick();
        expect(drawing.clearRect).toHaveBeenCalledTimes(1);
        visibilityChanged([{ isIntersecting: true }]);
        tick();
        expect(drawing.clearRect).toHaveBeenCalledTimes(2);
    });

    it('releases animation callbacks when leaving before delayed startup', () => {
        wrapper.unmount();
        vi.advanceTimersByTime(1500);
        expect(frames.size).toBe(0);
    });
});
