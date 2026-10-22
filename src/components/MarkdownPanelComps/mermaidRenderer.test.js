import { afterEach, describe, expect, it, vi } from 'vitest';
import { flushPromises } from '@vue/test-utils';

const mock = vi.hoisted(() => ({ loads: 0, initialize: vi.fn(), run: vi.fn() }));
vi.mock('mermaid', () => {
    mock.loads++;
    return { default: { initialize: mock.initialize, run: mock.run } };
});
import { createMermaidRenderer } from './mermaidRenderer';

const renderers = [];
function surface(source) {
    const container = document.createElement('article');
    if (source !== undefined) {
        const diagram = document.createElement('div');
        diagram.className = 'mermaid';
        diagram.textContent = source;
        container.appendChild(diagram);
    }
    document.body.appendChild(container);
    const renderer = createMermaidRenderer(() => container);
    renderers.push(renderer);
    return { container, renderer };
}

afterEach(() => {
    renderers.splice(0).forEach(renderer => renderer.dispose());
    document.body.innerHTML = '';
    document.documentElement.removeAttribute('data-theme');
    mock.run.mockReset();
});

describe('lazy Mermaid rendering', () => {
    it('does not import Mermaid for ordinary Markdown', async () => {
        const { renderer } = surface();
        await renderer.render();
        expect(mock.loads).toBe(0);
    });

    it('reuses the original definition on theme changes and disconnects on disposal', async () => {
        const source = 'graph TD\n A["<label>"] --> B';
        const definitions = [];
        mock.run.mockImplementation(async ({ nodes }) => {
            definitions.push(nodes[0].textContent);
            nodes[0].innerHTML = '<svg><text>Rendered label</text></svg>';
            nodes[0].setAttribute('data-processed', 'true');
        });
        const { renderer } = surface(source);
        await renderer.render();
        document.documentElement.setAttribute('data-theme', 'night');
        await flushPromises();
        expect(definitions).toEqual([source, source]);
        expect(mock.initialize).toHaveBeenLastCalledWith(expect.objectContaining({ startOnLoad: false, theme: 'dark' }));
        renderer.dispose();
        document.documentElement.setAttribute('data-theme', 'day');
        await flushPromises();
        expect(mock.run).toHaveBeenCalledTimes(2);
    });

    it('serializes surfaces and skips work disposed while waiting', async () => {
        let finish;
        mock.run.mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
        const first = surface('graph TD; A-->B');
        const second = surface('graph TD; C-->D');
        const firstTask = first.renderer.render();
        await flushPromises();
        const secondTask = second.renderer.render();
        await flushPromises();
        expect(mock.run).toHaveBeenCalledTimes(1);
        second.renderer.dispose();
        finish();
        await Promise.all([firstTask, secondTask]);
        expect(mock.run).toHaveBeenCalledTimes(1);
    });

    it('allows later diagrams to render after a rendering failure', async () => {
        mock.run.mockRejectedValueOnce(new Error('invalid diagram')).mockResolvedValueOnce();
        await expect(surface('bad').renderer.render()).rejects.toThrow('invalid diagram');
        await surface('graph TD; A-->B').renderer.render();
        expect(mock.run).toHaveBeenCalledTimes(2);
    });
});
