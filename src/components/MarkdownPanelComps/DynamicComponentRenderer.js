import { createApp, h } from 'vue';

export function renderDynamicComponents(container, componentsMap) {
    if (container) {
        Object.keys(componentsMap).forEach((selector) => {
            const Component = componentsMap[selector];
            const elements = container.querySelectorAll(selector);
            elements.forEach((el) => {
                const props = {};
                for (const attr of el.attributes) {
                    if (attr.name.startsWith(':')) {
                        const propName = attr.name.slice(1);
                        props[propName] = attr.value.replace(/['"]/g, '');
                    }
                }
                const app = createApp({
                    render() {
                        return h(Component, props);
                    }
                });
                app.mount(el);
            });
        });
    }
}