// src/composables/useTheme.js - Theme Management Composable
import { ref, computed, watch } from 'vue';
import config from '@/config';
import {
    prefersHighContrast,
    onHighContrastChange,
    prefersReducedMotion,
    sanitizeThemeMode,
    isValidThemeMode
} from '@/utils/themeUtils';

// Global theme state
const currentMode = ref('light'); // 'light' or 'dark'
const currentTheme = ref('day'); // Current theme palette name
const isSystemTheme = ref(true); // Whether using system preference
const transitionsEnabled = ref(true); // Whether transitions are enabled
const highContrastMode = ref(false); // Whether high contrast mode is active

/**
 * Theme Management Composable
 * Provides reactive theme management with persistence and system detection
 */
export function useTheme() {
    // Computed properties
    const isDarkMode = computed(() => currentMode.value === 'dark');
    const themeIcon = computed(() => isDarkMode.value ? 'moon' : 'sun');

    /**
     * Apply a theme palette by setting the data-theme attribute
     * All theme colors are defined in color.css using [data-theme] selectors
     * @param {string} themeName - Name of the theme palette to apply
     */
    function applyThemePalette(themeName) {
        try {
            // Validate theme name
            const availableThemes = config.availableThemes || ['day', 'dark', 'night', 'bright'];
            if (!availableThemes.includes(themeName)) {
                console.warn(`Theme '${themeName}' not found, falling back to 'day'`);
                themeName = 'day';
            }

            const root = document.documentElement;
            if (!root) {
                console.error('Document root element not available');
                return;
            }

            // Apply theme data attribute - this triggers CSS variable changes in color.css
            root.setAttribute('data-theme', themeName);

            // Apply high contrast mode if needed
            if (highContrastMode.value) {
                if (root.setAttribute) {
                    root.setAttribute('data-high-contrast', 'true');
                }
            } else {
                if (root.removeAttribute) {
                    root.removeAttribute('data-high-contrast');
                }
            }

            // Update current theme state
            currentTheme.value = themeName;

            // Log theme change for debugging
            console.log(`Theme applied: ${themeName}`);
        } catch (error) {
            console.error('Failed to apply theme palette:', error);
        }
    }

    /**
     * Get the theme palette configuration for a given theme name
     * Note: This is kept for backward compatibility but colors are now in color.css
     * @param {string} themeName - Name of the theme palette
     * @returns {Object} Theme palette configuration
     */
    function getThemePalette(themeName) {
        // Validate input
        if (!themeName || typeof themeName !== 'string') {
            console.error('Invalid theme name provided, falling back to default');
            themeName = 'day';
        }

        const availableThemes = config.availableThemes || ['day', 'dark', 'night', 'bright'];
        if (!availableThemes.includes(themeName)) {
            console.warn(`Theme palette '${themeName}' not found, falling back to 'day'`);
            themeName = 'day';
        }

        // Return minimal palette info - actual colors are in color.css
        return {
            name: themeName,
            displayName: themeName.charAt(0).toUpperCase() + themeName.slice(1) + ' Theme'
        };
    }

    /**
     * Get a minimal default theme palette as last resort fallback
     * @returns {Object} Minimal theme palette configuration
     */
    function getDefaultThemePalette() {
        return {
            name: 'day',
            displayName: 'Day Theme'
        };
    }

    /**
     * Get the appropriate theme palette for the current mode
     * @returns {string} Theme palette name
     */
    function getCurrentThemePalette() {
        if (currentMode.value === 'dark') {
            return config.DarkTheme || 'dark';
        } else {
            return config.LightTheme || 'day';
        }
    }

    /**
     * Set the theme mode and apply the corresponding palette
     * @param {string} mode - 'light' or 'dark'
     * @param {boolean} savePreference - Whether to save to localStorage
     */
    function setTheme(mode, savePreference = true) {
        // Validate and sanitize the mode
        const sanitizedMode = sanitizeThemeMode(mode, 'light');

        if (!isValidThemeMode(sanitizedMode)) {
            console.error(`Invalid theme mode after sanitization: ${sanitizedMode}`);
            return;
        }

        currentMode.value = sanitizedMode;
        const themePalette = getCurrentThemePalette();

        // Validate theme palette name
        const availableThemes = config.availableThemes || ['day', 'dark', 'night', 'bright'];
        const sanitizedPalette = availableThemes.includes(themePalette) ? themePalette : 'day';

        applyThemePalette(sanitizedPalette);

        if (savePreference) {
            saveThemePreference(sanitizedMode);
            isSystemTheme.value = false;
        }

        console.log(`Theme mode set to: ${sanitizedMode} (palette: ${sanitizedPalette})`);
    }

    /**
     * Toggle between light and dark modes
     */
    function toggleTheme() {
        const newMode = currentMode.value === 'light' ? 'dark' : 'light';
        setTheme(newMode);
    }

    /**
     * Detect system theme preference using prefers-color-scheme
     * @returns {string} 'light' or 'dark'
     */
    function detectSystemTheme() {
        // Check if system detection is enabled
        if (!config.enableSystemDetection) {
            console.log('System theme detection is disabled in configuration');
            return 'light';
        }

        try {
            // Check if window is available (SSR safety)
            if (typeof window === 'undefined') {
                console.warn('Window object not available, falling back to light theme');
                return 'light';
            }

            // Check if matchMedia is supported
            if (!window.matchMedia || typeof window.matchMedia !== 'function') {
                console.warn('matchMedia not supported, falling back to light theme');
                return 'light';
            }

            // Check if prefers-color-scheme is supported
            let mediaQuery;
            try {
                mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            } catch (error) {
                console.warn('Failed to create media query:', error);
                return 'light';
            }

            // Some browsers support matchMedia but not prefers-color-scheme
            if (!mediaQuery || mediaQuery.media === 'not all') {
                console.warn('prefers-color-scheme not supported, falling back to light theme');
                return 'light';
            }

            // Check if matches property is available
            if (typeof mediaQuery.matches !== 'boolean') {
                console.warn('Media query matches property not available');
                return 'light';
            }

            if (mediaQuery.matches) {
                console.log('System theme detected: dark');
                return 'dark';
            } else {
                console.log('System theme detected: light');
                return 'light';
            }
        } catch (error) {
            console.warn('System theme detection failed:', error);
            return 'light';
        }
    }

    /**
     * Reset to system theme preference
     */
    function resetToSystemTheme() {
        try {
            const systemMode = detectSystemTheme();
            currentMode.value = systemMode;
            const themePalette = getCurrentThemePalette();
            applyThemePalette(themePalette);

            // Clear saved preference
            try {
                if (typeof localStorage !== 'undefined') {
                    localStorage.removeItem('theme-mode');
                    console.log('Cleared saved theme preference');
                }
            } catch (error) {
                if (error.name === 'SecurityError') {
                    console.warn('Cannot clear theme preference due to security settings');
                } else {
                    console.warn('Failed to clear theme preference:', error);
                }
            }

            isSystemTheme.value = true;
            console.log(`Reset to system theme: ${systemMode} (palette: ${themePalette})`);
        } catch (error) {
            console.error('Failed to reset to system theme:', error);
            // Fallback to light mode if reset fails
            try {
                currentMode.value = 'light';
                applyThemePalette('day');
                isSystemTheme.value = true;
            } catch (fallbackError) {
                console.error('Failed to apply fallback theme:', fallbackError);
            }
        }
    }

    /**
     * Save theme preference to localStorage
     * @param {string} mode - Theme mode to save
     */
    function saveThemePreference(mode) {
        // Validate input
        if (mode !== 'light' && mode !== 'dark') {
            console.warn(`Invalid theme mode for saving: ${mode}`);
            return;
        }

        try {
            // Check if localStorage is available
            if (typeof localStorage === 'undefined') {
                console.warn('localStorage is not available');
                return;
            }

            // Test if localStorage is accessible (can be blocked by privacy settings)
            localStorage.setItem('theme-mode', mode);
            console.log(`Theme preference saved: ${mode}`);
        } catch (error) {
            // Handle quota exceeded, security errors, or other localStorage failures
            if (error.name === 'QuotaExceededError') {
                console.warn('localStorage quota exceeded, cannot save theme preference');
            } else if (error.name === 'SecurityError') {
                console.warn('localStorage access denied due to security settings');
            } else {
                console.warn('Failed to save theme preference:', error);
            }
        }
    }

    /**
     * Load theme preference from localStorage
     * @returns {string|null} Saved theme mode or null
     */
    function loadThemePreference() {
        try {
            // Check if localStorage is available
            if (typeof localStorage === 'undefined') {
                console.warn('localStorage is not available');
                return null;
            }

            const savedMode = localStorage.getItem('theme-mode');

            // Validate the loaded value
            if (savedMode && savedMode !== 'light' && savedMode !== 'dark') {
                console.warn(`Invalid saved theme mode: ${savedMode}, clearing preference`);
                try {
                    localStorage.removeItem('theme-mode');
                } catch (e) {
                    // Silently fail if we can't clear
                }
                return null;
            }

            return savedMode;
        } catch (error) {
            // Handle security errors or other localStorage failures
            if (error.name === 'SecurityError') {
                console.warn('localStorage access denied due to security settings');
            } else {
                console.warn('Failed to load theme preference:', error);
            }
            return null;
        }
    }

    /**
     * Initialize theme system
     */
    function initializeTheme() {
        try {
            // Batch all initialization operations
            const initOperations = {
                highContrast: false,
                reducedMotion: false,
                savedMode: null,
                systemMode: 'light'
            };

            // Detect high contrast mode
            try {
                initOperations.highContrast = prefersHighContrast();
                highContrastMode.value = initOperations.highContrast;
            } catch (error) {
                console.warn('Failed to detect high contrast mode:', error);
            }

            // Check for reduced motion preference
            try {
                initOperations.reducedMotion = prefersReducedMotion();
                if (initOperations.reducedMotion) {
                    transitionsEnabled.value = false;
                    console.log('Reduced motion detected, transitions disabled');
                }
            } catch (error) {
                console.warn('Failed to detect reduced motion preference:', error);
            }

            // Prevent flash by adding no-transitions class
            try {
                if (document && document.body) {
                    document.body.classList.add('no-transitions');
                }
            } catch (error) {
                console.warn('Failed to add no-transitions class:', error);
            }

            // Load saved preference or detect system theme
            try {
                initOperations.savedMode = loadThemePreference();
            } catch (error) {
                console.warn('Failed to load theme preference:', error);
            }

            let initialMode;

            if (initOperations.savedMode && (initOperations.savedMode === 'light' || initOperations.savedMode === 'dark')) {
                initialMode = initOperations.savedMode;
                isSystemTheme.value = false;
                console.log(`Loaded saved theme preference: ${initialMode}`);
            } else {
                try {
                    initOperations.systemMode = detectSystemTheme();
                    initialMode = initOperations.systemMode;
                    isSystemTheme.value = true;
                    console.log(`Using system theme: ${initialMode}`);
                } catch (error) {
                    console.warn('Failed to detect system theme:', error);
                    initialMode = 'light';
                    isSystemTheme.value = true;
                }
            }

            // Set initial theme without saving (to avoid overriding system preference)
            try {
                setTheme(initialMode, false);
            } catch (error) {
                console.error('Failed to set initial theme:', error);
                // Try fallback to light mode
                try {
                    setTheme('light', false);
                } catch (fallbackError) {
                    console.error('Failed to set fallback theme:', fallbackError);
                }
            }

            // Enable transitions after a short delay to prevent flash (unless reduced motion)
            // Use a single timeout for better performance
            setTimeout(() => {
                try {
                    if (config.enableTransitions && !initOperations.reducedMotion) {
                        if (document && document.body) {
                            document.body.classList.remove('no-transitions');
                        }
                        transitionsEnabled.value = true;
                    } else {
                        if (document && document.body) {
                            document.body.classList.remove('no-transitions');
                        }
                    }
                } catch (error) {
                    console.warn('Failed to enable transitions:', error);
                }
            }, 100);

            // Listen for system theme changes (only if enabled)
            if (config.enableSystemDetection && typeof window !== 'undefined' && window.matchMedia) {
                try {
                    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

                    // Check if the media query is supported
                    if (mediaQuery && mediaQuery.media !== 'not all') {
                        const changeHandler = (e) => {
                            try {
                                if (isSystemTheme.value) {
                                    const newMode = e.matches ? 'dark' : 'light';
                                    setTheme(newMode, false);
                                    console.log(`System theme changed to: ${newMode}`);
                                }
                            } catch (error) {
                                console.warn('Failed to handle system theme change:', error);
                            }
                        };

                        if (mediaQuery.addEventListener) {
                            mediaQuery.addEventListener('change', changeHandler);
                        } else if (mediaQuery.addListener) {
                            // Fallback for older browsers
                            mediaQuery.addListener(changeHandler);
                        }
                        console.log('System theme change listener registered');
                    } else {
                        console.warn('prefers-color-scheme media query not supported, system theme changes will not be detected');
                    }
                } catch (error) {
                    console.warn('Failed to listen for system theme changes:', error);
                }
            }

            // Listen for high contrast mode changes
            try {
                const cleanupHighContrast = onHighContrastChange((isHighContrast) => {
                    try {
                        highContrastMode.value = isHighContrast;
                        const themePalette = getCurrentThemePalette();
                        applyThemePalette(themePalette);
                        console.log(`High contrast mode ${isHighContrast ? 'enabled' : 'disabled'}`);
                    } catch (error) {
                        console.warn('Failed to handle high contrast mode change:', error);
                    }
                });

                // Store cleanup function for potential future use
                if (typeof window !== 'undefined') {
                    window.__themeCleanup = cleanupHighContrast;
                }
            } catch (error) {
                console.warn('Failed to set up high contrast mode listener:', error);
            }
        } catch (error) {
            console.error('Theme initialization failed:', error);
            // Attempt minimal fallback initialization
            try {
                currentMode.value = 'light';
                applyThemePalette('day');
            } catch (fallbackError) {
                console.error('Failed to apply fallback theme during initialization:', fallbackError);
            }
        }
    }

    /**
     * Validate theme configuration
     */
    function validateThemeConfig() {
        const warnings = [];
        const availableThemes = config.availableThemes || ['day', 'dark', 'night', 'bright'];

        // Check if required theme palettes exist
        if (!availableThemes.includes('day')) {
            warnings.push("Missing 'day' theme in availableThemes");
        }

        if (!availableThemes.includes('dark')) {
            warnings.push("Missing 'dark' theme in availableThemes");
        }

        // Check if configured themes exist
        if (config.LightTheme && !availableThemes.includes(config.LightTheme)) {
            warnings.push(`LightTheme '${config.LightTheme}' not found in availableThemes`);
        }

        if (config.DarkTheme && !availableThemes.includes(config.DarkTheme)) {
            warnings.push(`DarkTheme '${config.DarkTheme}' not found in availableThemes`);
        }

        if (warnings.length > 0) {
            console.warn('Theme configuration issues:', warnings);
        }

        return warnings.length === 0;
    }

    // Watch for configuration changes (useful for development)
    watch(() => config.LightTheme, () => {
        if (currentMode.value === 'light') {
            const themePalette = getCurrentThemePalette();
            applyThemePalette(themePalette);
        }
    });

    watch(() => config.DarkTheme, () => {
        if (currentMode.value === 'dark') {
            const themePalette = getCurrentThemePalette();
            applyThemePalette(themePalette);
        }
    });

    return {
        // State
        currentMode: computed(() => currentMode.value),
        currentTheme: computed(() => currentTheme.value),
        isSystemTheme: computed(() => isSystemTheme.value),
        transitionsEnabled: computed(() => transitionsEnabled.value),
        highContrastMode: computed(() => highContrastMode.value),

        // Computed
        isDarkMode,
        themeIcon,

        // Actions
        setTheme,
        toggleTheme,
        resetToSystemTheme,
        initializeTheme,
        validateThemeConfig,

        // Utilities
        getThemePalette,
        getCurrentThemePalette,
        detectSystemTheme,
        loadThemePreference,
        saveThemePreference
    };
}

// Export a singleton instance for global use
export const themeManager = useTheme();