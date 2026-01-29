import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import Graph from './Graph.vue';
import gsap from 'gsap';

// Mock GSAP
vi.mock('gsap', () => ({
    default: {
        timeline: vi.fn((config) => {
            // Store the onComplete callback to call it later
            const timelineMock = {
                to: vi.fn().mockReturnThis(),
                _onComplete: config?.onComplete,
            };
            // Simulate timeline completion after a short delay
            if (config?.onComplete) {
                setTimeout(() => config.onComplete(), 0);
            }
            return timelineMock;
        }),
    },
}));

describe('Graph.vue - Click Expand Animation', () => {
    let wrapper;
    const mockImage = {
        id: 'test-image-1',
        src: '/test-image.jpg',
        alt: 'Test Image',
        title: 'Test Title',
        date: '2024-01-01',
        aspectRatio: 1.5,
        dominantColor: 'hsl(250, 60%, 65%)',
    };

    beforeEach(() => {
        // Clear all mocks before each test
        vi.clearAllMocks();

        // Mock IntersectionObserver properly as a class
        global.IntersectionObserver = class IntersectionObserver {
            constructor() {
                this.observe = vi.fn();
                this.unobserve = vi.fn();
                this.disconnect = vi.fn();
            }
        };

        // Mock requestAnimationFrame - don't call callback to avoid infinite loop
        global.requestAnimationFrame = vi.fn(() => 1);
        global.cancelAnimationFrame = vi.fn();
    });

    it('should render the graph card', () => {
        wrapper = mount(Graph, {
            props: {
                image: mockImage,
                index: 0,
            },
        });

        expect(wrapper.find('.graph-card').exists()).toBe(true);
    });

    it('should call GSAP timeline when card is clicked', async () => {
        wrapper = mount(Graph, {
            props: {
                image: mockImage,
                index: 0,
            },
        });

        const card = wrapper.find('.graph-card');
        await card.trigger('click');

        // Verify GSAP timeline was created
        expect(gsap.timeline).toHaveBeenCalled();
    });

    it('should emit click event with image data and card rect', async () => {
        wrapper = mount(Graph, {
            props: {
                image: mockImage,
                index: 0,
            },
        });

        const card = wrapper.find('.graph-card');
        await card.trigger('click');

        // Wait for GSAP timeline onComplete callback
        await new Promise(resolve => setTimeout(resolve, 50));
        await wrapper.vm.$nextTick();

        // Verify click event was emitted with correct data
        expect(wrapper.emitted('click')).toBeTruthy();
        expect(wrapper.emitted('click')[0][0]).toEqual(mockImage);
        // Second argument should be the card rect (DOMRect object)
        expect(wrapper.emitted('click')[0][1]).toBeDefined();
    });

    it('should prevent multiple clicks during animation', async () => {
        wrapper = mount(Graph, {
            props: {
                image: mockImage,
                index: 0,
            },
        });

        const card = wrapper.find('.graph-card');

        // Click multiple times rapidly
        await card.trigger('click');
        await card.trigger('click');
        await card.trigger('click');

        // GSAP timeline should only be called once
        expect(gsap.timeline).toHaveBeenCalledTimes(1);
    });

    it('should set isExpanding state when clicked', async () => {
        wrapper = mount(Graph, {
            props: {
                image: mockImage,
                index: 0,
            },
        });

        const card = wrapper.find('.graph-card');
        await card.trigger('click');

        // Check if is-expanding class is added
        expect(wrapper.find('.graph-card').classes()).toContain('is-expanding');
    });
});


describe('Graph.vue - Mouse Interaction', () => {
    let wrapper;
    const mockImage = {
        id: 'test-image-1',
        src: '/test-image.jpg',
        alt: 'Test Image',
        title: 'Test Title',
        date: '2024-01-01',
        aspectRatio: 1.5,
        dominantColor: 'hsl(250, 60%, 65%)',
    };

    beforeEach(() => {
        // Clear all mocks before each test
        vi.clearAllMocks();

        // Mock IntersectionObserver properly as a class
        global.IntersectionObserver = class IntersectionObserver {
            constructor() {
                this.observe = vi.fn();
                this.unobserve = vi.fn();
                this.disconnect = vi.fn();
            }
        };

        // Mock requestAnimationFrame - don't call callback to avoid infinite loop
        global.requestAnimationFrame = vi.fn(() => 1);
        global.cancelAnimationFrame = vi.fn();
    });

    it('should add hover class on mouse enter', async () => {
        wrapper = mount(Graph, {
            props: {
                image: mockImage,
                index: 0,
            },
        });

        const card = wrapper.find('.graph-card');

        // Hover the card
        await card.trigger('mouseenter');

        // Check if is-hovered class is added
        expect(card.classes()).toContain('is-hovered');
    });

    it('should remove hover class on mouse leave', async () => {
        wrapper = mount(Graph, {
            props: {
                image: mockImage,
                index: 0,
            },
        });

        const card = wrapper.find('.graph-card');

        // Hover and move
        await card.trigger('mouseenter');
        await card.trigger('mousemove', {
            clientX: 150,
            clientY: 100,
        });

        // Leave
        await card.trigger('mouseleave');

        // Wait for next tick
        await wrapper.vm.$nextTick();

        // Check that hover class is removed
        expect(wrapper.find('.graph-card').classes()).not.toContain('is-hovered');
    });

    it('should update glow position on mouse move', async () => {
        wrapper = mount(Graph, {
            props: {
                image: mockImage,
                index: 0,
            },
        });

        const card = wrapper.find('.graph-card');

        // Hover the card first
        await card.trigger('mouseenter');

        // Simulate mouse move
        await card.trigger('mousemove', {
            clientX: 150,
            clientY: 100,
        });

        // Check if glow position CSS variables are updated
        const style = card.attributes('style');
        expect(style).toContain('--glow-x');
        expect(style).toContain('--glow-y');
    });

    it('should not update glow position when not hovered', async () => {
        wrapper = mount(Graph, {
            props: {
                image: mockImage,
                index: 0,
            },
        });

        const card = wrapper.find('.graph-card');

        // Get initial glow position
        const initialStyle = card.attributes('style');
        const initialGlowX = initialStyle?.match(/--glow-x:\s*([^;]+)/)?.[1];

        // Simulate mouse move without hovering
        await card.trigger('mousemove', {
            clientX: 150,
            clientY: 100,
        });

        // Glow position should remain at default (50%)
        const style = card.attributes('style');
        expect(style).toContain('--glow-x: 50%');
        expect(style).toContain('--glow-y: 50%');
    });
});
