// src/composables/useTheme.test.js - Unit Tests for Theme Manager Composable
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { nextTick } from 'vue'
import { useTheme } from './useTheme.js'

// Mock config
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
                    linkColor: '#667eea',
                    linkHover: '#764ba2',
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
                    linkColor: '#a78bfa',
                    linkHover: '#c084fc',
                    primary: '#a78bfa',
                    secondary: '#c084fc',
                    accent: '#f093fb',
                    success: '#34d399',
                    warning: '#fbbf24',
                    error: '#f87171',
                    info: '#60a5fa'
                }
            }
        }
    }
}))

describe('useTheme Composable', () => {
    let documentElementMock
    let bodyMock
    let consoleLogSpy
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
        consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => { })
        consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => { })

        // Mock setTimeout
        vi.useFakeTimers()
    })

    afterEach(() => {
        vi.restoreAllMocks()
        vi.useRealTimers()
    })

    describe('Basic Functionality', () => {
        it('should initialize with default light mode', () => {
            const theme = useTheme()

            expect(theme.currentMode.value).toBe('light')
            expect(theme.isDarkMode.value).toBe(false)
            expect(theme.themeIcon.value).toBe('sun')
        })

        it('should toggle between light and dark modes', () => {
            const theme = useTheme()

            // Start in light mode
            expect(theme.currentMode.value).toBe('light')
            expect(theme.isDarkMode.value).toBe(false)

            // Toggle to dark mode
            theme.toggleTheme()
            expect(theme.currentMode.value).toBe('dark')
            expect(theme.isDarkMode.value).toBe(true)
            expect(theme.themeIcon.value).toBe('moon')

            // Toggle back to light mode
            theme.toggleTheme()
            expect(theme.currentMode.value).toBe('light')
            expect(theme.isDarkMode.value).toBe(false)
            expect(theme.themeIcon.value).toBe('sun')
        })

        it('should set theme mode correctly', () => {
            const theme = useTheme()

            theme.setTheme('dark')
            expect(theme.currentMode.value).toBe('dark')
            expect(theme.isDarkMode.value).toBe(true)

            theme.setTheme('light')
            expect(theme.currentMode.value).toBe('light')
            expect(theme.isDarkMode.value).toBe(false)
        })

        it('should warn on invalid theme mode', () => {
            const theme = useTheme()

            theme.setTheme('invalid')
            expect(consoleWarnSpy).toHaveBeenCalledWith("Invalid theme mode: invalid. Must be 'light' or 'dark'")
            expect(theme.currentMode.value).toBe('light') // Should remain unchanged
        })
    })

    describe('Theme Palette Application', () => {
        it('should apply theme palette to CSS variables', () => {
            const theme = useTheme()

            theme.setTheme('dark')

            // Check that data-theme attribute is set
            expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', 'dark')

            // Check that CSS variables are set
            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith('--theme-body-bg', '#121212')
            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith('--theme-body-text', '#e0e0e0')
            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith('--theme-panel-bg', '#1e1e1e')
            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith('--theme-link-color', '#a78bfa')
        })

        it('should get correct theme palette for current mode', () => {
            const theme = useTheme()

            // Reset to light mode first
            theme.setTheme('light')
            expect(theme.getCurrentThemePalette()).toBe('day')

            // Dark mode should use dark theme
            theme.setTheme('dark')
            expect(theme.getCurrentThemePalette()).toBe('dark')
        })

        it('should handle missing theme palette gracefully', () => {
            const theme = useTheme()

            const palette = theme.getThemePalette('nonexistent')
            expect(consoleWarnSpy).toHaveBeenCalledWith("Theme palette 'nonexistent' not found, falling back to 'day'")
            // Should return the day palette as fallback
            expect(palette.name).toBe('day')
        })
    })

    describe('System Theme Detection', () => {
        it('should detect system dark theme preference', () => {
            // Mock system dark theme preference
            window.matchMedia.mockReturnValue({
                matches: true,
                media: '(prefers-color-scheme: dark)',
                addEventListener: vi.fn(),
                removeEventListener: vi.fn()
            })

            const theme = useTheme()
            const systemTheme = theme.detectSystemTheme()

            expect(systemTheme).toBe('dark')
        })

        it('should detect system light theme preference', () => {
            // Mock system light theme preference
            window.matchMedia.mockReturnValue({
                matches: false,
                media: '(prefers-color-scheme: dark)',
                addEventListener: vi.fn(),
                removeEventListener: vi.fn()
            })

            const theme = useTheme()
            const systemTheme = theme.detectSystemTheme()

            expect(systemTheme).toBe('light')
        })

        it('should fallback to light theme when system detection fails', () => {
            // Mock matchMedia to throw error
            window.matchMedia.mockImplementation(() => {
                throw new Error('matchMedia not supported')
            })

            const theme = useTheme()
            const systemTheme = theme.detectSystemTheme()

            expect(systemTheme).toBe('light')
            expect(consoleWarnSpy).toHaveBeenCalledWith('System theme detection failed:', expect.any(Error))
        })
    })

    describe('Theme Persistence', () => {
        it('should save theme preference to localStorage', () => {
            const theme = useTheme()

            theme.setTheme('dark')

            expect(localStorage.setItem).toHaveBeenCalledWith('theme-mode', 'dark')
            expect(theme.isSystemTheme.value).toBe(false)
        })

        it('should not save preference when savePreference is false', () => {
            const theme = useTheme()

            theme.setTheme('dark', false)

            expect(localStorage.setItem).not.toHaveBeenCalled()
        })

        it('should handle localStorage save errors gracefully', () => {
            localStorage.setItem.mockImplementation(() => {
                throw new Error('localStorage not available')
            })

            const theme = useTheme()
            theme.setTheme('dark')

            expect(consoleWarnSpy).toHaveBeenCalledWith('Failed to save theme preference:', expect.any(Error))
        })

        it('should load theme preference from localStorage', () => {
            localStorage.getItem.mockReturnValue('dark')

            const theme = useTheme()
            const savedMode = theme.loadThemePreference()

            expect(savedMode).toBe('dark')
            expect(localStorage.getItem).toHaveBeenCalledWith('theme-mode')
        })

        it('should handle localStorage load errors gracefully', () => {
            localStorage.getItem.mockImplementation(() => {
                throw new Error('localStorage not available')
            })

            const theme = useTheme()
            const savedMode = theme.loadThemePreference()

            expect(savedMode).toBe(null)
            expect(consoleWarnSpy).toHaveBeenCalledWith('Failed to load theme preference:', expect.any(Error))
        })
    })

    describe('Theme Initialization', () => {
        it('should initialize with saved preference', () => {
            localStorage.getItem.mockReturnValue('dark')

            const theme = useTheme()
            theme.initializeTheme()

            expect(theme.currentMode.value).toBe('dark')
            expect(theme.isSystemTheme.value).toBe(false)
            expect(bodyMock.classList.add).toHaveBeenCalledWith('no-transitions')
        })

        it('should initialize with system preference when no saved preference', () => {
            localStorage.getItem.mockReturnValue(null)
            window.matchMedia.mockReturnValue({
                matches: true,
                media: '(prefers-color-scheme: dark)',
                addEventListener: vi.fn(),
                removeEventListener: vi.fn()
            })

            const theme = useTheme()
            theme.initializeTheme()

            expect(theme.currentMode.value).toBe('dark')
            expect(theme.isSystemTheme.value).toBe(true)
        })

        it('should enable transitions after delay', () => {
            const theme = useTheme()
            theme.initializeTheme()

            // Initially transitions should be disabled
            expect(bodyMock.classList.add).toHaveBeenCalledWith('no-transitions')

            // Fast-forward time
            vi.advanceTimersByTime(100)

            // Transitions should be enabled
            expect(bodyMock.classList.remove).toHaveBeenCalledWith('no-transitions')
        })
    })

    describe('Reset to System Theme', () => {
        it('should reset to system theme and clear localStorage', () => {
            window.matchMedia.mockReturnValue({
                matches: true,
                media: '(prefers-color-scheme: dark)',
                addEventListener: vi.fn(),
                removeEventListener: vi.fn()
            })

            const theme = useTheme()
            theme.resetToSystemTheme()

            expect(theme.currentMode.value).toBe('dark')
            expect(theme.isSystemTheme.value).toBe(true)
            expect(localStorage.removeItem).toHaveBeenCalledWith('theme-mode')
        })

        it('should handle localStorage clear errors gracefully', () => {
            localStorage.removeItem.mockImplementation(() => {
                throw new Error('localStorage not available')
            })

            const theme = useTheme()
            theme.resetToSystemTheme()

            expect(consoleWarnSpy).toHaveBeenCalledWith('Failed to clear theme preference:', expect.any(Error))
        })
    })

    describe('Theme Configuration Validation', () => {
        it('should validate theme configuration successfully', () => {
            const theme = useTheme()
            const isValid = theme.validateThemeConfig()

            expect(isValid).toBe(true)
        })
    })
})