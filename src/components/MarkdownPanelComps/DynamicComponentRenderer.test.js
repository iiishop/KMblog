import { afterEach, describe, expect, it, vi } from 'vitest';
import { defineComponent, h, onUnmounted } from 'vue';
import { renderDynamicComponents, unmountDynamicComponents } from './DynamicComponentRenderer';

describe('Markdown component ownership', () => {
    afterEach(() => { document.body.innerHTML = ''; });

    it('unmounts detached blocks and releases their resources without affecting another article', () => {
        const cleanup = vi.fn();
        const Block = defineComponent({
            setup() {
                onUnmounted(cleanup);
                return () => h('span', 'block');
            }
        });
        const first = document.createElement('article');
        const second = document.createElement('article');
        document.body.append(first, second);
        first.innerHTML = second.innerHTML = '<test-block></test-block>';
        renderDynamicComponents(first, { 'test-block': Block });
        renderDynamicComponents(second, { 'test-block': Block });

        // Even if v-html has already detached the old elements, cleanup must still run.
        first.innerHTML = '<p>new article</p>';
        unmountDynamicComponents(first);
        unmountDynamicComponents(first);
        expect(cleanup).toHaveBeenCalledTimes(1);
        expect(second.textContent).toBe('block');
        unmountDynamicComponents(second);
        expect(cleanup).toHaveBeenCalledTimes(2);
    });

    it('cleans up the previous apps before mounting a surface again', () => {
        const cleanup = vi.fn();
        const Block = defineComponent({
            setup() { onUnmounted(cleanup); return () => h('span', 'block'); }
        });
        const container = document.createElement('article');
        container.innerHTML = '<test-block></test-block>';
        renderDynamicComponents(container, { 'test-block': Block });
        renderDynamicComponents(container, { 'test-block': Block });
        expect(cleanup).toHaveBeenCalledTimes(1);
        expect(container.textContent).toBe('block');
        unmountDynamicComponents(container);
        expect(cleanup).toHaveBeenCalledTimes(2);
    });
});

it('disposes preview-owned apps without unmounting another article', () => {
    const disposed = vi.fn();
    const Block = defineComponent({ setup() { onUnmounted(disposed); return () => h('span', 'mounted'); } });
    const preview = document.createElement('div');
    const article = document.createElement('div');
    preview.innerHTML = article.innerHTML = '<testblock></testblock>';
    renderDynamicComponents(preview, { testblock: Block });
    renderDynamicComponents(article, { testblock: Block });
    unmountDynamicComponents(preview);
    unmountDynamicComponents(preview);
    expect(disposed).toHaveBeenCalledTimes(1);
    expect(article.textContent).toBe('mounted');
    unmountDynamicComponents(article);
    expect(disposed).toHaveBeenCalledTimes(2);
});
