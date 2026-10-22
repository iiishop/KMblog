import { initializeMermaid } from './mermaidConfig';

let libraryPromise;
let renderQueue = Promise.resolve();

function loadMermaid() {
    if (!libraryPromise) {
        libraryPromise = import('mermaid').then(module => module.default).catch(error => {
            libraryPromise = null;
            throw error;
        });
    }
    return libraryPromise;
}

// Mermaid has global configuration, so serialize rendering across article/preview surfaces.
export function createMermaidRenderer(getContainer) {
    const sources = new WeakMap();
    let observer;
    let version = 0;
    let disposed = false;

    function render() {
        const currentVersion = ++version;
        const container = getContainer();
        const nodes = Array.from(container?.querySelectorAll('.mermaid') || []);
        if (disposed || nodes.length === 0) {
            observer?.disconnect();
            observer = null;
            return Promise.resolve();
        }
        for (const node of nodes) {
            if (!sources.has(node)) sources.set(node, node.textContent);
        }
        if (!observer) {
            observer = new MutationObserver(() => {
                render().catch(error => console.warn('Mermaid theme rendering failed:', error));
            });
            observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
        }

        const isCurrent = () => !disposed && currentVersion === version && getContainer() === container;
        const task = renderQueue.then(async () => {
            if (!isCurrent()) return;
            const mermaid = await loadMermaid();
            if (!isCurrent()) return;
            const currentNodes = nodes.filter(node => container.contains(node));
            if (!currentNodes.length) return;
            initializeMermaid(mermaid);
            for (const node of currentNodes) {
                // Theme changes must render the original definition, never the previous SVG text.
                node.textContent = sources.get(node);
                node.removeAttribute('data-processed');
            }
            await mermaid.run({ nodes: currentNodes });
            if (!isCurrent()) return;
            currentNodes.forEach(node => {
                const svg = node.querySelector('svg');
                if (!svg) return;
                svg.removeAttribute('width');
                svg.removeAttribute('height');
                Object.assign(svg.style, {
                    width: '100%', height: '400px', maxWidth: '100%', maxHeight: '400px',
                    display: 'block', margin: '0 auto'
                });
            });
        });
        // A malformed diagram must not poison the queue for other articles.
        renderQueue = task.catch(() => {});
        return task;
    }

    function dispose() {
        disposed = true;
        version++;
        observer?.disconnect();
        observer = null;
    }

    return { render, dispose };
}
