import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import ImageModal from './ImageModal.vue';
import gsap from 'gsap';
import anime from 'animejs';

// Mock GSAP
vi.mock('gsap', () => ({
    default: {
        set: vi.fn(),
        to: vi.fn().mockReturnThis(),
        timeline: vi.fn((config) => {
            const timelineMock = {
                to: vi.fn().mockReturnThis(),
                add: vi.fn().mockReturnThis(),
                _onComplete: config?.onComplete,
            };
            if (config?.onComplete) {
                setTimeout(() => config.onComplete(), 0);
            }
            return timelineMock;
        }),
    },
}));

// Mock anime.js
vi.mock('animejs', () => ({
    animate: vi.fn((config) => {
        if (config.update) {
            config.update();
        }
        if (config.complete) {
            setTimeout(() => config.complete(), 0);
        }
    }),
}));

// Mock markdown-it
vi.mock('markdown-it', () => {
    return {
        default: class MarkdownIt {
            constructor() {
                this.render = vi.fn((text) => `<p>${text}</p>`);
            }
        }
    };
});

describe('ImageModal.vue - Keyboard Support', () => {
    let wrapper;
    const mockImage = {
        id: 'test-image-1',
        src: '/test-image.jpg',
        alt: 'Test Image',
        title: 'Test Title',
        width: 1920,
        height: 1080,
    };

    beforeEach(() => {
        vi.clearAllMocks();

        global.fetch = vi.fn(() =>
            Promise.resolve({
                ok: false,
            })
        );
    });

    afterEach(() => {
        if (wrapper) {
            wrapper.unmount();
        }
    });

    it('should close modal on Escape key', async () => {
        wrapper = mount(ImageModal, {
            props: {
                image: mockImage,
            },
        });

        // Wait for modal to open
        await wrapper.vm.$nextTick();

        // Simulate Escape key press
        const event = new KeyboardEvent('keydown', { key: 'Escape' });
        document.dispatchEvent(event);

        await new Promise(resolve => setTimeout(resolve, 150));

        expect(wrapper.emitted('close')).toBeTruthy();
    });

    it('should emit prev on ArrowLeft key', async () => {
        wrapper = mount(ImageModal, {
            props: {
                image: mockImage,
            },
        });

        await wrapper.vm.$nextTick();

        const event = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
        document.dispatchEvent(event);

        await wrapper.vm.$nextTick();

        expect(wrapper.emitted('prev')).toBeTruthy();
    });

    it('should emit next on ArrowRight key', async () => {
        wrapper = mount(ImageModal, {
            props: {
                image: mockImage,
            },
        });

        await wrapper.vm.$nextTick();

        const event = new KeyboardEvent('keydown', { key: 'ArrowRight' });
        document.dispatchEvent(event);

        await wrapper.vm.$nextTick();

        expect(wrapper.emitted('next')).toBeTruthy();
    });
});

describe('ImageModal.vue - Markdown Loading', () => {
    let wrapper;
    const mockImage = {
        id: 'test-image-1',
        src: '/test-image.jpg',
        alt: 'Test Image',
        title: 'Test Title',
        width: 1920,
        height: 1080,
        mdPath: '/test-image.md',
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        if (wrapper) {
            wrapper.unmount();
        }
    });

    it('should load markdown description from mdPath', async () => {
        global.fetch = vi.fn(() =>
            Promise.resolve({
                ok: true,
                text: () => Promise.resolve('# Test Markdown'),
            })
        );

        wrapper = mount(ImageModal, {
            props: {
                image: mockImage,
            },
        });

        await new Promise(resolve => setTimeout(resolve, 50));

        expect(global.fetch).toHaveBeenCalledWith('/test-image.md');
    });

    it('should handle markdown loading failure gracefully', async () => {
        global.fetch = vi.fn(() =>
            Promise.resolve({
                ok: false,
            })
        );

        wrapper = mount(ImageModal, {
            props: {
                image: mockImage,
            },
        });

        await new Promise(resolve => setTimeout(resolve, 50));

        // Should not throw error
        expect(wrapper.vm).toBeTruthy();
    });
});

describe('ImageModal.vue - Component Props', () => {
    let wrapper;
    const mockImage = {
        id: 'test-image-1',
        src: '/test-image.jpg',
        alt: 'Test Image',
        title: 'Test Title',
        width: 1920,
        height: 1080,
    };

    beforeEach(() => {
        vi.clearAllMocks();

        global.fetch = vi.fn(() =>
            Promise.resolve({
                ok: false,
            })
        );
    });

    afterEach(() => {
        if (wrapper) {
            wrapper.unmount();
        }
    });

    it('should compute image dimensions correctly', () => {
        wrapper = mount(ImageModal, {
            props: {
                image: mockImage,
            },
        });

        expect(wrapper.vm.imageDimensions).toBe('1920 × 1080');
    });

    it('should compute image format correctly', () => {
        wrapper = mount(ImageModal, {
            props: {
                image: mockImage,
            },
        });

        expect(wrapper.vm.imageFormat).toBe('JPG');
    });

    it('should handle image without dimensions', () => {
        const imageWithoutDimensions = {
            id: 'test-image-2',
            src: '/test.png',
            alt: 'Test',
            title: 'Test',
        };

        wrapper = mount(ImageModal, {
            props: {
                image: imageWithoutDimensions,
            },
        });

        expect(wrapper.vm.imageDimensions).toBe('');
    });
});

describe('ImageModal.vue - Animation Integration', () => {
    let wrapper;
    const mockImage = {
        id: 'test-image-1',
        src: '/test-image.jpg',
        alt: 'Test Image',
        title: 'Test Title',
        width: 1920,
        height: 1080,
    };

    beforeEach(() => {
        vi.clearAllMocks();

        global.fetch = vi.fn(() =>
            Promise.resolve({
                ok: false,
            })
        );

        // Mock canvas context
        HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
            clearRect: vi.fn(),
            fillStyle: '',
            beginPath: vi.fn(),
            arc: vi.fn(),
            fill: vi.fn(),
        }));
    });

    afterEach(() => {
        if (wrapper) {
            wrapper.unmount();
        }
    });

    it('should initialize component successfully', () => {
        wrapper = mount(ImageModal, {
            props: {
                image: mockImage,
            },
        });

        // Component initializes successfully
        expect(wrapper.vm).toBeTruthy();
    });

    it('should have handleClose method', () => {
        wrapper = mount(ImageModal, {
            props: {
                image: mockImage,
            },
        });

        expect(typeof wrapper.vm.handleClose).toBe('function');
    });

    it('should emit close event when handleClose is called', async () => {
        wrapper = mount(ImageModal, {
            props: {
                image: mockImage,
            },
        });

        // Call handleClose directly
        wrapper.vm.handleClose();
        await wrapper.vm.$nextTick();

        // Check if close event was emitted
        expect(wrapper.emitted('close')).toBeTruthy();
    });
});
