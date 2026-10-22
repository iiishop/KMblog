import { afterEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import Graph from './Graph.vue';

let wrapper;
afterEach(() => { wrapper?.unmount(); vi.unstubAllGlobals(); });
describe('gallery compatibility', () => {
    it('loads images without IntersectionObserver and does not restore hover after mouseleave', async () => {
        vi.stubGlobal('IntersectionObserver', undefined);
        const frames = [];
        vi.stubGlobal('requestAnimationFrame', callback => { frames.push(callback); return 1; });
        wrapper = mount(Graph, { props: { image: { src: '/photo.jpg', alt: 'photo' }, index: 0 } });
        await wrapper.vm.$nextTick();
        expect(wrapper.find('img').attributes('src')).toBe('/photo.jpg');
        await wrapper.find('.graph-card').trigger('mouseenter');
        expect(wrapper.classes()).toContain('is-hovered');
        await wrapper.find('.graph-card').trigger('mouseleave');
        frames.splice(0).forEach(callback => callback());
        await wrapper.vm.$nextTick();
        expect(wrapper.classes()).not.toContain('is-hovered');
    });
});
