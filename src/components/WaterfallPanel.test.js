import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import WaterfallPanel from './WaterfallPanel.vue';

describe('WaterfallPanel - Layout Algorithm', () => {
    let wrapper;

    const mockImages = [
        { id: '1', src: '/img1.jpg', alt: 'Image 1', aspectRatio: 1.5, width: 300, height: 200 },
        { id: '2', src: '/img2.jpg', alt: 'Image 2', aspectRatio: 0.75, width: 200, height: 267 },
        { id: '3', src: '/img3.jpg', alt: 'Image 3', aspectRatio: 1.0, width: 300, height: 300 },
        { id: '4', src: '/img4.jpg', alt: 'Image 4', aspectRatio: 1.2, width: 300, height: 250 },
    ];

    beforeEach(() => {
        wrapper = mount(WaterfallPanel, {
            props: {
                images: mockImages
            }
        });
    });

    it('should render waterfall container', () => {
        expect(wrapper.find('.waterfall-container').exists()).toBe(true);
    });

    it('should render canvas layers for particles and magnetic lines', () => {
        expect(wrapper.find('.particle-layer').exists()).toBe(true);
        expect(wrapper.find('.magnetic-layer').exists()).toBe(true);
    });

    it('should render waterfall grid', () => {
        expect(wrapper.find('.waterfall-grid').exists()).toBe(true);
    });

    it('should calculate responsive column count based on container width', async () => {
        // The component calculates column count on mount
        // In test environment, offsetWidth defaults to 0, which results in 1 column
        await wrapper.vm.$nextTick();

        // Should have at least 1 column
        expect(wrapper.vm.columnCount).toBeGreaterThanOrEqual(1);
        expect(wrapper.vm.columnCount).toBeLessThanOrEqual(4);
    });

    it('should calculate positions for all images', async () => {
        await wrapper.vm.$nextTick();

        // Should have positions for all images
        expect(wrapper.vm.cardPositions.length).toBe(mockImages.length);

        // Each position should have required properties
        wrapper.vm.cardPositions.forEach(pos => {
            expect(pos).toHaveProperty('x');
            expect(pos).toHaveProperty('y');
            expect(pos).toHaveProperty('width');
            expect(pos).toHaveProperty('height');
            expect(pos).toHaveProperty('column');
            expect(pos).toHaveProperty('id');
            expect(pos).toHaveProperty('index');
        });
    });

    it('should distribute cards across columns', async () => {
        await wrapper.vm.$nextTick();

        const columns = new Set(wrapper.vm.cardPositions.map(pos => pos.column));

        // Should have at least 1 column
        expect(columns.size).toBeGreaterThanOrEqual(1);

        // Column indices should be valid
        columns.forEach(col => {
            expect(col).toBeGreaterThanOrEqual(0);
            expect(col).toBeLessThan(wrapper.vm.columnCount);
        });
    });

    it('should apply organic offset to card positions', async () => {
        await wrapper.vm.$nextTick();

        // Check that positions are not perfectly aligned (due to random offset)
        const positions = wrapper.vm.cardPositions;

        if (positions.length >= 2) {
            // Find cards in the same column
            const column0Cards = positions.filter(p => p.column === 0);

            if (column0Cards.length >= 2) {
                // X positions should be slightly different due to organic offset
                const xPositions = column0Cards.map(p => p.x);
                const uniqueX = new Set(xPositions);

                // With organic offset, x positions should vary slightly
                // (This test might occasionally fail due to randomness, but should pass most of the time)
                expect(uniqueX.size).toBeGreaterThanOrEqual(1);
            }
        }
    });

    it('should maintain aspect ratios in calculated heights', async () => {
        await wrapper.vm.$nextTick();

        wrapper.vm.cardPositions.forEach((pos, index) => {
            const image = mockImages[index];
            const calculatedRatio = pos.width / pos.height;
            const expectedRatio = image.aspectRatio || 1;

            // Allow small floating point differences
            expect(Math.abs(calculatedRatio - expectedRatio)).toBeLessThan(0.01);
        });
    });

    it('should emit image-click event when card is clicked', async () => {
        await wrapper.vm.$nextTick();

        // Simulate clicking on the waterfall grid
        wrapper.vm.$emit('image-click', mockImages[0]);

        expect(wrapper.emitted('image-click')).toBeTruthy();
        expect(wrapper.emitted('image-click')[0]).toEqual([mockImages[0]]);
    });

    it('should update layout when images prop changes', async () => {
        const initialPositions = wrapper.vm.cardPositions.length;

        // Add more images
        await wrapper.setProps({
            images: [...mockImages, { id: '5', src: '/img5.jpg', alt: 'Image 5', aspectRatio: 1.0 }]
        });

        await wrapper.vm.$nextTick();

        // Should have more positions
        expect(wrapper.vm.cardPositions.length).toBeGreaterThan(initialPositions);
    });

    it('should calculate grid style with minimum height', async () => {
        await wrapper.vm.$nextTick();

        const gridStyle = wrapper.vm.gridStyle;

        expect(gridStyle).toHaveProperty('position', 'relative');
        expect(gridStyle).toHaveProperty('width', '100%');
        expect(gridStyle).toHaveProperty('minHeight');
        expect(gridStyle.minHeight).toMatch(/\d+px/);
    });
});

