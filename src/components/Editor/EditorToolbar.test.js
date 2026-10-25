import { mount } from '@vue/test-utils';
import { ref } from 'vue';
import { afterEach, describe, expect, it, vi } from 'vitest';
vi.mock('@/composables/useTheme', () => ({ useTheme: () => ({ isDarkMode: ref(false), currentMode: ref('light'), toggleTheme: vi.fn() }) }));
import EditorToolbar from './EditorToolbar.vue';
let wrapper;
afterEach(() => wrapper?.unmount());
describe('editor toolbar', () => {
    it('retries failed saves and clearly labels conflicts', async () => {
        wrapper = mount(EditorToolbar, { props: { saveStatus: 'error' } });
        expect(wrapper.text()).toContain('保存失败');
        await wrapper.get('.save-btn').trigger('click');
        expect(wrapper.emitted('save')).toHaveLength(1);
        await wrapper.setProps({ saveStatus: 'conflict' });
        expect(wrapper.text()).toContain('版本冲突');
        expect(wrapper.get('.save-btn').element.disabled).toBe(true);
    });
    it('disables saving when a file is opening or a draft choice is pending', () => {
        wrapper = mount(EditorToolbar, { props: { saveStatus: 'unsaved', disabled: true } });
        expect(wrapper.get('.save-btn').element.disabled).toBe(true);
    });
    it('exposes a compact formatting disclosure for small screens', async () => {
        wrapper = mount(EditorToolbar);
        const toggle = wrapper.get('.mobile-tools-toggle');
        expect(toggle.attributes('aria-expanded')).toBe('false');
        await toggle.trigger('click');
        expect(toggle.attributes('aria-expanded')).toBe('true');
    });
});
