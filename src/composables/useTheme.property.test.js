// src/composables/useTheme.property.test.js - Property-Based Tests for Theme Manager Composable
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import * as fc from 'fast-check'

// Mock the config module first
vi.mock('@/config', () => ({
    default: {
        LightTheme: 'day',
        DarkTheme: 'dark',
        enableSystemDetection: true,
        enableTransitions: true,
        transitionDuration: 300,
        themePalettes: {
            day: {
                name: 'day',
                displayName: 'Day Theme',
                colors: {
                    bodyBackground: '#ffffff',
                    bodyText: '#000000',
                    panelBackground: '#f9f9f9',
                    panelShadow: 'rgba(0, 0, 0, 0.1)',
                    panelText: '#000000',
                    panelBorder: 'rgba(0, 0, 0, 0.05)',
                    headerBackground: 'rgba(255, 215, 231, 0.616)',
                    headerBackgroundScrolled: 'rgba(200, 255, 255, 0.7)',
                    headerShadow: 'rgba(0, 0, 0, 0.1)',
                    linkColor: '#667eea',
                    linkHover: '#764ba2',
                    buttonBackground: '#667eea',
                    buttonText: '#ffffff',
                    primary: '#667eea',
                    secondary: '#764ba2',
                    accent: '#f093fb',
                    success: '#10b981',
                    warning: '#f59e0b',
                    error: '#ef4444',
                    info: '#3b82f6'
                }
            },
            dark: {
                name: 'dark',
                displayName: 'Dark Theme',
                colors: {
                    bodyBackground: '#121212',
                    bodyText: '#e0e0e0',
                    panelBackground: '#1e1e1e',
                    panelShadow: 'rgba(0, 0, 0, 0.5)',
                    panelText: '#e0e0e0',
                    panelBorder: 'rgba(255, 255, 255, 0.1)',
                    headerBackground: 'rgba(20, 20, 30, 0.9)',
                    headerBackgroundScrolled: 'rgba(30, 30, 40, 0.95)',
                    headerShadow: 'rgba(0, 0, 0, 0.5)',
                    linkColor: '#a78bfa',
                    linkHover: '#c084fc',
                    buttonBackground: '#a78bfa',
                    buttonText: '#ffffff',
                    primary: '#a78bfa',
                    secondary: '#c084fc',
                    accent: '#f093fb',
                    success: '#34d399',
                    warning: '#fbbf24',
                    error: '#f87171',
                    info: '#60a5fa'
                }
            },
            bright: {
                name: 'bright',
                displayName: 'Bright Theme',
                colors: {
                    bodyBackground: '#fafafa',
                    bodyText: '#1a1a1a',
                    panelBackground: '#ffffff',
                    panelShadow: 'rgba(0, 0, 0, 0.08)',
                    panelText: '#1a1a1a',
                    panelBorder: 'rgba(0, 0, 0, 0.03)',
                    headerBackground: 'rgba(255, 255, 255, 0.9)',
                    headerBackgroundScrolled: 'rgba(255, 255, 255, 0.95)',
                    headerShadow: 'rgba(0, 0, 0, 0.08)',
                    linkColor: '#3b82f6',
                    linkHover: '#1d4ed8',
                    buttonBackground: '#3b82f6',
                    buttonText: '#ffffff',
                    primary: '#3b82f6',
                    secondary: '#1d4ed8',
                    accent: '#8b5cf6',
                    success: '#059669',
                    warning: '#d97706',
                    error: '#dc2626',
                    info: '#0284c7'
                }
            },
            night: {
                name: 'night',
                displayName: 'Night Theme',
                colors: {
                    bodyBackground: '#0a0a0a',
                    bodyText: '#f0f0f0',
                    panelBackground: '#1a1a1a',
                    panelShadow: 'rgba(0, 0, 0, 0.8)',
                    panelText: '#f0f0f0',
                    panelBorder: 'rgba(255, 255, 255, 0.05)',
                    headerBackground: 'rgba(10, 10, 10, 0.95)',
                    headerBackgroundScrolled: 'rgba(15, 15, 15, 0.98)',
                    headerShadow: 'rgba(0, 0, 0, 0.8)',
                    linkColor: '#8b5cf6',
                    linkHover: '#a855f7',
                    buttonBackground: '#8b5cf6',
                    buttonText: '#ffffff',
                    primary: '#8b5cf6',
                    secondary: '#a855f7',
                    accent: '#ec4899',
                    success: '#10b981',
                    warning: '#f59e0b',
                    error: '#ef4444',
                    info: '#06b6d4'
                }
            }
        }
    }
}))

