import { createApp, h } from 'vue';

const mountedApps = new Map();

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

                // 如果已经有实例挂载在这个元素上，先卸载它
                if (mountedApps.has(el)) {
                    mountedApps.get(el).unmount();
                }

                const app = createApp({
                    render() {
                        return h(Component, props);
                    }
                });
                app.mount(el);

                // 记录这个实例
                mountedApps.set(el, app);
            });
        });
    }
}