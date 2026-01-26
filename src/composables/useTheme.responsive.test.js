// src/composables/useTheme.responsive.test.js - Responsive Theme Functionality Tests
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useTheme } from './useTheme';

describe('Responsive Theme Functionality', () => {
    let theme;

    beforeEach(() => {
        // Reset DOM
        document.documentElement.removeAttribute('data-theme');
        document.documentElement.removeAttribute('data-high-contrast');
        document.body.className = '';

        // Clear localStorage
        localStorage.clear();

        // Reset matchMedia mock
        window.matchMedia = vi.fn().mockImplementation(query => ({
            matches: false,
            media: query,
            onchange: null,
            addListener: vi.fn(),
            removeListener: vi.fn(),
            addEventListener: vi.fn(),
            removeEventListener: vi.fn(),
            dispatchEvent: vi.fn(),
        }));

        theme = useTheme();
    });

    describe('Theme Toggle Accessibility', () => {
        it('should maintain theme toggle functionality on small screens', () => {
            // Simulate mobile viewport
            global.innerWidth = 375;
            global.innerHeight = 667;

            // Initialize theme
            theme.initializeTheme();

            // Toggle theme
            const initialMode = theme.currentMode.value;
            theme.toggleTheme();

            // Verify theme changed
            expect(theme.currentMode.value).not.toBe(initialMode);
            expect(theme.currentMode.value).toBe(initialMode === 'light' ? 'dark' : 'light');
        });

        it('should maintain theme toggle functionality on tablet screens', () => {
            // Simulate tablet viewport
            global.innerWidth = 768;
            global.innerHeight = 1024;

            // Initialize theme
            theme.initializeTheme();

            // Toggle theme
            const initialMode = theme.currentMode.value;
            theme.toggleTheme();

            // Verify theme changed
            expect(theme.currentMode.value).not.toBe(initialMode);
        });

        it('should maintain theme toggle functionality on desktop screens', () => {
            // Simulate desktop viewport
            global.innerWidth = 1920;
            global.innerHeight = 1080;

            // Initialize theme
            theme.initializeTheme();

            // Toggle theme
            const initialMode = theme.currentMode.value;
            theme.toggleTheme();

            // Verify theme changed
            expect(theme.currentMode.value).not.toBe(initialMode);
        });
    });

    describe('Theme Persistence Across Breakpoints', () => {
        it('should persist theme preference when viewport changes', () => {
            // Initialize on desktop
            global.innerWidth = 1920;
            theme.initializeTheme();

            // Set dark mode
            theme.setTheme('dark');
            expect(theme.currentMode.value).toBe('dark');

            // Simulate viewport change to mobile
            global.innerWidth = 375;
            window.dispatchEvent(new Event('resize'));

            // Theme should still be dark
            expect(theme.currentMode.value).toBe('dark');
        });

        it('should maintain theme state across orientation changes', () => {
            // Initialize in portrait
            global.innerWidth = 375;
            global.innerHeight = 667;
            theme.initializeTheme();

            // Set light mode
            theme.setTheme('light');
            expect(theme.currentMode.value).toBe('light');

            // Simulate orientation change to landscape
            global.innerWidth = 667;
            global.innerHeight = 375;
            window.dispatchEvent(new Event('orientationchange'));

            // Theme should still be light
            expect(theme.currentMode.value).toBe('light');
        });
    });

    describe('CSS Variable Application Across Breakpoints', () => {
        it('should apply CSS variables correctly on mobile', () => {
            global.innerWidth = 375;
            theme.initializeTheme();
            theme.setTheme('dark');

            // Verify CSS variables are set
            const root = document.documentElement;
            const bodyBg = root.style.getPropertyValue('--theme-body-bg');

            expect(bodyBg).toBeTruthy();
            expect(root.getAttribute('data-theme')).toBe('dark');
        });

        it('should apply CSS variables correctly on tablet', () => {
            global.innerWidth = 768;
            theme.initializeTheme();
            theme.setTheme('light');

            // Verify CSS variables are set
            const root = document.documentElement;
            const bodyBg = root.style.getPropertyValue('--theme-body-bg');

            expect(bodyBg).toBeTruthy();
            expect(root.getAttribute('data-theme')).toBe('day');
        });

        it('should apply CSS variables correctly on desktop', () => {
            global.innerWidth = 1920;
            theme.initializeTheme();
            theme.setTheme('dark');

            // Verify CSS variables are set
            const root = document.documentElement;
            const bodyBg = root.style.getPropertyValue('--theme-body-bg');

            expect(bodyBg).toBeTruthy();
            expect(root.getAttribute('data-theme')).toBe('dark');
        });
    });

    describe('Theme Transitions Across Breakpoints', () => {
        it('should handle transitions on mobile devices', () => {
            global.innerWidth = 375;
            theme.initializeTheme();

            // Verify no-transitions class is added initially
            expect(document.body.classList.contains('no-transitions')).toBe(true);

            // Wait for transitions to be enabled
            return new Promise(resolve => {
                setTimeout(() => {
                    // Transitions should be enabled after delay
                    expect(theme.transitionsEnabled.value).toBe(true);
                    resolve();
                }, 150);
            });
        });

        it('should respect reduced motion preference on all screen sizes', () => {
            // Mock reduced motion preference
            window.matchMedia = vi.fn().mockImplementation(query => {
                if (query === '(prefers-reduced-motion: reduce)') {
                    return {
                        matches: true,
                        media: query,
                        addEventListener: vi.fn(),
                        removeEventListener: vi.fn(),
                    };
                }
                return {
                    matches: false,
                    media: query,
                    addEventListener: vi.fn(),
                    removeEventListener: vi.fn(),
                };
            });

            // Test on mobile
            global.innerWidth = 375;
            theme.initializeTheme();

            // Transitions should be disabled
            return new Promise(resolve => {
                setTimeout(() => {
                    expect(theme.transitionsEnabled.value).toBe(false);
                    resolve();
                }, 150);
            });
        });
    });

    describe('System Theme Detection Across Breakpoints', () => {
        it('should detect system theme on mobile', () => {
            global.innerWidth = 375;

            // Mock dark mode preference
            window.matchMedia = vi.fn().mockImplementation(query => {
                if (query === '(prefers-color-scheme: dark)') {
                    return {
                        matches: true,
                        media: query,
                        addEventListener: vi.fn(),
                        removeEventListener: vi.fn(),
                    };
                }
                return {
                    matches: false,
                    media: query,
                    addEventListener: vi.fn(),
                    removeEventListener: vi.fn(),
                };
            });

            const detectedTheme = theme.detectSystemTheme();
            expect(detectedTheme).toBe('dark');
        });

        it('should detect system theme on tablet', () => {
            global.innerWidth = 768;

            // Mock light mode preference
            window.matchMedia = vi.fn().mockImplementation(query => ({
                matches: false,
                media: query,
                addEventListener: vi.fn(),
                removeEventListener: vi.fn(),
            }));

            const detectedTheme = theme.detectSystemTheme();
            expect(detectedTheme).toBe('light');
        });

        it('should detect system theme on desktop', () => {
            global.innerWidth = 1920;

            // Mock dark mode preference
            window.matchMedia = vi.fn().mockImplementation(query => {
                if (query === '(prefers-color-scheme: dark)') {
                    return {
                        matches: true,
                        media: query,
                        addEventListener: vi.fn(),
                        removeEventListener: vi.fn(),
                    };
                }
                return {
                    matches: false,
                    media: query,
                    addEventListener: vi.fn(),
                    removeEventListener: vi.fn(),
                };
            });

            const detectedTheme = theme.detectSystemTheme();
            expect(detectedTheme).toBe('dark');
        });
    });

    describe('Theme State Consistency', () => {
        it('should maintain consistent theme state across viewport changes', () => {
            // Start on mobile
            global.innerWidth = 375;
            theme.initializeTheme();
            theme.setTheme('dark');

            const initialTheme = theme.currentTheme.value;
            const initialMode = theme.currentMode.value;

            // Change to tablet
            global.innerWidth = 768;
            window.dispatchEvent(new Event('resize'));

            // State should be unchanged
            expect(theme.currentTheme.value).toBe(initialTheme);
            expect(theme.currentMode.value).toBe(initialMode);

            // Change to desktop
            global.innerWidth = 1920;
            window.dispatchEvent(new Event('resize'));

            // State should still be unchanged
            expect(theme.currentTheme.value).toBe(initialTheme);
            expect(theme.currentMode.value).toBe(initialMode);
        });

        it('should not interfere with theme switching at different breakpoints', () => {
            const breakpoints = [375, 768, 1024, 1920];

            breakpoints.forEach(width => {
                global.innerWidth = width;
                theme.initializeTheme();

                // Toggle theme
                theme.toggleTheme();
                const mode1 = theme.currentMode.value;

                // Toggle again
                theme.toggleTheme();
                const mode2 = theme.currentMode.value;

                // Should toggle back
                expect(mode2).not.toBe(mode1);
            });
        });
    });

    describe('High Contrast Mode Across Breakpoints', () => {
        it('should apply high contrast mode on mobile', () => {
            global.innerWidth = 375;

            // Mock high contrast preference
            window.matchMedia = vi.fn().mockImplementation(query => {
                if (query === '(forced-colors: active)' ||
                    query === '(prefers-contrast: high)' ||
                    query === '(prefers-contrast: more)') {
                    return {
                        matches: true,
                        media: query,
                        addEventListener: vi.fn(),
                        removeEventListener: vi.fn(),
                    };
                }
                return {
                    matches: false,
                    media: query,
                    addEventListener: vi.fn(),
                    removeEventListener: vi.fn(),
                };
            });

            theme.initializeTheme();

            // High contrast should be detected
            expect(theme.highContrastMode.value).toBe(true);
        });

        it('should apply high contrast mode on desktop', () => {
            global.innerWidth = 1920;

            // Mock high contrast preference
            window.matchMedia = vi.fn().mockImplementation(query => {
                if (query === '(forced-colors: active)') {
                    return {
                        matches: true,
                        media: query,
                        addEventListener: vi.fn(),
                        removeEventListener: vi.fn(),
                    };
                }
                return {
                    matches: false,
                    media: query,
                    addEventListener: vi.fn(),
                    removeEventListener: vi.fn(),
                };
            });

            theme.initializeTheme();

            // High contrast should be detected
            expect(theme.highContrastMode.value).toBe(true);
        });
    });
});
