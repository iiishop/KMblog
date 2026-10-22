import { defineComponent, h, onUnmounted } from 'vue';
import { expect, it, vi } from 'vitest';
import { renderDynamicComponents, unmountDynamicComponents } from './DynamicComponentRenderer';

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
