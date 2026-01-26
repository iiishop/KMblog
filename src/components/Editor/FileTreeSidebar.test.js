import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import FileTreeSidebar from './FileTreeSidebar.vue';
import FileTreeNode from './FileTreeNode.vue';

describe('FileTreeSidebar', () => {
    const mockFiles = [
        {
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
        }
    ];

    it('renders file tree sidebar', () => {
        const wrapper = mount(FileTreeSidebar, {
            props: {
                visible: true,
                width: 250,
                files: mockFiles,
                currentFile: null
            },
            global: {
                stubs: {
                    FileTreeNode: true
                }
            }
        });

        expect(wrapper.find('.file-tree-sidebar').exists()).toBe(true);
        expect(wrapper.find('.sidebar-header h3').text()).toBe('文件');
    });

    it('hides sidebar when visible is false', () => {
        const wrapper = mount(FileTreeSidebar, {
            props: {
                visible: false,
                width: 250,
                files: mockFiles,
                currentFile: null
            },
            global: {
                stubs: {
                    FileTreeNode: true
                }
            }
        });

        expect(wrapper.find('.file-tree-sidebar').classes()).toContain('collapsed');
    });

    it('emits update:visible when close button clicked', async () => {
        const wrapper = mount(FileTreeSidebar, {
            props: {
                visible: true,
                width: 250,
                files: mockFiles,
                currentFile: null
            },
            global: {
                stubs: {
                    FileTreeNode: true
                }
            }
        });

        await wrapper.find('.close-btn').trigger('click');
        expect(wrapper.emitted('update:visible')).toBeTruthy();
        expect(wrapper.emitted('update:visible')[0]).toEqual([false]);
    });

    it('renders FileTreeNode components for each file', () => {
        const wrapper = mount(FileTreeSidebar, {
            props: {
                visible: true,
                width: 250,
                files: mockFiles,
                currentFile: null
            },
            global: {
                components: {
                    FileTreeNode
                }
            }
        });

        const nodes = wrapper.findAllComponents(FileTreeNode);
        expect(nodes.length).toBe(mockFiles.length);
    });

    it('applies correct width style', () => {
        const wrapper = mount(FileTreeSidebar, {
            props: {
                visible: true,
                width: 300,
                files: mockFiles,
                currentFile: null
            },
            global: {
                stubs: {
                    FileTreeNode: true
                }
            }
        });

        expect(wrapper.find('.file-tree-sidebar').attributes('style')).toContain('300px');
    });
});
