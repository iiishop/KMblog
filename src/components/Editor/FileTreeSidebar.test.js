import { mount } from '@vue/test-utils';
import { afterEach, describe, expect, it } from 'vitest';
import FileTreeSidebar from './FileTreeSidebar.vue';
const article = { name: 'Hello.md', path: '/Posts/Markdowns/Notes/Hello.md', type: 'file' };
const files = [{ name: 'Markdowns', path: '/Posts/Markdowns', type: 'folder', children: [{ name: 'Notes', path: '/Posts/Markdowns/Notes', type: 'folder', children: [article, { name: 'cover.png', type: 'file', path: '/Posts/Markdowns/Notes/cover.png' }] }] }];
let wrapper;
afterEach(() => wrapper?.unmount());
const mountSidebar = (extra = {}) => wrapper = mount(FileTreeSidebar, { props: { files, visible: true, width: 250, ...extra }, global: { stubs: { FileTreeNode: true } } });
describe('file browser', () => {
    it('searches nested paths case-insensitively and opens the result via Enter', async () => {
        mountSidebar();
        await wrapper.get('input').setValue('NOTES hello');
        expect(wrapper.findAll('.search-result')).toHaveLength(1);
        await wrapper.get('input').trigger('keydown', { key: 'Enter' });
        expect(wrapper.emitted('file-select')[0]).toEqual([article]);
    });
    it('shows an empty search state and restores the tree via Escape', async () => {
        mountSidebar();
        await wrapper.get('input').setValue('missing');
        expect(wrapper.text()).toContain('0 篇匹配文章');
        await wrapper.get('input').trigger('keydown', { key: 'Escape' });
        expect(wrapper.get('.file-tree').isVisible()).toBe(true);
    });
    it('closes explicitly and keeps collapsed controls out of keyboard navigation', async () => {
        mountSidebar();
        await wrapper.get('[aria-label="关闭文件浏览器"]').trigger('click');
        expect(wrapper.emitted('update:visible')[0]).toEqual([false]);
        await wrapper.setProps({ visible: false });
        expect(wrapper.attributes('inert')).toBeDefined();
    });
});
