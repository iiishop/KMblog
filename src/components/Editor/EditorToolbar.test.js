import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import EditorToolbar from './EditorToolbar.vue';

describe('EditorToolbar', () => {
    let wrapper;

    beforeEach(() => {
        wrapper = mount(EditorToolbar, {
            props: {
                saveStatus: 'saved',
                fileName: 'test.md'
            }
        });
    });

    it('renders correctly', () => {
        expect(wrapper.exists()).toBe(true);
        expect(wrapper.find('.editor-toolbar').exists()).toBe(true);
    });

    it('displays file name', () => {
        expect(wrapper.find('.file-name').text()).toBe('test.md');
    });

    it('displays default text when no file name', async () => {
        await wrapper.setProps({ fileName: '' });
        expect(wrapper.find('.file-name').text()).toBe('未选择文件');
    });

    it('displays save status correctly', async () => {
        // Test saved status
        expect(wrapper.find('.save-status').text()).toBe('已保存');
        expect(wrapper.find('.status-saved').exists()).toBe(true);

        // Test saving status
        await wrapper.setProps({ saveStatus: 'saving' });
        expect(wrapper.find('.save-status').text()).toBe('保存中...');
        expect(wrapper.find('.status-saving').exists()).toBe(true);

        // Test unsaved status
        await wrapper.setProps({ saveStatus: 'unsaved' });
        expect(wrapper.find('.save-status').text()).toBe('未保存');
        expect(wrapper.find('.status-unsaved').exists()).toBe(true);
    });

    it('emits save event when save button clicked', async () => {
        await wrapper.setProps({ saveStatus: 'unsaved' }); // Set to unsaved so button is enabled
        const saveBtn = wrapper.find('.save-btn');
        await saveBtn.trigger('click');
        expect(wrapper.emitted('save')).toBeTruthy();
        expect(wrapper.emitted('save').length).toBe(1);
    });

    it('disables save button when status is saved', async () => {
        await wrapper.setProps({ saveStatus: 'saved' });
        const saveBtn = wrapper.find('.save-btn');
        expect(saveBtn.attributes('disabled')).toBeDefined();
    });

    it('enables save button when status is unsaved', async () => {
        await wrapper.setProps({ saveStatus: 'unsaved' });
        const saveBtn = wrapper.find('.save-btn');
        expect(saveBtn.attributes('disabled')).toBeUndefined();
    });

    it('renders all format buttons', () => {
        const formatButtons = wrapper.findAll('.format-btn');
        expect(formatButtons.length).toBeGreaterThanOrEqual(6); // Bold, Italic, Heading, Link, Image, Code
    });

    it('emits insert-format event when format button clicked', async () => {
        const formatButtons = wrapper.findAll('.format-btn');
        await formatButtons[0].trigger('click'); // Click first format button
        expect(wrapper.emitted('insert-format')).toBeTruthy();
    });

    it('renders block insertion dropdown', () => {
        expect(wrapper.find('.dropdown').exists()).toBe(true);
        expect(wrapper.find('.dropdown-btn').exists()).toBe(true);
    });

    it('toggles dropdown menu when dropdown button clicked', async () => {
        const dropdownBtn = wrapper.find('.dropdown-btn');

        // Initially hidden
        expect(wrapper.find('.dropdown-menu').exists()).toBe(false);

        // Click to show
        await dropdownBtn.trigger('click');
        expect(wrapper.find('.dropdown-menu').exists()).toBe(true);

        // Click again to hide
        await dropdownBtn.trigger('click');
        expect(wrapper.find('.dropdown-menu').exists()).toBe(false);
    });

    it('displays all block options in dropdown', async () => {
        const dropdownBtn = wrapper.find('.dropdown-btn');
        await dropdownBtn.trigger('click');

        const dropdownItems = wrapper.findAll('.dropdown-item');
        expect(dropdownItems.length).toBe(6); // bilibili, steam, bangumi, github, xiaohongshu, mermaid
    });

    it('emits insert-block event when block option clicked', async () => {
        const dropdownBtn = wrapper.find('.dropdown-btn');
        await dropdownBtn.trigger('click');

        const firstItem = wrapper.find('.dropdown-item');
        await firstItem.trigger('click');

        expect(wrapper.emitted('insert-block')).toBeTruthy();
        expect(wrapper.emitted('insert-block').length).toBe(1);
    });

    it('closes dropdown after selecting a block', async () => {
        const dropdownBtn = wrapper.find('.dropdown-btn');
        await dropdownBtn.trigger('click');
        expect(wrapper.find('.dropdown-menu').exists()).toBe(true);

        const firstItem = wrapper.find('.dropdown-item');
        await firstItem.trigger('click');

        expect(wrapper.find('.dropdown-menu').exists()).toBe(false);
    });

    it('emits toggle-file-tree event when file tree button clicked', async () => {
        const fileTreeBtn = wrapper.findAll('.toolbar-btn')[0]; // First button is file tree toggle
        await fileTreeBtn.trigger('click');
        expect(wrapper.emitted('toggle-file-tree')).toBeTruthy();
    });
});
