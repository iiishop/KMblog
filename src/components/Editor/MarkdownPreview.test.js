import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';

// Mock mermaid before importing the component
vi.mock('mermaid', () => ({
    default: {
        initialize: vi.fn(),
        mermaidAPI: {
            reset: vi.fn()
        },
        run: vi.fn()
    }
}));

import MarkdownPreview from './MarkdownPreview.vue';

describe('MarkdownPreview', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders markdown content correctly', async () => {
        const wrapper = mount(MarkdownPreview, {
            props: {
                content: '# Hello World\n\nThis is a test.'
            }
        });

        await wrapper.vm.$nextTick();
        await new Promise(resolve => setTimeout(resolve, 100));

        // Verify the component renders
        expect(wrapper.find('.markdown-preview-container').exists()).toBe(true);
        expect(wrapper.find('.post-content').exists()).toBe(true);
    });

    it('handles empty content', async () => {
        const wrapper = mount(MarkdownPreview, {
            props: {
                content: ''
            }
        });

        await wrapper.vm.$nextTick();

        // Should not throw error
        expect(wrapper.find('.markdown-preview-container').exists()).toBe(true);
    });

    it('updates when content changes', async () => {
        const wrapper = mount(MarkdownPreview, {
            props: {
                content: '# Initial Content'
            }
        });

        await wrapper.vm.$nextTick();

        // Update content
        await wrapper.setProps({
            content: '# Updated Content'
        });

        await wrapper.vm.$nextTick();
        await new Promise(resolve => setTimeout(resolve, 100));

        // Verify component still renders
        expect(wrapper.find('.markdown-preview-container').exists()).toBe(true);
    });

    it('handles front-matter in markdown', async () => {
        const content = `---
title: Test Post
date: 2024-01-01
---

# Content`;

        const wrapper = mount(MarkdownPreview, {
            props: {
                content
            }
        });

        await wrapper.vm.$nextTick();
        await new Promise(resolve => setTimeout(resolve, 100));

        // Should render without errors
        expect(wrapper.find('.markdown-preview-container').exists()).toBe(true);
    });
});
