// src/composables/useTheme.persistence.test.js - Comprehensive localStorage Persistence Tests
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
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

describe('useTheme localStorage Persistence Tests', () => {
    let documentElementMock
    let bodyMock
    let consoleLogSpy
    let consoleWarnSpy
    let localStorageMock

    beforeEach(() => {
        // Mock localStorage
        localStorageMock = {
            getItem: vi.fn(),
            setItem: vi.fn(),
            removeItem: vi.fn(),
            clear: vi.fn()
        }
        global.localStorage = localStorageMock

        // Mock matchMedia
        global.window.matchMedia = vi.fn().mockReturnValue({
            matches: false,
            media: '(prefers-color-scheme: dark)',
            addEventListener: vi.fn(),
            removeEventListener: vi.fn()
        })

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

    describe('Requirement 5.1: Save theme mode preference to localStorage', () => {
        it('should save light mode preference when switching to light', () => {
            const theme = useTheme()

            theme.setTheme('light')

            expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', 'light')
            expect(theme.isSystemTheme.value).toBe(false)
        })

        it('should save dark mode preference when switching to dark', () => {
            const theme = useTheme()

            theme.setTheme('dark')

            expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', 'dark')
            expect(theme.isSystemTheme.value).toBe(false)
        })

        it('should save preference when toggling themes', () => {
            const theme = useTheme()

            // Start in light mode
            theme.setTheme('light')
            expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', 'light')

            // Toggle to dark
            theme.toggleTheme()
            expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', 'dark')

            // Toggle back to light
            theme.toggleTheme()
            expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', 'light')
        })

        it('should not save preference when savePreference is false', () => {
            const theme = useTheme()

            theme.setTheme('dark', false)

            expect(localStorageMock.setItem).not.toHaveBeenCalled()
            // Note: isSystemTheme is only set to false when savePreference is true
        })

        it('should overwrite existing preference when switching modes', () => {
            localStorageMock.setItem('theme-mode', 'light')
            const theme = useTheme()

            theme.setTheme('dark')

            expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', 'dark')
        })
    })

    describe('Requirement 5.2: Restore previously selected theme mode on load', () => {
        it('should restore light mode from localStorage', () => {
            localStorageMock.getItem.mockReturnValue('light')

            const theme = useTheme()
            theme.initializeTheme()

            expect(theme.currentMode.value).toBe('light')
            expect(theme.isSystemTheme.value).toBe(false)
            expect(consoleLogSpy).toHaveBeenCalledWith('Loaded saved theme preference: light')
        })

        it('should restore dark mode from localStorage', () => {
            localStorageMock.getItem.mockReturnValue('dark')

            const theme = useTheme()
            theme.initializeTheme()

            expect(theme.currentMode.value).toBe('dark')
            expect(theme.isSystemTheme.value).toBe(false)
            expect(consoleLogSpy).toHaveBeenCalledWith('Loaded saved theme preference: dark')
        })

        it('should ignore invalid saved preferences', () => {
            localStorageMock.getItem.mockReturnValue('invalid-mode')
            window.matchMedia.mockReturnValue({
                matches: false,
                media: '(prefers-color-scheme: dark)',
                addEventListener: vi.fn(),
                removeEventListener: vi.fn()
            })

            const theme = useTheme()
            theme.initializeTheme()

            // Should fall back to system theme (light in this case)
            expect(theme.currentMode.value).toBe('light')
            expect(theme.isSystemTheme.value).toBe(true)
        })

        it('should handle null localStorage value', () => {
            localStorageMock.getItem.mockReturnValue(null)
            window.matchMedia.mockReturnValue({
                matches: true,
                media: '(prefers-color-scheme: dark)',
                addEventListener: vi.fn(),
                removeEventListener: vi.fn()
            })

            const theme = useTheme()
            theme.initializeTheme()

            // Should use system theme (dark in this case)
            expect(theme.currentMode.value).toBe('dark')
            expect(theme.isSystemTheme.value).toBe(true)
        })
    })

    describe('Requirement 5.3: Apply appropriate theme palette based on restored mode', () => {
        it('should apply day palette when restoring light mode', () => {
            localStorageMock.getItem.mockReturnValue('light')

            const theme = useTheme()
            theme.initializeTheme()

            expect(theme.currentMode.value).toBe('light')
            expect(theme.currentTheme.value).toBe('day')
            expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', 'day')
        })

        it('should apply dark palette when restoring dark mode', () => {
            localStorageMock.getItem.mockReturnValue('dark')

            const theme = useTheme()
            theme.initializeTheme()

            expect(theme.currentMode.value).toBe('dark')
            expect(theme.currentTheme.value).toBe('dark')
            expect(documentElementMock.setAttribute).toHaveBeenCalledWith('data-theme', 'dark')
        })

        it('should apply CSS variables for restored theme', () => {
            localStorageMock.getItem.mockReturnValue('dark')

            const theme = useTheme()
            theme.initializeTheme()

            // Verify dark theme CSS variables are applied
            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith('--theme-body-bg', '#121212')
            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith('--theme-body-text', '#e0e0e0')
            expect(documentElementMock.style.setProperty).toHaveBeenCalledWith('--theme-panel-bg', '#1e1e1e')
        })
    })

    describe('Requirement 5.4: Default to light mode when no preference exists', () => {
        it('should default to light mode when localStorage is empty', () => {
            localStorageMock.getItem.mockReturnValue(null)
            window.matchMedia.mockReturnValue({
                matches: false,
                media: '(prefers-color-scheme: dark)',
                addEventListener: vi.fn(),
                removeEventListener: vi.fn()
            })

            const theme = useTheme()
            theme.initializeTheme()

            expect(theme.currentMode.value).toBe('light')
            expect(theme.currentTheme.value).toBe('day')
        })

        it('should use LightTheme config for default mode', () => {
            localStorageMock.getItem.mockReturnValue(null)
            window.matchMedia.mockReturnValue({
                matches: false,
                media: '(prefers-color-scheme: dark)',
                addEventListener: vi.fn(),
                removeEventListener: vi.fn()
            })

            const theme = useTheme()
            theme.initializeTheme()

            expect(theme.getCurrentThemePalette()).toBe('day') // Should use LightTheme config
        })
    })

    describe('Requirement 5.5: Graceful fallback when localStorage unavailable', () => {
        it('should handle localStorage.setItem errors gracefully', () => {
            localStorageMock.setItem.mockImplementation(() => {
                throw new Error('localStorage not available')
            })

            const theme = useTheme()

            // Should not throw error
            expect(() => theme.setTheme('dark')).not.toThrow()

            // Should still update theme state
            expect(theme.currentMode.value).toBe('dark')
            expect(theme.currentTheme.value).toBe('dark')

            // Should log warning
            expect(consoleWarnSpy).toHaveBeenCalledWith('Failed to save theme preference:', expect.any(Error))
        })

        it('should handle localStorage.getItem errors gracefully', () => {
            localStorageMock.getItem.mockImplementation(() => {
                throw new Error('localStorage not available')
            })
            window.matchMedia.mockReturnValue({
                matches: false,
                media: '(prefers-color-scheme: dark)',
                addEventListener: vi.fn(),
                removeEventListener: vi.fn()
            })

            const theme = useTheme()

            // Should not throw error
            expect(() => theme.initializeTheme()).not.toThrow()

            // Should fall back to light mode
            expect(theme.currentMode.value).toBe('light')
            expect(theme.currentTheme.value).toBe('day')

            // Should log warning
            expect(consoleWarnSpy).toHaveBeenCalledWith('Failed to load theme preference:', expect.any(Error))
        })

        it('should handle localStorage.removeItem errors gracefully', () => {
            localStorageMock.removeItem.mockImplementation(() => {
                throw new Error('localStorage not available')
            })
            window.matchMedia.mockReturnValue({
                matches: true,
                media: '(prefers-color-scheme: dark)',
                addEventListener: vi.fn(),
                removeEventListener: vi.fn()
            })

            const theme = useTheme()

            // Should not throw error
            expect(() => theme.resetToSystemTheme()).not.toThrow()

            // Should still reset to system theme
            expect(theme.currentMode.value).toBe('dark')
            expect(theme.isSystemTheme.value).toBe(true)

            // Should log warning
            expect(consoleWarnSpy).toHaveBeenCalledWith('Failed to clear theme preference:', expect.any(Error))
        })

        it('should handle quota exceeded errors', () => {
            localStorageMock.setItem.mockImplementation(() => {
                const error = new Error('QuotaExceededError')
                error.name = 'QuotaExceededError'
                throw error
            })

            const theme = useTheme()

            // Should handle quota exceeded gracefully
            expect(() => theme.setTheme('dark')).not.toThrow()

            // Should still update theme state
            expect(theme.currentMode.value).toBe('dark')

            // Should log warning
            expect(consoleWarnSpy).toHaveBeenCalledWith('Failed to save theme preference:', expect.any(Error))
        })
    })

    describe('Integration Tests: Complete persistence workflow', () => {
        it('should complete full save-load cycle correctly', () => {
            // First session: save preference
            const theme1 = useTheme()
            theme1.setTheme('dark')

            expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', 'dark')

            // Simulate page reload by creating new theme instance
            localStorageMock.getItem.mockReturnValue('dark')
            const theme2 = useTheme()
            theme2.initializeTheme()

            // Should restore the saved preference
            expect(theme2.currentMode.value).toBe('dark')
            expect(theme2.currentTheme.value).toBe('dark')
            expect(theme2.isSystemTheme.value).toBe(false)
        })

        it('should handle preference changes across multiple sessions', () => {
            // Session 1: Save light mode
            const theme1 = useTheme()
            theme1.setTheme('light')

            // Session 2: Load light mode and change to dark
            localStorageMock.getItem.mockReturnValue('light')
            const theme2 = useTheme()
            theme2.initializeTheme()
            expect(theme2.currentMode.value).toBe('light')

            theme2.setTheme('dark')
            expect(localStorageMock.setItem).toHaveBeenCalledWith('theme-mode', 'dark')

            // Session 3: Load dark mode
            localStorageMock.getItem.mockReturnValue('dark')
            const theme3 = useTheme()
            theme3.initializeTheme()
            expect(theme3.currentMode.value).toBe('dark')
        })

        it('should handle reset to system theme correctly', () => {
            // Save user preference
            const theme = useTheme()
            theme.setTheme('dark')
            expect(theme.isSystemTheme.value).toBe(false)

            // Reset to system theme
            window.matchMedia.mockReturnValue({
                matches: false, // System prefers light
                media: '(prefers-color-scheme: dark)',
                addEventListener: vi.fn(),
                removeEventListener: vi.fn()
            })

            theme.resetToSystemTheme()

            // Should clear localStorage and use system preference
            expect(localStorageMock.removeItem).toHaveBeenCalledWith('theme-mode')
            expect(theme.currentMode.value).toBe('light')
            expect(theme.isSystemTheme.value).toBe(true)
        })

        it('should maintain theme consistency during localStorage errors', () => {
            const theme = useTheme()

            // Start with working localStorage
            theme.setTheme('dark')
            expect(theme.currentMode.value).toBe('dark')

            // Simulate localStorage failure
            localStorageMock.setItem.mockImplementation(() => {
                throw new Error('localStorage failed')
            })

            // Theme switching should still work
            theme.setTheme('light')
            expect(theme.currentMode.value).toBe('light')
            expect(theme.currentTheme.value).toBe('day')

            // Should log warning but continue functioning
            expect(consoleWarnSpy).toHaveBeenCalledWith('Failed to save theme preference:', expect.any(Error))
        })
    })
})