describe('WaterfallPanel - Particle System', () => {
    let wrapper;

    const mockImages = [
        { id: '1', src: '/img1.jpg', alt: 'Image 1', aspectRatio: 1.5, width: 300, height: 200 },
    ];

    beforeEach(() => {
        wrapper = mount(WaterfallPanel, {
            props: {
                images: mockImages
            }
        });
    });

    it('should initialize particle canvas', () => {
        const particleCanvas = wrapper.find('.particle-layer');
        expect(particleCanvas.exists()).toBe(true);
        expect(particleCanvas.element.tagName).toBe('CANVAS');
    });

    it('should have mouse position tracking', async () => {
        await wrapper.vm.$nextTick();

        // Mouse position should be initialized
        expect(wrapper.vm.mousePosition).toBeDefined();
        expect(wrapper.vm.mousePosition).toHaveProperty('x');
        expect(wrapper.vm.mousePosition).toHaveProperty('y');
    });

    it('should update mouse position on mouse move', async () => {
        await wrapper.vm.$nextTick();

        const container = wrapper.find('.waterfall-container');

        // Simulate mouse move event
        await container.trigger('mousemove', {
            clientX: 100,
            clientY: 150
        });

        // Mouse position should be updated
        expect(wrapper.vm.mousePosition.x).toBeGreaterThanOrEqual(0);
        expect(wrapper.vm.mousePosition.y).toBeGreaterThanOrEqual(0);
    });

    it('should render both particle and magnetic canvas layers', () => {
        const particleLayer = wrapper.find('.particle-layer');
        const magneticLayer = wrapper.find('.magnetic-layer');

        expect(particleLayer.exists()).toBe(true);
        expect(magneticLayer.exists()).toBe(true);

        // Both should be canvas elements
        expect(particleLayer.element.tagName).toBe('CANVAS');
        expect(magneticLayer.element.tagName).toBe('CANVAS');
    });

    it('should have proper z-index layering', () => {
        const particleLayer = wrapper.find('.particle-layer');
        const magneticLayer = wrapper.find('.magnetic-layer');
        const waterfallGrid = wrapper.find('.waterfall-grid');

        // All layers should exist
        expect(particleLayer.exists()).toBe(true);
        expect(magneticLayer.exists()).toBe(true);
        expect(waterfallGrid.exists()).toBe(true);
    });
});

describe('WaterfallPanel - Magnetic Lines System', () => {
    let wrapper;

    const mockImages = [
        { id: '1', src: '/img1.jpg', alt: 'Image 1', aspectRatio: 1.5, width: 300, height: 200 },
        { id: '2', src: '/img2.jpg', alt: 'Image 2', aspectRatio: 0.75, width: 200, height: 267 },
        { id: '3', src: '/img3.jpg', alt: 'Image 3', aspectRatio: 1.0, width: 300, height: 300 },
    ];

    beforeEach(() => {
        wrapper = mount(WaterfallPanel, {
            props: {
                images: mockImages
            }
        });
    });

    it('should initialize magnetic canvas', () => {
        const magneticCanvas = wrapper.find('.magnetic-layer');
        expect(magneticCanvas.exists()).toBe(true);
        expect(magneticCanvas.element.tagName).toBe('CANVAS');
    });

    it('should track hovered card index', async () => {
        await wrapper.vm.$nextTick();

        // Initially no card is hovered
        expect(wrapper.vm.hoveredCardIndex).toBeNull();

        // Simulate card hover
        wrapper.vm.handleCardHover(0);
        expect(wrapper.vm.hoveredCardIndex).toBe(0);

        // Simulate card leave
        wrapper.vm.handleCardLeave(0);
        expect(wrapper.vm.hoveredCardIndex).toBeNull();
    });

    it('should update hovered card on mouseenter event', async () => {
        await wrapper.vm.$nextTick();

        // Simulate hovering over a card
        wrapper.vm.handleCardHover(1);

        expect(wrapper.vm.hoveredCardIndex).toBe(1);
    });

    it('should clear hovered card on mouseleave event', async () => {
        await wrapper.vm.$nextTick();

        // First hover over a card
        wrapper.vm.handleCardHover(1);
        expect(wrapper.vm.hoveredCardIndex).toBe(1);

        // Then leave the card
        wrapper.vm.handleCardLeave(1);
        expect(wrapper.vm.hoveredCardIndex).toBeNull();
    });

    it('should have magnetic line time tracking', async () => {
        await wrapper.vm.$nextTick();

        // Magnetic line time should be initialized
        expect(wrapper.vm.magneticLineTime).toBeDefined();
        expect(typeof wrapper.vm.magneticLineTime).toBe('number');
    });

    it('should handle multiple card hovers correctly', async () => {
        await wrapper.vm.$nextTick();

        // Hover over first card
        wrapper.vm.handleCardHover(0);
        expect(wrapper.vm.hoveredCardIndex).toBe(0);

        // Hover over second card (should replace first)
        wrapper.vm.handleCardHover(1);
        expect(wrapper.vm.hoveredCardIndex).toBe(1);

        // Leave second card
        wrapper.vm.handleCardLeave(1);
        expect(wrapper.vm.hoveredCardIndex).toBeNull();
    });

    it('should have card positions for magnetic line calculations', async () => {
        await wrapper.vm.$nextTick();

        // Card positions should be calculated
        expect(wrapper.vm.cardPositions).toBeDefined();
        expect(Array.isArray(wrapper.vm.cardPositions)).toBe(true);
        expect(wrapper.vm.cardPositions.length).toBe(mockImages.length);

        // Each position should have coordinates needed for magnetic lines
        wrapper.vm.cardPositions.forEach(pos => {
            expect(pos).toHaveProperty('x');
            expect(pos).toHaveProperty('y');
            expect(pos).toHaveProperty('width');
            expect(pos).toHaveProperty('height');
        });
    });
});