import { useTheme } from './useTheme.js'
import config from '@/config'

describe('useTheme Property-Based Tests', () => {
    let documentElementMock
    let bodyMock
    let consoleWarnSpy

    beforeEach(() => {
        // Mock document.documentElement
        documentElementMock = {
            setAttribute: vi.fn(),
            style: {
                setProperty: vi.fn()
            }
        }

        // Mock document.body
        bodyMock = {
            classList: {
                add: vi.fn(),
                remove: vi.fn()
            }
        }

        global.document = {
            documentElement: documentElementMock,
            body: bodyMock
        }

        // Mock console methods
        consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => { })

        // Mock setTimeout
        vi.useFakeTimers()

        // Reset mock config to defaults
        config.LightTheme = 'day'
        config.DarkTheme = 'dark'
    })

    afterEach(() => {
        vi.restoreAllMocks()
        vi.useRealTimers()
    })

    describe('Property 3: Theme Palette Application', () => {
        /**
         * **Validates: Requirements 1.3, 1.4, 3.2, 3.3, 10.4, 10.5**
         * 
         * For any theme mode (light or dark) and configuration settings, 
         * the Theme_System should apply the theme palette specified in the 
         * corresponding configuration property (LightTheme or DarkTheme).
         */
        it('should apply correct theme palette based on mode and configuration', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('light', 'dark'), // themeMode
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (themeMode, lightThemeConfig, darkThemeConfig) => {
                        // Update mock configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Clear previous mocks
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()

                        const theme = useTheme()
                        theme.setTheme(themeMode)

                        // Determine expected palette based on mode and configuration
                        const expectedPaletteName = themeMode === 'light' ? lightThemeConfig : darkThemeConfig

                        // Verify data-theme attribute is set correctly (Requirement 1.3, 1.4)
                        expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', expectedPaletteName)

                        // Verify current theme is updated (Requirement 1.3, 1.4)
                        expect(theme.currentTheme.value).toBe(expectedPaletteName)

                        // Verify current mode is set correctly (Requirement 3.2, 3.3)
                        expect(theme.currentMode.value).toBe(themeMode)

                        // Verify isDarkMode computed property (Requirement 3.2, 3.3)
                        expect(theme.isDarkMode.value).toBe(themeMode === 'dark')

                        // Verify theme icon (Requirement 3.2, 3.3)
                        expect(theme.themeIcon.value).toBe(themeMode === 'dark' ? 'moon' : 'sun')

                        // Verify getCurrentThemePalette returns the correct palette name (Requirement 10.4, 10.5)
                        expect(theme.getCurrentThemePalette()).toBe(expectedPaletteName)

                        // Verify CSS variables are being set with correct palette colors
                        expect(documentElementMock.style.setProperty).toHaveBeenCalled()

                        // Verify specific CSS variables are set with expected palette colors
                        const expectedPalette = config.themePalettes[expectedPaletteName]
                        if (expectedPalette && expectedPalette.colors) {
                            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith(
                                '--theme-body-bg',
                                expectedPalette.colors.bodyBackground
                            )
                            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith(
                                '--theme-body-text',
                                expectedPalette.colors.bodyText
                            )
                        }
                    }
                ),
                { numRuns: 20 }
            )
        })

        /**
         * **Validates: Requirements 1.3, 1.4, 10.4, 10.5**
         * 
         * For any configuration change, the system should apply the new
         * theme palette specified in the updated configuration.
         */
        it('should apply theme palette according to configuration changes', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('light', 'dark'), // themeMode
                    fc.constantFrom('day', 'bright'), // initialLightTheme
                    fc.constantFrom('dark', 'night'), // initialDarkTheme
                    fc.constantFrom('day', 'bright'), // newLightTheme
                    fc.constantFrom('dark', 'night'), // newDarkTheme
                    (themeMode, initialLightTheme, initialDarkTheme, newLightTheme, newDarkTheme) => {
                        // Set initial configuration
                        config.LightTheme = initialLightTheme
                        config.DarkTheme = initialDarkTheme

                        const theme = useTheme()
                        theme.setTheme(themeMode)

                        const initialExpectedPalette = themeMode === 'light' ? initialLightTheme : initialDarkTheme
                        expect(theme.currentTheme.value).toBe(initialExpectedPalette)

                        // Change configuration
                        config.LightTheme = newLightTheme
                        config.DarkTheme = newDarkTheme

                        // Clear mocks
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()

                        // Apply theme again with new configuration
                        theme.setTheme(themeMode)

                        const newExpectedPalette = themeMode === 'light' ? newLightTheme : newDarkTheme

                        // Verify new palette is applied
                        expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', newExpectedPalette)
                        expect(theme.currentTheme.value).toBe(newExpectedPalette)
                        expect(theme.getCurrentThemePalette()).toBe(newExpectedPalette)
                    }
                ),
                { numRuns: 15 }
            )
        })

        /**
         * **Validates: Requirements 1.3, 1.4**
         * 
         * For any sequence of theme mode changes, the system should consistently
         * apply the correct palette for each mode.
         */
        it('should maintain consistency across multiple theme mode changes', () => {
            fc.assert(
                fc.property(
                    fc.array(fc.constantFrom('light', 'dark'), { minLength: 1, maxLength: 10 }),
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (modeSequence, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        const theme = useTheme()

                        // Apply each mode in sequence and verify consistency
                        modeSequence.forEach((mode) => {
                            documentElementMock.setAttribute.mockClear()
                            documentElementMock.style.setProperty.mockClear()

                            theme.setTheme(mode)

                            const expectedPaletteName = mode === 'light' ? lightThemeConfig : darkThemeConfig

                            // Verify the correct palette is applied
                            expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', expectedPaletteName)
                            expect(theme.currentTheme.value).toBe(expectedPaletteName)
                            expect(theme.currentMode.value).toBe(mode)
                            expect(theme.isDarkMode.value).toBe(mode === 'dark')
                            expect(theme.themeIcon.value).toBe(mode === 'dark' ? 'moon' : 'sun')

                            // Verify CSS variables are being set
                            expect(documentElementMock.style.setProperty).toHaveBeenCalled()
                        })
                    }
                ),
                { numRuns: 15 }
            )
        })

        /**
         * **Validates: Requirements 3.1, 3.2, 3.3**
         * 
         * For any number of theme toggles, the system should alternate between
         * light and dark modes correctly, applying the appropriate configured palette.
         */
        it('should toggle themes correctly for any number of toggles', () => {
            fc.assert(
                fc.property(
                    fc.integer({ min: 1, max: 20 }), // number of toggles
                    fc.constantFrom('light', 'dark'), // starting mode
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (numToggles, startingMode, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        const theme = useTheme()

                        // Set initial mode
                        theme.setTheme(startingMode)
                        let expectedMode = startingMode

                        // Perform toggles and verify each one
                        for (let i = 0; i < numToggles; i++) {
                            documentElementMock.setAttribute.mockClear()
                            documentElementMock.style.setProperty.mockClear()

                            theme.toggleTheme()
                            expectedMode = expectedMode === 'light' ? 'dark' : 'light'
                            const expectedPalette = expectedMode === 'light' ? lightThemeConfig : darkThemeConfig

                            // Verify the toggle worked correctly
                            expect(theme.currentMode.value).toBe(expectedMode)
                            expect(theme.currentTheme.value).toBe(expectedPalette)
                            expect(theme.isDarkMode.value).toBe(expectedMode === 'dark')
                            expect(theme.themeIcon.value).toBe(expectedMode === 'dark' ? 'moon' : 'sun')
                            expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', expectedPalette)
                        }
                    }
                ),
                { numRuns: 15 }
            )
        })

        /**
         * **Validates: Requirements 1.3, 1.4**
         * 
         * For any invalid theme mode input, the system should reject it
         * and maintain the current valid state.
         */
        it('should handle invalid theme modes gracefully', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('light', 'dark'), // valid starting mode
                    fc.string().filter(s => s !== 'light' && s !== 'dark' && s.length > 0), // invalid mode
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (validMode, invalidMode, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        const theme = useTheme()

                        // Set valid initial mode
                        theme.setTheme(validMode)
                        const initialMode = theme.currentMode.value
                        const initialTheme = theme.currentTheme.value

                        // Clear mocks
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()
                        consoleWarnSpy.mockClear()

                        // Try to set invalid mode
                        theme.setTheme(invalidMode)

                        // Verify state hasn't changed
                        expect(theme.currentMode.value).toBe(initialMode)
                        expect(theme.currentTheme.value).toBe(initialTheme)

                        // Verify warning was logged
                        expect(consoleWarnSpy).toHaveBeenCalledWith(
                            `Invalid theme mode: ${invalidMode}. Must be 'light' or 'dark'`
                        )

                        // Verify no DOM changes were made
                        expect(documentElementMock.setAttribute).not.toHaveBeenCalled()
                        expect(documentElementMock.style.setProperty).not.toHaveBeenCalled()
                    }
                ),
                { numRuns: 15 }
            )
        })

        /**
         * **Validates: Requirements 10.4, 10.5**
         * 
         * For any missing or invalid theme palette configuration, the system
         * should fallback gracefully and still apply a valid theme.
         */
        it('should handle missing theme palette configurations gracefully', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('light', 'dark'), // themeMode
                    fc.constantFrom('nonexistent1', 'nonexistent2', 'invalid'), // invalidPaletteName
                    (themeMode, invalidPaletteName) => {
                        // Set invalid configuration
                        if (themeMode === 'light') {
                            config.LightTheme = invalidPaletteName
                            config.DarkTheme = 'dark' // Keep dark valid
                        } else {
                            config.LightTheme = 'day' // Keep light valid
                            config.DarkTheme = invalidPaletteName
                        }

                        // Clear mocks
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()
                        consoleWarnSpy.mockClear()

                        const theme = useTheme()
                        theme.setTheme(themeMode)

                        // System should still function, falling back to available palette
                        expect(theme.currentMode.value).toBe(themeMode)
                        expect(theme.isDarkMode.value).toBe(themeMode === 'dark')

                        // Should have logged a warning about missing palette
                        expect(consoleWarnSpy).toHaveBeenCalledWith(
                            expect.stringContaining(`Theme palette '${invalidPaletteName}' not found`)
                        )

                        // Should still set data-theme attribute (even if fallback)
                        expect(documentElementMock.setAttribute).toHaveBeenCalled()
                    }
                ),
                { numRuns: 10 }
            )
        })

        /**
         * **Validates: Requirements 1.3, 1.4, 3.2, 3.3**
         * 
         * For any valid theme palette, all expected CSS variables should be
         * applied when the palette is activated.
         */
        it('should apply all CSS variables from theme palette', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('light', 'dark'), // themeMode
                    (themeMode) => {
                        const theme = useTheme()

                        // Clear mocks
                        documentElementMock.style.setProperty.mockClear()

                        theme.setTheme(themeMode)

                        const expectedPaletteName = themeMode === 'light' ? config.LightTheme : config.DarkTheme
                        const expectedPalette = config.themePalettes[expectedPaletteName]

                        if (expectedPalette && expectedPalette.colors) {
                            // Verify core CSS variables are set
                            const coreVariables = [
                                ['--theme-body-bg', expectedPalette.colors.bodyBackground],
                                ['--theme-body-text', expectedPalette.colors.bodyText],
                                ['--theme-panel-bg', expectedPalette.colors.panelBackground],
                                ['--theme-link-color', expectedPalette.colors.linkColor],
                                ['--theme-primary', expectedPalette.colors.primary]
                            ]

                            coreVariables.forEach(([cssVar, expectedValue]) => {
                                if (expectedValue) {
                                    expect(documentElementMock.style.setProperty).toHaveBeenCalledWith(cssVar, expectedValue)
                                }
                            })
                        }

                        // Verify minimum number of CSS variables were set
                        expect(documentElementMock.style.setProperty.mock.calls.length).toBeGreaterThan(5)
                    }
                ),
                { numRuns: 20 }
            )
        })
    })

    describe('Property 11: Theme Persistence Round Trip', () => {
        /**
         * **Validates: Requirements 5.1, 5.2, 5.3**
         * 
         * For any theme mode selection, the preference should be saved to localStorage,
         * and when the application reloads, the same theme mode and corresponding palette
         * should be restored.
         */
        it('should persist and restore theme mode across application reloads', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('light', 'dark'), // themeMode
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (themeMode, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock localStorage
                        const localStorageMock = {
                            getItem: vi.fn(),
                            setItem: vi.fn(),
                            removeItem: vi.fn()
                        }
                        global.localStorage = localStorageMock

                        // Clear previous mocks
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()

                        // Phase 1: Save theme preference
                        const theme1 = useTheme()
                        theme1.setTheme(themeMode)

                        // Verify theme was saved to localStorage (Requirement 5.1)
                        expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', themeMode)

                        // Verify theme was applied correctly
                        const expectedPalette = themeMode === 'light' ? lightThemeConfig : darkThemeConfig
                        expect(theme1.currentMode.value).toBe(themeMode)
                        expect(theme1.currentTheme.value).toBe(expectedPalette)

                        // Phase 2: Simulate application reload
                        // Mock localStorage to return the saved value
                        localStorageMock.getItem.mockReturnValue(themeMode)

                        // Clear mocks to verify new application
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()

                        // Create new theme instance (simulating reload)
                        const theme2 = useTheme()
                        theme2.initializeTheme()

                        // Verify theme was loaded from localStorage (Requirement 5.2)
                        expect(localStorageMock.getItem).toHaveBeenCalledWith('theme-mode')

                        // Verify the same theme mode was restored (Requirement 5.2)
                        expect(theme2.currentMode.value).toBe(themeMode)

                        // Verify the same theme palette was restored (Requirement 5.3)
                        expect(theme2.currentTheme.value).toBe(expectedPalette)

                        // Verify data-theme attribute was set correctly (Requirement 5.3)
                        expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', expectedPalette)

                        // Verify CSS variables were applied (Requirement 5.3)
                        expect(documentElementMock.style.setProperty).toHaveBeenCalled()

                        // Verify the palette colors match
                        const palette = config.themePalettes[expectedPalette]
                        if (palette && palette.colors) {
                            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith(
                                '--theme-body-bg',
                                palette.colors.bodyBackground
                            )
                            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith(
                                '--theme-body-text',
                                palette.colors.bodyText
                            )
                        }

                        // Verify isSystemTheme is false after loading saved preference
                        expect(theme2.isSystemTheme.value).toBe(false)
                    }
                ),
                { numRuns: 20 }
            )
        })

        /**
         * **Validates: Requirements 5.1, 5.2, 5.3**
         * 
         * For any sequence of theme changes, each change should be persisted
         * and the final state should be correctly restored on reload.
         */
        it('should persist the most recent theme mode after multiple changes', () => {
            fc.assert(
                fc.property(
                    fc.array(fc.constantFrom('light', 'dark'), { minLength: 2, maxLength: 10 }),
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (modeSequence, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock localStorage
                        const localStorageMock = {
                            getItem: vi.fn(),
                            setItem: vi.fn(),
                            removeItem: vi.fn()
                        }
                        global.localStorage = localStorageMock

                        const theme = useTheme()

                        // Apply each theme mode in sequence
                        modeSequence.forEach((mode) => {
                            localStorageMock.setItem.mockClear()
                            theme.setTheme(mode)

                            // Verify each change is saved
                            expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', mode)
                        })

                        // Get the final mode
                        const finalMode = modeSequence[modeSequence.length - 1]
                        const finalPalette = finalMode === 'light' ? lightThemeConfig : darkThemeConfig

                        // Simulate reload
                        localStorageMock.getItem.mockReturnValue(finalMode)
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()

                        const theme2 = useTheme()
                        theme2.initializeTheme()

                        // Verify the final state is restored
                        expect(theme2.currentMode.value).toBe(finalMode)
                        expect(theme2.currentTheme.value).toBe(finalPalette)
                        expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', finalPalette)
                    }
                ),
                { numRuns: 15 }
            )
        })

        /**
         * **Validates: Requirements 5.1, 5.2, 5.3**
         * 
         * For any theme toggle operations, the final toggled state should be
         * persisted and restored correctly.
         */
        it('should persist theme mode after toggle operations', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('light', 'dark'), // startingMode
                    fc.integer({ min: 1, max: 10 }), // numberOfToggles
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (startingMode, numberOfToggles, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock localStorage
                        const localStorageMock = {
                            getItem: vi.fn(),
                            setItem: vi.fn(),
                            removeItem: vi.fn()
                        }
                        global.localStorage = localStorageMock

                        const theme = useTheme()
                        theme.setTheme(startingMode)

                        // Perform toggles
                        let expectedMode = startingMode
                        for (let i = 0; i < numberOfToggles; i++) {
                            localStorageMock.setItem.mockClear()
                            theme.toggleTheme()
                            expectedMode = expectedMode === 'light' ? 'dark' : 'light'

                            // Verify each toggle is saved
                            expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', expectedMode)
                        }

                        const expectedPalette = expectedMode === 'light' ? lightThemeConfig : darkThemeConfig

                        // Simulate reload
                        localStorageMock.getItem.mockReturnValue(expectedMode)
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()

                        const theme2 = useTheme()
                        theme2.initializeTheme()

                        // Verify the final toggled state is restored
                        expect(theme2.currentMode.value).toBe(expectedMode)
                        expect(theme2.currentTheme.value).toBe(expectedPalette)
                        expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', expectedPalette)
                    }
                ),
                { numRuns: 15 }
            )
        })

        /**
         * **Validates: Requirements 5.1, 5.2, 5.3**
         * 
         * For any theme mode and configuration combination, the round trip
         * should preserve both the mode and the correct palette mapping.
         */
        it('should preserve theme mode and palette mapping through round trip', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('light', 'dark'), // themeMode
                    fc.record({
                        light: fc.constantFrom('day', 'bright'),
                        dark: fc.constantFrom('dark', 'night')
                    }), // themeConfigs
                    (themeMode, themeConfigs) => {
                        // Set configuration
                        config.LightTheme = themeConfigs.light
                        config.DarkTheme = themeConfigs.dark

                        // Mock localStorage
                        const localStorageMock = {
                            getItem: vi.fn(),
                            setItem: vi.fn(),
                            removeItem: vi.fn()
                        }
                        global.localStorage = localStorageMock

                        // Phase 1: Save
                        const theme1 = useTheme()
                        theme1.setTheme(themeMode)

                        const expectedPalette = themeMode === 'light' ? themeConfigs.light : themeConfigs.dark

                        // Verify save
                        expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', themeMode)
                        expect(theme1.currentTheme.value).toBe(expectedPalette)

                        // Phase 2: Reload and restore
                        localStorageMock.getItem.mockReturnValue(themeMode)
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()

                        const theme2 = useTheme()
                        theme2.initializeTheme()

                        // Verify restore
                        expect(theme2.currentMode.value).toBe(themeMode)
                        expect(theme2.currentTheme.value).toBe(expectedPalette)

                        // Verify the palette mapping is correct
                        expect(theme2.getCurrentThemePalette()).toBe(expectedPalette)

                        // Verify CSS variables match the expected palette
                        const palette = config.themePalettes[expectedPalette]
                        if (palette && palette.colors) {
                            // Check a few key CSS variables
                            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith(
                                '--theme-body-bg',
                                palette.colors.bodyBackground
                            )
                            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith(
                                '--theme-panel-bg',
                                palette.colors.panelBackground
                            )
                            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith(
                                '--theme-link-color',
                                palette.colors.linkColor
                            )
                        }
                    }
                ),
                { numRuns: 20 }
            )
        })

        /**
         * **Validates: Requirements 5.1, 5.2, 5.3**
         * 
         * For any valid theme mode, the round trip should work correctly
         * even when configuration changes between save and load.
         */
        it('should handle configuration changes between save and reload', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('light', 'dark'), // themeMode
                    fc.constantFrom('day', 'bright'), // initialLightTheme
                    fc.constantFrom('dark', 'night'), // initialDarkTheme
                    fc.constantFrom('day', 'bright'), // newLightTheme
                    fc.constantFrom('dark', 'night'), // newDarkTheme
                    (themeMode, initialLightTheme, initialDarkTheme, newLightTheme, newDarkTheme) => {
                        // Mock localStorage
                        const localStorageMock = {
                            getItem: vi.fn(),
                            setItem: vi.fn(),
                            removeItem: vi.fn()
                        }
                        global.localStorage = localStorageMock

                        // Phase 1: Save with initial configuration
                        config.LightTheme = initialLightTheme
                        config.DarkTheme = initialDarkTheme

                        const theme1 = useTheme()
                        theme1.setTheme(themeMode)

                        expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', themeMode)

                        // Phase 2: Change configuration and reload
                        config.LightTheme = newLightTheme
                        config.DarkTheme = newDarkTheme

                        localStorageMock.getItem.mockReturnValue(themeMode)
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()

                        const theme2 = useTheme()
                        theme2.initializeTheme()

                        // Verify mode is restored
                        expect(theme2.currentMode.value).toBe(themeMode)

                        // Verify new configuration is applied
                        const expectedNewPalette = themeMode === 'light' ? newLightTheme : newDarkTheme
                        expect(theme2.currentTheme.value).toBe(expectedNewPalette)
                        expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', expectedNewPalette)

                        // Verify CSS variables match the new palette
                        const newPalette = config.themePalettes[expectedNewPalette]
                        if (newPalette && newPalette.colors) {
                            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith(
                                '--theme-body-bg',
                                newPalette.colors.bodyBackground
                            )
                        }
                    }
                ),
                { numRuns: 15 }
            )
        })

        /**
         * **Validates: Requirements 5.1, 5.2**
         * 
         * For any theme mode, when savePreference is false, the theme should
         * not be persisted and reload should not restore it.
         */
        it('should not persist theme when savePreference is false', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('light', 'dark'), // themeMode
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (themeMode, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock localStorage
                        const localStorageMock = {
                            getItem: vi.fn().mockReturnValue(null),
                            setItem: vi.fn(),
                            removeItem: vi.fn()
                        }
                        global.localStorage = localStorageMock

                        // Mock matchMedia for system theme detection
                        global.window.matchMedia = vi.fn().mockReturnValue({
                            matches: false, // System prefers light
                            media: '(prefers-color-scheme: dark)',
                            addEventListener: vi.fn(),
                            removeEventListener: vi.fn()
                        })

                        const theme = useTheme()

                        // Set theme without saving preference
                        theme.setTheme(themeMode, false)

                        // Verify theme was NOT saved to localStorage
                        expect(localStorageMock.setItem).not.toHaveBeenCalled()

                        // Verify theme was applied
                        expect(theme.currentMode.value).toBe(themeMode)

                        // Simulate reload
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()

                        const theme2 = useTheme()
                        theme2.initializeTheme()

                        // Verify system theme is used (not the unsaved preference)
                        expect(theme2.currentMode.value).toBe('light') // System default
                        expect(theme2.isSystemTheme.value).toBe(true)
                    }
                ),
                { numRuns: 15 }
            )
        })
    })
})