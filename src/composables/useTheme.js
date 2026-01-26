// src/composables/useTheme.js - Theme Management Composable
import { ref, computed, watch } from 'vue';
import config from '@/config';
import {
    prefersHighContrast,
    applyHighContrastMode,
    onHighContrastChange,
    prefersReducedMotion,
    sanitizeThemePalette,
    sanitizeThemeMode,
    sanitizeThemeName,
    isValidThemeMode
} from '@/utils/themeUtils';

// Global theme state
const currentMode = ref('light'); // 'light' or 'dark'
const currentTheme = ref('day'); // Current theme palette name
const isSystemTheme = ref(true); // Whether using system preference
const transitionsEnabled = ref(true); // Whether transitions are enabled
const highContrastMode = ref(false); // Whether high contrast mode is active

// Performance optimization: debounce timer for rapid theme changes
let themeChangeTimer = null;

/**
 * Theme Management Composable
 * Provides reactive theme management with persistence and system detection
 */
export function useTheme() {
    // Computed properties
    const isDarkMode = computed(() => currentMode.value === 'dark');
    const themeIcon = computed(() => isDarkMode.value ? 'moon' : 'sun');

    /**
     * Get the theme palette configuration for a given theme name
     * @param {string} themeName - Name of the theme palette
     * @returns {Object} Theme palette configuration
     */
    function getThemePalette(themeName) {
        // Validate input
        if (!themeName || typeof themeName !== 'string') {
            console.error('Invalid theme name provided, falling back to default');
            themeName = 'day';
        }

        // Check if theme palettes exist
        if (!config.themePalettes || typeof config.themePalettes !== 'object') {
            console.error('Theme palettes configuration is missing or invalid');
            return getDefaultThemePalette();
        }

        const palette = config.themePalettes[themeName];
        if (!palette) {
            console.warn(`Theme palette '${themeName}' not found, falling back to 'day'`);

            // Try fallback to 'day' theme
            if (config.themePalettes.day) {
                const sanitized = sanitizeThemePalette(config.themePalettes.day);
                return sanitized || config.themePalettes.day;
            }

            // If 'day' theme doesn't exist, return minimal default
            console.error('Default theme palette not found, using minimal fallback');
            return getDefaultThemePalette();
        }

        // Sanitize the palette before returning
        const sanitized = sanitizeThemePalette(palette);
        if (!sanitized) {
            console.error(`Failed to sanitize theme palette '${themeName}', using fallback`);
            return getDefaultThemePalette();
        }

        return sanitized;
    }

    /**
     * Get a minimal default theme palette as last resort fallback
     * @returns {Object} Minimal theme palette configuration
     */
    function getDefaultThemePalette() {
        return {
            name: 'default',
            displayName: 'Default',
            colors: {
                bodyBackground: '#ffffff',
                bodyText: '#000000',
                panelBackground: '#f9f9f9',
                panelText: '#000000',
                panelShadow: 'rgba(0, 0, 0, 0.1)',
                panelBorder: 'rgba(0, 0, 0, 0.05)',
                headerBackground: 'rgba(255, 255, 255, 0.9)',
                headerBackgroundScrolled: 'rgba(255, 255, 255, 0.95)',
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
        };
    }

    /**
     * Apply a theme palette to CSS variables
     * @param {string} themeName - Name of the theme palette to apply
     */
    function applyThemePalette(themeName) {
        try {
            const palette = getThemePalette(themeName);

            // Validate palette structure
            if (!palette || typeof palette !== 'object') {
                console.error('Invalid palette structure, cannot apply theme');
                return;
            }

            const root = document.documentElement;
            if (!root) {
                console.error('Document root element not available');
                return;
            }

            // Apply theme data attribute for CSS selectors
            try {
                root.setAttribute('data-theme', themeName);
            } catch (error) {
                console.warn('Failed to set data-theme attribute:', error);
            }

            // Apply high contrast mode if needed
            let colors = palette.colors;
            if (!colors || typeof colors !== 'object') {
                console.error('Theme palette missing colors object');
                return;
            }

            if (highContrastMode.value && colors) {
                try {
                    colors = applyHighContrastMode(colors);
                    if (root.setAttribute) {
                        root.setAttribute('data-high-contrast', 'true');
                    }
                } catch (error) {
                    console.warn('Failed to apply high contrast mode:', error);
                }
            } else {
                try {
                    if (root.removeAttribute) {
                        root.removeAttribute('data-high-contrast');
                    }
                } catch (error) {
                    console.warn('Failed to remove high contrast attribute:', error);
                }
            }

            // Apply palette colors to CSS variables if palette has colors
            if (colors) {
                // Map palette colors to CSS variables
                const colorMappings = {
                    // Core colors
                    bodyBackground: '--theme-body-bg',
                    bodyText: '--theme-body-text',

                    // Panel colors
                    panelBackground: '--theme-panel-bg',
                    panelShadow: '--theme-panel-shadow',
                    panelText: '--theme-panel-text',
                    panelBorder: '--theme-panel-border',

                    // Header colors
                    headerBackground: '--theme-header-bg',
                    headerBackgroundScrolled: '--theme-header-bg-scrolled',
                    headerShadow: '--theme-header-shadow',

                    // Interactive colors
                    linkColor: '--theme-link-color',
                    linkHover: '--theme-link-hover',
                    buttonBackground: '--theme-button-bg',
                    buttonText: '--theme-button-text',
                    buttonHover: '--theme-button-hover',
                    buttonActive: '--theme-button-active',

                    // Semantic accent colors
                    primary: '--theme-primary',
                    primaryHover: '--theme-primary-hover',
                    primaryActive: '--theme-primary-active',
                    primaryDisabled: '--theme-primary-disabled',

                    secondary: '--theme-secondary',
                    secondaryHover: '--theme-secondary-hover',
                    secondaryActive: '--theme-secondary-active',
                    secondaryDisabled: '--theme-secondary-disabled',

                    accent: '--theme-accent',
                    accentHover: '--theme-accent-hover',
                    accentActive: '--theme-accent-active',
                    accentDisabled: '--theme-accent-disabled',

                    // State colors
                    success: '--theme-success',
                    successHover: '--theme-success-hover',
                    successActive: '--theme-success-active',
                    successDisabled: '--theme-success-disabled',

                    warning: '--theme-warning',
                    warningHover: '--theme-warning-hover',
                    warningActive: '--theme-warning-active',
                    warningDisabled: '--theme-warning-disabled',

                    error: '--theme-error',
                    errorHover: '--theme-error-hover',
                    errorActive: '--theme-error-active',
                    errorDisabled: '--theme-error-disabled',

                    info: '--theme-info',
                    infoHover: '--theme-info-hover',
                    infoActive: '--theme-info-active',
                    infoDisabled: '--theme-info-disabled',

                    // Input and form states
                    inputBackground: '--theme-input-bg',
                    inputBorder: '--theme-input-border',
                    inputBorderHover: '--theme-input-border-hover',
                    inputBorderFocus: '--theme-input-border-focus',
                    inputText: '--theme-input-text',
                    inputPlaceholder: '--theme-input-placeholder',
                    inputDisabled: '--theme-input-disabled',

                    // Surface colors
                    surfaceDefault: '--theme-surface-default',
                    surfaceHover: '--theme-surface-hover',
                    surfaceActive: '--theme-surface-active',
                    surfaceDisabled: '--theme-surface-disabled'
                };

                // Apply each color from the palette to its corresponding CSS variable
                // Batch updates for better performance
                Object.entries(colorMappings).forEach(([paletteKey, cssVar]) => {
                    if (colors[paletteKey]) {
                        try {
                            root.style.setProperty(cssVar, colors[paletteKey]);
                        } catch (error) {
                            console.warn(`Failed to set CSS variable ${cssVar}:`, error);
                        }
                    }
                });
            }

            // Update current theme
            currentTheme.value = themeName;

            console.log(`Applied theme palette: ${themeName}${highContrastMode.value ? ' (high contrast)' : ''}`);
        } catch (error) {
            console.error('Failed to apply theme palette:', error);
            // Attempt to apply default theme as fallback
            if (themeName !== 'day') {
                console.log('Attempting to apply default theme as fallback');
                try {
                    const defaultPalette = getDefaultThemePalette();
                    const root = document.documentElement;
                    if (root && defaultPalette.colors) {
                        Object.entries(defaultPalette.colors).forEach(([key, value]) => {
                            const cssVar = `--theme-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
                            try {
                                root.style.setProperty(cssVar, value);
                            } catch (e) {
                                // Silently fail for individual properties
                            }
                        });
                    }
                } catch (fallbackError) {
                    console.error('Failed to apply fallback theme:', fallbackError);
                }
            }
        }
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
        const sanitizedPalette = sanitizeThemeName(themePalette, config.themePalettes, 'day');

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

        // Check if required theme palettes exist
        if (!config.themePalettes.day) {
            warnings.push("Missing 'day' theme palette");
        }

        if (!config.themePalettes.dark) {
            warnings.push("Missing 'dark' theme palette");
        }

        // Check if configured themes exist
        if (config.LightTheme && !config.themePalettes[config.LightTheme]) {
            warnings.push(`LightTheme '${config.LightTheme}' palette not found`);
        }

        if (config.DarkTheme && !config.themePalettes[config.DarkTheme]) {
            warnings.push(`DarkTheme '${config.DarkTheme}' palette not found`);
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
        currentMode: readonly(currentMode),
        currentTheme: readonly(currentTheme),
        isSystemTheme: readonly(isSystemTheme),
        transitionsEnabled: readonly(transitionsEnabled),
        highContrastMode: readonly(highContrastMode),

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

// Create a readonly wrapper for reactive refs
function readonly(ref) {
    return computed(() => ref.value);
}

// Export a singleton instance for global use
export const themeManager = useTheme();