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
                        let propValue = attr.value;

                        // 特殊处理复杂属性值
                        if (propValue.startsWith('JSON.parse(')) {
                            // 处理 JSON.parse() 调用
                            try {
                                const jsonMatch = propValue.match(/JSON\.parse\('(.+)'\)/);
                                if (jsonMatch) {
                                    const escapedJson = jsonMatch[1];
                                    const unescapedJson = escapedJson.replace(/&#39;/g, "'").replace(/&quot;/g, '"');
                                    props[propName] = JSON.parse(unescapedJson);
                                }
                            } catch (e) {
                                console.warn('Failed to parse JSON prop:', propValue, e);
                                props[propName] = [];
                            }
                        } else if ((propValue.startsWith('[') && propValue.endsWith(']')) ||
                            (propValue.startsWith('{') && propValue.endsWith('}'))) {
                            // 尝试作为 JSON 解析 (数组或对象)
                            try {
                                // 替换 HTML 实体
                                const unescapedJson = propValue.replace(/&quot;/g, '"').replace(/&#39;/g, "'");
                                props[propName] = JSON.parse(unescapedJson);
                            } catch (e) {
                                console.warn('Failed to parse JSON prop value:', propValue, e);
                                props[propName] = propValue.replace(/['"]/g, '');
                            }
                        } else {
                            // 普通属性值处理
                            props[propName] = propValue.replace(/['"]/g, '');
                        }
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