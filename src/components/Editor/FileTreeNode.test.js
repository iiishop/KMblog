import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import FileTreeNode from './FileTreeNode.vue';

describe('FileTreeNode', () => {
    const mockFileNode = {
        name: 'test.md',
        type: 'file',
        path: '/Posts/Markdowns/test.md'
    };

    const mockFolderNode = {
        name: 'Markdowns',
        type: 'folder',
        path: '/Posts/Markdowns',
        children: [
            {
                name: 'test.md',
                type: 'file',
                path: '/Posts/Markdowns/test.md'
            }
        ]
    };

    it('renders file node correctly', () => {
        const wrapper = mount(FileTreeNode, {
            props: {
                node: mockFileNode,
                currentFile: null
            }
        });

        expect(wrapper.find('.node-name').text()).toBe('test.md');
        expect(wrapper.find('.file-icon').exists()).toBe(true);
    });

    it('renders folder node correctly', () => {
        const wrapper = mount(FileTreeNode, {
            props: {
                node: mockFolderNode,
                currentFile: null
            }
        });

        expect(wrapper.find('.node-name').text()).toBe('Markdowns');
        expect(wrapper.find('.folder-icon').exists()).toBe(true);
    });

    it('highlights current file', () => {
        const wrapper = mount(FileTreeNode, {
            props: {
                node: mockFileNode,
                currentFile: mockFileNode
            }
        });

        expect(wrapper.find('.node-content').classes()).toContain('is-current');
    });

    it('emits select event when file is clicked', async () => {
        const wrapper = mount(FileTreeNode, {
            props: {
                node: mockFileNode,
                currentFile: null
            }
        });

        await wrapper.find('.node-content').trigger('click');
        expect(wrapper.emitted('select')).toBeTruthy();
        expect(wrapper.emitted('select')[0]).toEqual([mockFileNode]);
    });

    it('toggles folder expansion when clicked', async () => {
        const wrapper = mount(FileTreeNode, {
            props: {
                node: mockFolderNode,
                currentFile: null
            },
            global: {
                stubs: {
                    FileTreeNode: true
                }
            }
        });

        // Initially not expanded
        expect(wrapper.find('.node-children').exists()).toBe(false);

        // Click to expand
        await wrapper.find('.node-content').trigger('click');
        await wrapper.vm.$nextTick();

        // Should be expanded
        expect(wrapper.vm.isExpanded).toBe(true);
    });

    it('shows context menu on right click', async () => {
        const wrapper = mount(FileTreeNode, {
            props: {
                node: mockFileNode,
                currentFile: null
            }
        });

        await wrapper.find('.node-content').trigger('contextmenu');
        await wrapper.vm.$nextTick();

        expect(wrapper.vm.showContextMenu).toBe(true);
    });

    it('file node is draggable', () => {
        const wrapper = mount(FileTreeNode, {
            props: {
                node: mockFileNode,
                currentFile: null
            }
        });

        expect(wrapper.find('.node-content').attributes('draggable')).toBe('true');
    });

    it('folder node is not draggable', () => {
        const wrapper = mount(FileTreeNode, {
            props: {
                node: mockFolderNode,
                currentFile: null
            },
            global: {
                stubs: {
                    FileTreeNode: true
                }
            }
        });

        expect(wrapper.find('.node-content').attributes('draggable')).toBe('false');
    });
});
