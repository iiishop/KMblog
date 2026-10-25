import { mount, flushPromises } from '@vue/test-utils';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import BaseLayout from './BaseLayout.vue';

vi.mock('@/config', () => ({ default: {
    InfoListUp: [], InfoListDown: [], InfoListFloat: [], TipListUp: [], TipListDown: [], TipListFloat: [],
    MainListUp: [], MainListDown: []
} }));
vi.mock('vue-router', () => ({ useRoute: () => ({ name: 'Home' }) }));
vi.mock('@/composables/useTheme', () => ({ themeManager: { currentTheme: { value: 'day' } } }));

let wrapper, observers;
beforeEach(async () => {
    observers = [];
    vi.stubGlobal('ResizeObserver', class {
        constructor(callback) { this.callback = callback; observers.push(this); }
        observe = vi.fn();
        disconnect = vi.fn();
    });
    vi.stubGlobal('requestAnimationFrame', vi.fn(() => 1));
    vi.stubGlobal('cancelAnimationFrame', vi.fn());
    document.documentElement.style.setProperty('--header-height', '123px');
    wrapper = mount(BaseLayout, { attachTo: document.body, global: { stubs: {
        HeadMenu: { template: '<header class="header-menu"></header>' }
    } } });
    await flushPromises();
});
afterEach(() => {
    wrapper.unmount();
    document.documentElement.style.removeProperty('--header-height');
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
});

it('updates only Scene spacing from the observed border box, without a forced header measurement', () => {
    const header = wrapper.get('.header-menu').element;
    const measured = vi.spyOn(header, 'offsetHeight', 'get').mockReturnValue(999);
    const observer = observers.find(o => o.observe.mock.calls.some(([element]) => element === header));
    observer.callback([{ borderBoxSize: [{ blockSize: 72.4 }] }]);
    expect(wrapper.get('.Scene').element.style.paddingTop).toBe('88px');
    expect(document.documentElement.style.getPropertyValue('--header-height')).toBe('123px');
    expect(measured).not.toHaveBeenCalled();
    observer.callback([{ borderBoxSize: [{ blockSize: 65.6 }] }]);
    expect(wrapper.get('.Scene').element.style.paddingTop).toBe('82px');
});
