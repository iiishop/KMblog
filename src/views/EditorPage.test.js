import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import axios from 'axios';

// Mock mermaid before importing components
vi.mock('mermaid', () => ({
    default: {
        initialize: vi.fn(),
        mermaidAPI: {
            reset: vi.fn()
        },
        run: vi.fn()
    }
}));

// Mock axios
vi.mock('axios', () => {
    const mockAxios = {
        defaults: {
            headers: {
                common: {}
            }
        },
        get: vi.fn(),
        post: vi.fn(),
        delete: vi.fn(),
        CancelToken: {
            source: vi.fn(() => ({
                token: 'mock-token',
                cancel: vi.fn()
            }))
        },
        isCancel: vi.fn((error) => error && error.name === 'CanceledError')
    };
    return {
        default: mockAxios
    };
});

// Mock MonacoEditor component
vi.mock('@/components/Editor/MonacoEditor.vue', () => ({
    default: {
        name: 'MonacoEditor',
        template: '<div class="monaco-editor-mock"></div>',
        props: ['modelValue', 'language', 'theme'],
        emits: ['update:modelValue', 'change', 'scroll']
    }
}));

import EditorPage from './EditorPage.vue';

describe('EditorPage', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Mock URL hash params
        delete window.location;
        window.location = {
            hash: '#/editor?token=test-token&api_port=8000'
        };

        // Reset axios mocks
        axios.get.mockReset();
        axios.post.mockReset();
        axios.delete.mockReset();
    });

    it('renders the editor page with all main components', () => {
        const wrapper = mount(EditorPage, {
            global: {
                stubs: {
                    MonacoEditor: true
                }
            }
        });

        // Check main structure
        expect(wrapper.find('.editor-container').exists()).toBe(true);
        expect(wrapper.find('.file-tree-sidebar').exists()).toBe(true);
        expect(wrapper.find('.main-editor').exists()).toBe(true);
        expect(wrapper.find('.editor-toolbar').exists()).toBe(true);
        expect(wrapper.find('.editor-panels').exists()).toBe(true);
    });

    it('renders MarkdownPreview component', () => {
        const wrapper = mount(EditorPage, {
            global: {
                stubs: {
                    MonacoEditor: true
                }
            }
        });

        // Check that preview panel exists
        expect(wrapper.find('.preview-panel').exists()).toBe(true);

        // Check that MarkdownPreview component is rendered
        const previewComponent = wrapper.findComponent({ name: 'MarkdownPreview' });
        expect(previewComponent.exists()).toBe(true);
    });

    it('passes content to MarkdownPreview', async () => {
        const wrapper = mount(EditorPage, {
            global: {
                stubs: {
                    MonacoEditor: true
                }
            }
        });

        // Set content
        await wrapper.vm.$nextTick();
        wrapper.vm.content = '# Test Content';
        await wrapper.vm.$nextTick();

        // Check that MarkdownPreview receives the content
        const previewComponent = wrapper.findComponent({ name: 'MarkdownPreview' });
        expect(previewComponent.props('content')).toBe('# Test Content');
    });

    it('passes scroll sync to MarkdownPreview', async () => {
        const wrapper = mount(EditorPage, {
            global: {
                stubs: {
                    MonacoEditor: true
                }
            }
        });

        // Trigger scroll
        wrapper.vm.handleEditorScroll(0.5);
        await wrapper.vm.$nextTick();

        // Check that MarkdownPreview receives the scroll position
        const previewComponent = wrapper.findComponent({ name: 'MarkdownPreview' });
        expect(previewComponent.props('scrollSync')).toBe(0.5);
    });

    it('toggles file tree visibility', async () => {
        const wrapper = mount(EditorPage, {
            global: {
                stubs: {
                    MonacoEditor: true
                }
            }
        });

        // Initially visible
        expect(wrapper.find('.file-tree-sidebar').exists()).toBe(true);

        // Toggle visibility
        wrapper.vm.fileTreeVisible = false;
        await wrapper.vm.$nextTick();

        // Should be hidden
        expect(wrapper.find('.file-tree-sidebar').exists()).toBe(false);
    });

    it('updates save status on content change', async () => {
        const wrapper = mount(EditorPage, {
            global: {
                stubs: {
                    MonacoEditor: true
                }
            }
        });

        // Initially saved
        expect(wrapper.vm.saveStatus).toBe('saved');

        // Change content
        wrapper.vm.handleContentChange();
        await wrapper.vm.$nextTick();

        // Should be unsaved
        expect(wrapper.vm.saveStatus).toBe('unsaved');
    });

    describe('Error Handling', () => {
        it('handles network errors gracefully', async () => {
            // Mock network error
            axios.get.mockRejectedValueOnce({
                request: {},
                message: 'Network Error'
            });

            const wrapper = mount(EditorPage, {
                global: {
                    stubs: {
                        MonacoEditor: true
                    }
                }
            });

            // Mock alert
            const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => { });

            // Try to load file tree
            await wrapper.vm.loadFileTree();

            // Should show error message
            expect(alertSpy).toHaveBeenCalled();
            expect(alertSpy.mock.calls[0][0]).toContain('无法连接到服务器');

            alertSpy.mockRestore();
        });

        it('handles 404 errors with appropriate message', async () => {
            // Mock 404 error
            axios.get.mockRejectedValueOnce({
                response: {
                    status: 404,
                    data: {
                        detail: 'File not found'
                    }
                }
            });

            const wrapper = mount(EditorPage, {
                global: {
                    stubs: {
                        MonacoEditor: true
                    }
                }
            });

            // Mock alert
            const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => { });

            // Try to load file tree
            await wrapper.vm.loadFileTree();

            // Should show 404 error message
            expect(alertSpy).toHaveBeenCalled();
            expect(alertSpy.mock.calls[0][0]).toContain('文件不存在');

            alertSpy.mockRestore();
        });

        it('handles 500 errors with appropriate message', async () => {
            // Mock 500 error
            axios.get.mockRejectedValueOnce({
                response: {
                    status: 500,
                    data: {
                        detail: 'Internal server error'
                    }
                }
            });

            const wrapper = mount(EditorPage, {
                global: {
                    stubs: {
                        MonacoEditor: true
                    }
                }
            });

            // Mock alert
            const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => { });

            // Try to load file tree
            await wrapper.vm.loadFileTree();

            // Should show server error message
            expect(alertSpy).toHaveBeenCalled();
            expect(alertSpy.mock.calls[0][0]).toContain('服务器错误');

            alertSpy.mockRestore();
        });

        it('silently ignores cancelled requests', async () => {
            // Mock axios.get to return a resolved promise first (for initial mount)
            axios.get.mockResolvedValueOnce({
                data: { tree: [] }
            });

            const wrapper = mount(EditorPage, {
                global: {
                    stubs: {
                        MonacoEditor: true
                    }
                }
            });

            // Wait for initial mount to complete
            await wrapper.vm.$nextTick();

            // Now mock cancelled error for the next call
            const cancelError = new Error('Request cancelled');
            cancelError.name = 'CanceledError';
            axios.isCancel.mockReturnValueOnce(true);
            axios.get.mockRejectedValueOnce(cancelError);

            // Mock alert
            const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => { });

            // Try to load file tree again
            await wrapper.vm.loadFileTree();

            // Should NOT show error message for cancelled requests
            expect(alertSpy).not.toHaveBeenCalled();

            alertSpy.mockRestore();
        });
    });

    describe('Version Conflict Handling', () => {
        it('detects version conflicts and prompts user', async () => {
            const wrapper = mount(EditorPage, {
                global: {
                    stubs: {
                        MonacoEditor: true
                    }
                }
            });

            // Set up current file
            wrapper.vm.currentFile = { path: '/Posts/Markdowns/test.md', name: 'test.md' };
            wrapper.vm.content = 'Test content';
            wrapper.vm.currentFileVersion = { lastModified: 1000, etag: 'old-etag' };

            // Mock 409 conflict error
            axios.post.mockRejectedValueOnce({
                response: {
                    status: 409,
                    data: {
                        error: 'version_conflict',
                        currentVersion: { lastModified: 2000, etag: 'new-etag' }
                    }
                }
            });

            // Mock confirm dialog
            const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValueOnce(false);

            // Mock reload
            axios.get.mockResolvedValueOnce({
                data: {
                    content: 'Updated content',
                    version: { lastModified: 2000, etag: 'new-etag' }
                }
            });

            // Mock alert
            const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => { });

            // Try to save
            await wrapper.vm.handleSave();

            // Should prompt user about conflict
            expect(confirmSpy).toHaveBeenCalled();
            expect(confirmSpy.mock.calls[0][0]).toContain('版本冲突');

            confirmSpy.mockRestore();
            alertSpy.mockRestore();
        });

        it('allows force save on conflict', async () => {
            const wrapper = mount(EditorPage, {
                global: {
                    stubs: {
                        MonacoEditor: true
                    }
                }
            });

            // Set up current file
            wrapper.vm.currentFile = { path: '/Posts/Markdowns/test.md', name: 'test.md' };
            wrapper.vm.content = 'Test content';
            wrapper.vm.currentFileVersion = { lastModified: 1000, etag: 'old-etag' };

            // Mock 409 conflict error
            axios.post.mockRejectedValueOnce({
                response: {
                    status: 409,
                    data: {
                        error: 'version_conflict',
                        currentVersion: { lastModified: 2000, etag: 'new-etag' }
                    }
                }
            });

            // Mock confirm dialog - user chooses to force save
            const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValueOnce(true);

            // Mock successful force save
            axios.post.mockResolvedValueOnce({
                data: {
                    success: true,
                    version: { lastModified: 3000, etag: 'newest-etag' }
                }
            });

            // Mock alert
            const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => { });

            // Try to save
            await wrapper.vm.handleSave();

            // Should have called save twice (initial + force)
            expect(axios.post).toHaveBeenCalledTimes(2);
            expect(wrapper.vm.saveStatus).toBe('saved');

            confirmSpy.mockRestore();
            alertSpy.mockRestore();
        });
    });
});
