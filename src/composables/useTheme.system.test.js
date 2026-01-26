// src/composables/useTheme.system.test.js - Property-Based Tests for System Theme Detection
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

describe('useTheme System Detection Property-Based Tests', () => {
    let documentElementMock
    let bodyMock
    let consoleLogSpy
    let consoleWarnSpy
    let matchMediaMock

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
        consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => { })
        consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => { })

        // Mock setTimeout
        vi.useFakeTimers()

        // Mock localStorage
        global.localStorage = {
            getItem: vi.fn(),
            setItem: vi.fn(),
            removeItem: vi.fn(),
            clear: vi.fn()
        }

        // Mock matchMedia
        matchMediaMock = {
            matches: false,
            media: '(prefers-color-scheme: dark)',
            addEventListener: vi.fn(),
            removeEventListener: vi.fn()
        }
        global.window = {
            matchMedia: vi.fn(() => matchMediaMock)
        }

        // Reset mock config to defaults
        config.LightTheme = 'day'
        config.DarkTheme = 'dark'
        config.enableSystemDetection = true
    })

    afterEach(() => {
        vi.restoreAllMocks()
        vi.useRealTimers()
    })

    describe('Property 18: System Theme Detection', () => {
        /**
         * **Validates: Requirements 9.1, 9.2, 9.3, 9.4**
         * 
         * For any system color scheme preference (light or dark), when no user preference exists, 
         * the Theme_System should detect and apply the corresponding theme mode with the 
         * appropriate configured palette.
         */
        it('should detect and apply system theme preference when no user preference exists', () => {
            fc.assert(
                fc.property(
                    fc.boolean(), // systemPrefersDark
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (systemPrefersDark, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock system preference
                        matchMediaMock.matches = systemPrefersDark
                        global.window.matchMedia.mockReturnValue(matchMediaMock)

                        // Mock no user preference in localStorage
                        global.localStorage.getItem.mockReturnValue(null)

                        // Clear mocks
                        documentElementMock.setAttribute.mockClear()
                        documentElementMock.style.setProperty.mockClear()
                        consoleLogSpy.mockClear()

                        const theme = useTheme()
                        theme.initializeTheme()

                        const expectedMode = systemPrefersDark ? 'dark' : 'light'
                        const expectedPalette = systemPrefersDark ? darkThemeConfig : lightThemeConfig

                        // Verify system theme detection (Requirements 9.1, 9.2)
                        expect(theme.currentMode.value).toBe(expectedMode)
                        expect(theme.isSystemTheme.value).toBe(true)

                        // Verify correct palette application (Requirements 9.3, 9.4)
                        expect(theme.currentTheme.value).toBe(expectedPalette)
                        expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', expectedPalette)

                        // Verify theme mode properties
                        expect(theme.isDarkMode.value).toBe(systemPrefersDark)
                        expect(theme.themeIcon.value).toBe(systemPrefersDark ? 'moon' : 'sun')

                        // Verify CSS variables are applied
                        expect(documentElementMock.style.setProperty).toHaveBeenCalled()

                        // Verify system detection was used
                        expect(global.window.matchMedia).toHaveBeenCalledWith('(prefers-color-scheme: dark)')

                        // Verify appropriate log message
                        expect(consoleLogSpy).toHaveBeenCalledWith(`Using system theme: ${expectedMode}`)
                    }
                ),
                { numRuns: 20 }
            )
        })

        /**
         * **Validates: Requirements 9.1, 9.2**
         * 
         * For any system detection configuration, the system should use CSS media query
         * `prefers-color-scheme` to determine initial theme mode when enabled.
         */
        it('should use prefers-color-scheme media query for initial theme detection', () => {
            fc.assert(
                fc.property(
                    fc.boolean(), // systemPrefersDark
                    fc.boolean(), // enableSystemDetection
                    (systemPrefersDark, enableSystemDetection) => {
                        // Set system detection configuration
                        config.enableSystemDetection = enableSystemDetection

                        // Mock system preference
                        matchMediaMock.matches = systemPrefersDark
                        global.window.matchMedia.mockReturnValue(matchMediaMock)

                        // Mock no user preference
                        global.localStorage.getItem.mockReturnValue(null)

                        const theme = useTheme()
                        const detectedTheme = theme.detectSystemTheme()

                        if (enableSystemDetection) {
                            // Should use media query when enabled
                            expect(global.window.matchMedia).toHaveBeenCalledWith('(prefers-color-scheme: dark)')
                            expect(detectedTheme).toBe(systemPrefersDark ? 'dark' : 'light')
                        } else {
                            // Should fallback to light when disabled
                            expect(detectedTheme).toBe('light')
                        }
                    }
                ),
                { numRuns: 15 }
            )
        })

        /**
         * **Validates: Requirements 9.3, 9.4**
         * 
         * For any theme configuration, when system prefers dark/light, the system should
         * apply the corresponding configured theme palette.
         */
        it('should apply correct configured palette based on system preference', () => {
            fc.assert(
                fc.property(
                    fc.boolean(), // systemPrefersDark
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (systemPrefersDark, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock system preference
                        matchMediaMock.matches = systemPrefersDark
                        global.window.matchMedia.mockReturnValue(matchMediaMock)

                        // Mock no user preference
                        global.localStorage.getItem.mockReturnValue(null)

                        // Clear mocks
                        documentElementMock.setAttribute.mockClear()

                        const theme = useTheme()
                        theme.initializeTheme()

                        if (systemPrefersDark) {
                            // When system prefers dark, should use DarkTheme palette (Requirement 9.3)
                            expect(theme.currentMode.value).toBe('dark')
                            expect(theme.currentTheme.value).toBe(darkThemeConfig)
                            expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', darkThemeConfig)
                        } else {
                            // When system prefers light, should use LightTheme palette (Requirement 9.4)
                            expect(theme.currentMode.value).toBe('light')
                            expect(theme.currentTheme.value).toBe(lightThemeConfig)
                            expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', lightThemeConfig)
                        }

                        // Verify system theme flag is set
                        expect(theme.isSystemTheme.value).toBe(true)
                    }
                ),
                { numRuns: 20 }
            )
        })

        /**
         * **Validates: Requirements 9.1, 9.2**
         * 
         * For any media query error scenario, the system should gracefully fallback
         * to light theme without crashing.
         */
        it('should handle media query errors gracefully', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock matchMedia to throw error
                        global.window.matchMedia.mockImplementation(() => {
                            throw new Error('matchMedia not supported')
                        })

                        // Mock no user preference
                        global.localStorage.getItem.mockReturnValue(null)

                        // Clear mocks
                        consoleWarnSpy.mockClear()
                        documentElementMock.setAttribute.mockClear()

                        const theme = useTheme()

                        // Should not throw error
                        expect(() => theme.detectSystemTheme()).not.toThrow()
                        expect(() => theme.initializeTheme()).not.toThrow()

                        // Should fallback to light theme
                        expect(theme.currentMode.value).toBe('light')
                        expect(theme.currentTheme.value).toBe(lightThemeConfig)

                        // Should log warning
                        expect(consoleWarnSpy).toHaveBeenCalledWith(
                            'System theme detection failed:',
                            expect.any(Error)
                        )
                    }
                ),
                { numRuns: 10 }
            )
        })

        /**
         * **Validates: Requirements 9.1**
         * 
         * For any combination of system preference and localStorage state,
         * the system should only use system detection when no user preference exists.
         */
        it('should only use system detection when no user preference exists', () => {
            fc.assert(
                fc.property(
                    fc.boolean(), // systemPrefersDark
                    fc.constantFrom('light', 'dark', null), // savedUserPreference
                    (systemPrefersDark, savedUserPreference) => {
                        // Mock system preference
                        matchMediaMock.matches = systemPrefersDark
                        global.window.matchMedia.mockReturnValue(matchMediaMock)

                        // Mock user preference in localStorage
                        global.localStorage.getItem.mockReturnValue(savedUserPreference)

                        // Clear mocks
                        consoleLogSpy.mockClear()

                        const theme = useTheme()
                        theme.initializeTheme()

                        if (savedUserPreference === 'light' || savedUserPreference === 'dark') {
                            // Should use saved preference, not system
                            expect(theme.currentMode.value).toBe(savedUserPreference)
                            expect(theme.isSystemTheme.value).toBe(false)
                            expect(consoleLogSpy).toHaveBeenCalledWith(
                                `Loaded saved theme preference: ${savedUserPreference}`
                            )
                        } else {
                            // Should use system preference when no valid saved preference
                            const expectedMode = systemPrefersDark ? 'dark' : 'light'
                            expect(theme.currentMode.value).toBe(expectedMode)
                            expect(theme.isSystemTheme.value).toBe(true)
                            expect(consoleLogSpy).toHaveBeenCalledWith(
                                `Using system theme: ${expectedMode}`
                            )
                        }
                    }
                ),
                { numRuns: 15 }
            )
        })

        /**
         * **Validates: Requirements 9.2**
         * 
         * For any system theme change event, the system should respond appropriately
         * when listening for system changes.
         */
        it('should listen for system theme changes when using system theme', () => {
            fc.assert(
                fc.property(
                    fc.boolean(), // initialSystemPreference
                    fc.boolean(), // newSystemPreference
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (initialSystemPreference, newSystemPreference, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock initial system preference
                        matchMediaMock.matches = initialSystemPreference
                        global.window.matchMedia.mockReturnValue(matchMediaMock)

                        // Mock no user preference
                        global.localStorage.getItem.mockReturnValue(null)

                        const theme = useTheme()
                        theme.initializeTheme()

                        // Verify initial state
                        const initialMode = initialSystemPreference ? 'dark' : 'light'
                        expect(theme.currentMode.value).toBe(initialMode)
                        expect(theme.isSystemTheme.value).toBe(true)

                        // Verify event listener was added
                        expect(matchMediaMock.addEventListener).toHaveBeenCalledWith(
                            'change',
                            expect.any(Function)
                        )

                        // Simulate system theme change
                        const changeHandler = matchMediaMock.addEventListener.mock.calls[0][1]
                        const mockEvent = { matches: newSystemPreference }

                        // Clear mocks before triggering change
                        documentElementMock.setAttribute.mockClear()
                        consoleLogSpy.mockClear()

                        // Trigger system theme change
                        changeHandler(mockEvent)

                        if (initialSystemPreference !== newSystemPreference) {
                            // Should update to new system preference
                            const newMode = newSystemPreference ? 'dark' : 'light'
                            const newPalette = newSystemPreference ? darkThemeConfig : lightThemeConfig

                            expect(theme.currentMode.value).toBe(newMode)
                            expect(theme.currentTheme.value).toBe(newPalette)
                            expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', newPalette)
                            expect(consoleLogSpy).toHaveBeenCalledWith(`System theme changed to: ${newMode}`)
                        }

                        // Should still be using system theme
                        expect(theme.isSystemTheme.value).toBe(true)
                    }
                ),
                { numRuns: 15 }
            )
        })

        /**
         * **Validates: Requirements 9.1, 9.2**
         * 
         * For browsers that don't support prefers-color-scheme, the system should
         * detect this and fallback gracefully.
         */
        it('should handle unsupported prefers-color-scheme gracefully', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock matchMedia to return 'not all' (unsupported media query)
                        matchMediaMock.media = 'not all'
                        matchMediaMock.matches = false
                        global.window.matchMedia.mockReturnValue(matchMediaMock)

                        // Mock no user preference
                        global.localStorage.getItem.mockReturnValue(null)

                        // Clear mocks
                        consoleWarnSpy.mockClear()
                        documentElementMock.setAttribute.mockClear()

                        const theme = useTheme()

                        // Should detect unsupported media query
                        const detectedTheme = theme.detectSystemTheme()
                        expect(detectedTheme).toBe('light')

                        // Should log warning about unsupported feature
                        expect(consoleWarnSpy).toHaveBeenCalledWith(
                            'prefers-color-scheme not supported, falling back to light theme'
                        )

                        // Initialize should also work
                        theme.initializeTheme()
                        expect(theme.currentMode.value).toBe('light')
                        expect(theme.currentTheme.value).toBe(lightThemeConfig)

                        // Reset media for next test
                        matchMediaMock.media = '(prefers-color-scheme: dark)'
                    }
                ),
                { numRuns: 10 }
            )
        })

        /**
         * **Validates: Requirements 9.1, 9.2**
         * 
         * For browsers without matchMedia support, the system should
         * detect this and fallback gracefully.
         */
        it('should handle missing matchMedia support gracefully', () => {
            fc.assert(
                fc.property(
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock window without matchMedia
                        const originalMatchMedia = global.window.matchMedia
                        global.window.matchMedia = undefined

                        // Mock no user preference
                        global.localStorage.getItem.mockReturnValue(null)

                        // Clear mocks
                        consoleWarnSpy.mockClear()
                        documentElementMock.setAttribute.mockClear()

                        const theme = useTheme()

                        // Should detect missing matchMedia
                        const detectedTheme = theme.detectSystemTheme()
                        expect(detectedTheme).toBe('light')

                        // Should log warning about missing support
                        expect(consoleWarnSpy).toHaveBeenCalledWith(
                            'matchMedia not supported, falling back to light theme'
                        )

                        // Initialize should also work
                        theme.initializeTheme()
                        expect(theme.currentMode.value).toBe('light')
                        expect(theme.currentTheme.value).toBe(lightThemeConfig)

                        // Restore matchMedia for next test
                        global.window.matchMedia = originalMatchMedia
                    }
                ),
                { numRuns: 10 }
            )
        })
    })

    describe('Property 19: User Preference Override', () => {
        /**
         * **Validates: Requirements 9.5**
         * 
         * For any combination of system preference and user preference, the user's manual 
         * theme selection should take precedence over system settings.
         */
        it('should override system preference with user manual selection', () => {
            fc.assert(
                fc.property(
                    fc.boolean(), // systemPrefersDark
                    fc.constantFrom('light', 'dark'), // userSelectedMode
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (systemPrefersDark, userSelectedMode, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock system preference
                        matchMediaMock.matches = systemPrefersDark
                        global.window.matchMedia.mockReturnValue(matchMediaMock)

                        // Mock no initial user preference
                        global.localStorage.getItem.mockReturnValue(null)

                        const theme = useTheme()
                        theme.initializeTheme()

                        // Verify initial system theme is applied
                        const initialSystemMode = systemPrefersDark ? 'dark' : 'light'
                        expect(theme.currentMode.value).toBe(initialSystemMode)
                        expect(theme.isSystemTheme.value).toBe(true)

                        // Clear mocks
                        documentElementMock.setAttribute.mockClear()
                        global.localStorage.setItem.mockClear()

                        // User manually selects theme
                        theme.setTheme(userSelectedMode)

                        const expectedPalette = userSelectedMode === 'light' ? lightThemeConfig : darkThemeConfig

                        // Verify user preference overrides system (Requirement 9.5)
                        expect(theme.currentMode.value).toBe(userSelectedMode)
                        expect(theme.currentTheme.value).toBe(expectedPalette)
                        expect(theme.isSystemTheme.value).toBe(false)

                        // Verify user preference is saved
                        expect(global.localStorage.setItem).toHaveBeenCalledWith('theme-mode', userSelectedMode)

                        // Verify theme is applied
                        expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', expectedPalette)

                        // Simulate system theme change - should be ignored
                        const changeHandler = matchMediaMock.addEventListener.mock.calls[0][1]
                        const mockEvent = { matches: !systemPrefersDark }

                        // Clear mocks
                        documentElementMock.setAttribute.mockClear()

                        // Trigger system change
                        changeHandler(mockEvent)

                        // Should still use user preference, not system change
                        expect(theme.currentMode.value).toBe(userSelectedMode)
                        expect(theme.currentTheme.value).toBe(expectedPalette)
                        expect(theme.isSystemTheme.value).toBe(false)

                        // Should not have applied system change
                        expect(documentElementMock.setAttribute).not.toHaveBeenCalled()
                    }
                ),
                { numRuns: 20 }
            )
        })

        /**
         * **Validates: Requirements 9.5**
         * 
         * For any user preference reset scenario, the system should return to
         * following system preference.
         */
        it('should return to system preference after reset', () => {
            fc.assert(
                fc.property(
                    fc.boolean(), // systemPrefersDark
                    fc.constantFrom('light', 'dark'), // userSelectedMode
                    fc.constantFrom('day', 'bright'), // lightThemeConfig
                    fc.constantFrom('dark', 'night'), // darkThemeConfig
                    (systemPrefersDark, userSelectedMode, lightThemeConfig, darkThemeConfig) => {
                        // Set configuration
                        config.LightTheme = lightThemeConfig
                        config.DarkTheme = darkThemeConfig

                        // Mock system preference
                        matchMediaMock.matches = systemPrefersDark
                        global.window.matchMedia.mockReturnValue(matchMediaMock)

                        // Mock saved user preference
                        global.localStorage.getItem.mockReturnValue(userSelectedMode)

                        const theme = useTheme()
                        theme.initializeTheme()

                        // Verify user preference is loaded
                        expect(theme.currentMode.value).toBe(userSelectedMode)
                        expect(theme.isSystemTheme.value).toBe(false)

                        // Clear mocks
                        documentElementMock.setAttribute.mockClear()
                        global.localStorage.removeItem.mockClear()

                        // Reset to system theme
                        theme.resetToSystemTheme()

                        const expectedSystemMode = systemPrefersDark ? 'dark' : 'light'
                        const expectedSystemPalette = systemPrefersDark ? darkThemeConfig : lightThemeConfig

                        // Should return to system preference (Requirement 9.5)
                        expect(theme.currentMode.value).toBe(expectedSystemMode)
                        expect(theme.currentTheme.value).toBe(expectedSystemPalette)
                        expect(theme.isSystemTheme.value).toBe(true)

                        // Should clear saved preference
                        expect(global.localStorage.removeItem).toHaveBeenCalledWith('theme-mode')

                        // Should apply system theme
                        expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', expectedSystemPalette)

                        // Should now respond to system changes again
                        const changeHandler = matchMediaMock.addEventListener.mock.calls[0][1]
                        const mockEvent = { matches: !systemPrefersDark }

                        // Clear mocks
                        documentElementMock.setAttribute.mockClear()

                        // Trigger system change
                        changeHandler(mockEvent)

                        const newSystemMode = !systemPrefersDark ? 'dark' : 'light'
                        const newSystemPalette = !systemPrefersDark ? darkThemeConfig : lightThemeConfig

                        // Should respond to system change
                        expect(theme.currentMode.value).toBe(newSystemMode)
                        expect(theme.currentTheme.value).toBe(newSystemPalette)
                        expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', newSystemPalette)
                    }
                ),
                { numRuns: 15 }
            )
        })
    })
})