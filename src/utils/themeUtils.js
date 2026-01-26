// src/utils/themeUtils.js - Theme Utility Functions
import config from '@/config';

/**
 * Validate if a color value has sufficient contrast ratio
 * @param {string} foreground - Foreground color (hex, rgb, rgba, etc.)
 * @param {string} background - Background color (hex, rgb, rgba, etc.)
 * @param {number} requiredRatio - Required contrast ratio (default: 4.5 for WCAG AA)
 * @returns {boolean} Whether the contrast ratio is sufficient
 */
export function validateContrastRatio(foreground, background, requiredRatio = 4.5) {
    try {
        const fgLuminance = getLuminance(foreground);
        const bgLuminance = getLuminance(background);

        const contrast = (Math.max(fgLuminance, bgLuminance) + 0.05) /
            (Math.min(fgLuminance, bgLuminance) + 0.05);

        return contrast >= requiredRatio;
    } catch (error) {
        console.warn('Contrast validation failed:', error);
        return true; // Assume valid if validation fails
    }
}

/**
 * Calculate the contrast ratio between two colors
 * @param {string} foreground - Foreground color
 * @param {string} background - Background color
 * @returns {number} Contrast ratio (1-21)
 */
export function getContrastRatio(foreground, background) {
    try {
        const fgLuminance = getLuminance(foreground);
        const bgLuminance = getLuminance(background);

        return (Math.max(fgLuminance, bgLuminance) + 0.05) /
            (Math.min(fgLuminance, bgLuminance) + 0.05);
    } catch (error) {
        console.warn('Contrast ratio calculation failed:', error);
        return 1; // Return minimum contrast if calculation fails
    }
}

/**
 * Calculate relative luminance of a color
 * @param {string} color - Color value
 * @returns {number} Relative luminance (0-1)
 */
function getLuminance(color) {
    const rgb = parseColor(color);
    if (!rgb) return 0.5; // Default to middle luminance if parsing fails

    const [r, g, b] = rgb.map(c => {
        c = c / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });

    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/**
 * Validate if a string is a valid color value
 * @param {string} color - Color value to validate
 * @returns {boolean} Whether the color is valid
 */
export function isValidColor(color) {
    if (!color || typeof color !== 'string') {
        return false;
    }

    // Remove whitespace
    color = color.trim();

    // Check for empty string
    if (color.length === 0) {
        return false;
    }

    // Valid hex color (3 or 6 digits)
    if (/^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/.test(color)) {
        return true;
    }

    // Valid rgb() or rgba()
    if (/^rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+(\s*,\s*[\d.]+)?\s*\)$/.test(color)) {
        return true;
    }

    // Valid hsl() or hsla()
    if (/^hsla?\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%(\s*,\s*[\d.]+)?\s*\)$/.test(color)) {
        return true;
    }

    // Valid CSS color keywords (basic set)
    const cssColorKeywords = [
        'transparent', 'currentcolor', 'inherit', 'initial', 'unset',
        'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
        'gray', 'grey', 'silver', 'maroon', 'olive', 'lime', 'aqua', 'teal',
        'navy', 'fuchsia', 'purple', 'orange', 'pink', 'brown'
    ];

    if (cssColorKeywords.includes(color.toLowerCase())) {
        return true;
    }

    return false;
}

/**
 * Sanitize a color value
 * @param {string} color - Color value to sanitize
 * @param {string} fallback - Fallback color if invalid
 * @returns {string} Sanitized color value
 */
export function sanitizeColor(color, fallback = '#000000') {
    if (!isValidColor(color)) {
        console.warn(`Invalid color value: ${color}, using fallback: ${fallback}`);
        return fallback;
    }
    return color.trim();
}

/**
 * Validate and sanitize a theme palette
 * @param {Object} palette - Theme palette to validate
 * @param {Object} defaults - Default values for missing colors
 * @returns {Object} Sanitized theme palette
 */
export function sanitizeThemePalette(palette, defaults = {}) {
    if (!palette || typeof palette !== 'object') {
        console.error('Invalid palette structure');
        return null;
    }

    const sanitized = {
        name: palette.name || 'unknown',
        displayName: palette.displayName || 'Unknown Theme',
        colors: {},
        accessibility: palette.accessibility || {
            contrastRatio: 4.5,
            wcagLevel: 'AA'
        }
    };

    // Default color fallbacks
    const colorDefaults = {
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
        info: '#3b82f6',
        ...defaults
    };

    // Sanitize each color in the palette
    if (palette.colors && typeof palette.colors === 'object') {
        for (const [key, value] of Object.entries(palette.colors)) {
            const fallback = colorDefaults[key] || '#000000';
            sanitized.colors[key] = sanitizeColor(value, fallback);
        }
    }

    // Ensure required colors exist
    for (const [key, fallback] of Object.entries(colorDefaults)) {
        if (!sanitized.colors[key]) {
            sanitized.colors[key] = fallback;
        }
    }

    return sanitized;
}

/**
 * Validate theme mode value
 * @param {string} mode - Theme mode to validate
 * @returns {boolean} Whether the mode is valid
 */
export function isValidThemeMode(mode) {
    return mode === 'light' || mode === 'dark';
}

/**
 * Sanitize theme mode value
 * @param {string} mode - Theme mode to sanitize
 * @param {string} fallback - Fallback mode if invalid
 * @returns {string} Sanitized theme mode
 */
export function sanitizeThemeMode(mode, fallback = 'light') {
    if (!isValidThemeMode(mode)) {
        console.warn(`Invalid theme mode: ${mode}, using fallback: ${fallback}`);
        return fallback;
    }
    return mode;
}

/**
 * Validate theme palette name
 * @param {string} themeName - Theme name to validate
 * @param {Object} availablePalettes - Available theme palettes
 * @returns {boolean} Whether the theme name is valid
 */
export function isValidThemeName(themeName, availablePalettes) {
    if (!themeName || typeof themeName !== 'string') {
        return false;
    }

    if (!availablePalettes || typeof availablePalettes !== 'object') {
        return false;
    }

    return themeName in availablePalettes;
}

/**
 * Sanitize theme palette name
 * @param {string} themeName - Theme name to sanitize
 * @param {Object} availablePalettes - Available theme palettes
 * @param {string} fallback - Fallback theme name
 * @returns {string} Sanitized theme name
 */
export function sanitizeThemeName(themeName, availablePalettes, fallback = 'day') {
    if (!isValidThemeName(themeName, availablePalettes)) {
        console.warn(`Invalid theme name: ${themeName}, using fallback: ${fallback}`);
        return fallback;
    }
    return themeName;
}

/**
 * Parse color string to RGB values
 * @param {string} color - Color string (hex, rgb, rgba, etc.)
 * @returns {number[]|null} RGB values [r, g, b] or null if parsing fails
 */
function parseColor(color) {
    if (!color || typeof color !== 'string') return null;

    // Remove whitespace
    color = color.trim();

    // Handle hex colors
    if (color.startsWith('#')) {
        const hex = color.slice(1);
        if (hex.length === 3) {
            return [
                parseInt(hex[0] + hex[0], 16),
                parseInt(hex[1] + hex[1], 16),
                parseInt(hex[2] + hex[2], 16)
            ];
        } else if (hex.length === 6) {
            return [
                parseInt(hex.slice(0, 2), 16),
                parseInt(hex.slice(2, 4), 16),
                parseInt(hex.slice(4, 6), 16)
            ];
        }
    }

    // Handle rgb() and rgba()
    const rgbMatch = color.match(/rgba?\((\d+),?\s*(\d+),?\s*(\d+)/);
    if (rgbMatch) {
        return [parseInt(rgbMatch[1]), parseInt(rgbMatch[2]), parseInt(rgbMatch[3])];
    }

    return null;
}

/**
 * Validate a theme palette for accessibility compliance
 * @param {Object} palette - Theme palette object
 * @returns {Object} Validation result with warnings and errors
 */
export function validateThemePalette(palette) {
    const result = {
        valid: true,
        warnings: [],
        errors: [],
        contrastResults: []
    };

    if (!palette || !palette.colors) {
        result.valid = false;
        result.errors.push('Invalid palette structure: missing palette or colors object');
        return result;
    }

    const colors = palette.colors;

    // Validate color values
    const colorValidationErrors = [];
    for (const [key, value] of Object.entries(colors)) {
        if (!isValidColor(value)) {
            colorValidationErrors.push(`Invalid color value for '${key}': ${value}`);
        }
    }

    if (colorValidationErrors.length > 0) {
        result.errors.push(...colorValidationErrors);
        result.valid = false;
    }

    // Check required colors
    const requiredColors = [
        'bodyBackground', 'bodyText', 'panelBackground', 'panelText',
        'headerBackground', 'linkColor', 'primary'
    ];

    for (const colorKey of requiredColors) {
        if (!colors[colorKey]) {
            result.warnings.push(`Missing required color: ${colorKey}`);
        }
    }

    // Check contrast ratios for WCAG AA compliance (4.5:1 for normal text)
    const contrastChecks = [
        { fg: colors.bodyText, bg: colors.bodyBackground, name: 'body text/background', required: 4.5 },
        { fg: colors.panelText, bg: colors.panelBackground, name: 'panel text/background', required: 4.5 },
        { fg: colors.linkColor, bg: colors.bodyBackground, name: 'link/body background', required: 4.5 },
        { fg: colors.linkColor, bg: colors.panelBackground, name: 'link/panel background', required: 4.5 },
        { fg: colors.buttonText, bg: colors.buttonBackground, name: 'button text/background', required: 4.5 },
        { fg: colors.navText, bg: colors.headerBackground, name: 'nav text/header background', required: 4.5 }
    ];

    for (const check of contrastChecks) {
        if (check.fg && check.bg) {
            // Only check if both colors are valid
            if (isValidColor(check.fg) && isValidColor(check.bg)) {
                const ratio = getContrastRatio(check.fg, check.bg);
                const passes = ratio >= check.required;

                result.contrastResults.push({
                    name: check.name,
                    ratio: ratio.toFixed(2),
                    required: check.required,
                    passes
                });

                if (!passes) {
                    result.warnings.push(
                        `Low contrast ratio for ${check.name}: ${ratio.toFixed(2)}:1 (required: ${check.required}:1)`
                    );
                }
            } else {
                result.warnings.push(`Cannot check contrast for ${check.name}: invalid color values`);
            }
        }
    }

    return result;
}

/**
 * Validate all theme palettes in configuration
 * @param {Object} themePalettes - Theme palettes object from config
 * @returns {Object} Validation results for all palettes
 */
export function validateAllThemePalettes(themePalettes) {
    const results = {};

    for (const [themeName, palette] of Object.entries(themePalettes)) {
        results[themeName] = validateThemePalette(palette);
    }

    return results;
}

/**
 * Get all available theme palette names
 * @returns {string[]} Array of theme palette names
 */
export function getAvailableThemes() {
    return Object.keys(config.themePalettes || {});
}

/**
 * Check if a theme palette exists
 * @param {string} themeName - Name of the theme palette
 * @returns {boolean} Whether the theme exists
 */
export function themeExists(themeName) {
    return !!(config.themePalettes && config.themePalettes[themeName]);
}

/**
 * Get theme palette with fallback
 * @param {string} themeName - Name of the theme palette
 * @param {string} fallback - Fallback theme name (default: 'day')
 * @returns {Object} Theme palette object
 */
export function getThemeWithFallback(themeName, fallback = 'day') {
    if (themeExists(themeName)) {
        return config.themePalettes[themeName];
    }

    if (themeExists(fallback)) {
        console.warn(`Theme '${themeName}' not found, using fallback '${fallback}'`);
        return config.themePalettes[fallback];
    }

    console.error(`Neither theme '${themeName}' nor fallback '${fallback}' found`);
    return {
        name: 'default',
        displayName: 'Default',
        colors: {
            bodyBackground: '#ffffff',
            bodyText: '#000000'
        }
    };
}

/**
 * Create a CSS custom property name from a color key
 * @param {string} colorKey - Color key from theme palette
 * @returns {string} CSS custom property name
 */
export function createCSSVariableName(colorKey) {
    // Convert camelCase to kebab-case and add theme prefix
    const kebabCase = colorKey.replace(/([A-Z])/g, '-$1').toLowerCase();
    return `--theme-${kebabCase}`;
}

/**
 * Apply theme colors to CSS custom properties
 * @param {Object} colors - Color object from theme palette
 */
export function applyCSSVariables(colors) {
    const root = document.documentElement;

    for (const [colorKey, colorValue] of Object.entries(colors)) {
        const cssVar = createCSSVariableName(colorKey);
        root.style.setProperty(cssVar, colorValue);
    }
}

/**
 * Remove theme-related CSS custom properties
 */
export function clearCSSVariables() {
    const root = document.documentElement;
    const style = root.style;

    // Remove all theme-related custom properties
    for (let i = style.length - 1; i >= 0; i--) {
        const property = style[i];
        if (property.startsWith('--theme-')) {
            style.removeProperty(property);
        }
    }
}

/**
 * Generate theme configuration for new palette
 * @param {string} name - Theme name
 * @param {string} displayName - Display name
 * @param {Object} baseColors - Base color configuration
 * @returns {Object} Complete theme palette configuration
 */
export function generateThemePalette(name, displayName, baseColors) {
    return {
        name,
        displayName,
        colors: {
            // Core colors
            bodyBackground: baseColors.bodyBackground || '#ffffff',
            bodyText: baseColors.bodyText || '#000000',

            // Panel colors
            panelBackground: baseColors.panelBackground || baseColors.bodyBackground || '#ffffff',
            panelShadow: baseColors.panelShadow || 'rgba(0, 0, 0, 0.1)',
            panelText: baseColors.panelText || baseColors.bodyText || '#000000',
            panelBorder: baseColors.panelBorder || 'rgba(0, 0, 0, 0.1)',

            // Header colors
            headerBackground: baseColors.headerBackground || baseColors.panelBackground || '#ffffff',
            headerBackgroundScrolled: baseColors.headerBackgroundScrolled || baseColors.headerBackground || '#ffffff',
            headerShadow: baseColors.headerShadow || baseColors.panelShadow || 'rgba(0, 0, 0, 0.1)',

            // Interactive colors
            linkColor: baseColors.linkColor || '#667eea',
            linkHover: baseColors.linkHover || '#764ba2',
            buttonBackground: baseColors.buttonBackground || baseColors.linkColor || '#667eea',
            buttonText: baseColors.buttonText || '#ffffff',

            // Accent colors
            primary: baseColors.primary || baseColors.linkColor || '#667eea',
            secondary: baseColors.secondary || baseColors.linkHover || '#764ba2',
            accent: baseColors.accent || '#f093fb',

            // State colors
            success: baseColors.success || '#10b981',
            warning: baseColors.warning || '#f59e0b',
            error: baseColors.error || '#ef4444',
            info: baseColors.info || '#3b82f6',

            ...baseColors // Allow override of any generated colors
        },
        accessibility: {
            contrastRatio: 4.5,
            wcagLevel: 'AA'
        }
    };
}

/**
 * Export theme configuration as JSON
 * @param {string} themeName - Name of theme to export
 * @returns {string} JSON string of theme configuration
 */
export function exportThemeConfig(themeName) {
    const theme = getThemeWithFallback(themeName);
    return JSON.stringify(theme, null, 2);
}

/**
 * Import theme configuration from JSON
 * @param {string} jsonConfig - JSON string of theme configuration
 * @returns {Object|null} Parsed theme configuration or null if invalid
 */
export function importThemeConfig(jsonConfig) {
    try {
        const theme = JSON.parse(jsonConfig);
        const validation = validateThemePalette(theme);

        if (!validation.valid) {
            console.error('Invalid theme configuration:', validation.errors);
            return null;
        }

        if (validation.warnings.length > 0) {
            console.warn('Theme configuration warnings:', validation.warnings);
        }

        return theme;
    } catch (error) {
        console.error('Failed to parse theme configuration:', error);
        return null;
    }
}

/**
 * Detect if user prefers high contrast mode
 * @returns {boolean} Whether high contrast mode is preferred
 */
export function prefersHighContrast() {
    if (typeof window === 'undefined') return false;

    // Check for forced-colors media query (Windows High Contrast Mode)
    if (window.matchMedia) {
        return window.matchMedia('(forced-colors: active)').matches ||
            window.matchMedia('(prefers-contrast: high)').matches ||
            window.matchMedia('(prefers-contrast: more)').matches;
    }

    return false;
}

/**
 * Apply high contrast mode adjustments to theme
 * @param {Object} colors - Theme colors object
 * @returns {Object} Adjusted colors for high contrast
 */
export function applyHighContrastMode(colors) {
    if (!prefersHighContrast()) {
        return colors;
    }

    // Create high contrast version by increasing contrast ratios
    return {
        ...colors,
        bodyBackground: colors.bodyBackground === '#ffffff' ? '#ffffff' : '#000000',
        bodyText: colors.bodyText === '#000000' ? '#000000' : '#ffffff',
        panelBackground: colors.bodyBackground === '#ffffff' ? '#f0f0f0' : '#1a1a1a',
        linkColor: colors.bodyBackground === '#ffffff' ? '#0000ff' : '#00ffff',
        linkHover: colors.bodyBackground === '#ffffff' ? '#0000cc' : '#00cccc'
    };
}

/**
 * Check if user prefers reduced motion
 * @returns {boolean} Whether reduced motion is preferred
 */
export function prefersReducedMotion() {
    if (typeof window === 'undefined') return false;

    if (window.matchMedia) {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    return false;
}

/**
 * Get WCAG compliance level for a contrast ratio
 * @param {number} ratio - Contrast ratio
 * @param {boolean} isLargeText - Whether the text is large (18pt+ or 14pt+ bold)
 * @returns {string} Compliance level: 'AAA', 'AA', 'Fail'
 */
export function getWCAGLevel(ratio, isLargeText = false) {
    if (isLargeText) {
        if (ratio >= 4.5) return 'AAA';
        if (ratio >= 3.0) return 'AA';
        return 'Fail';
    } else {
        if (ratio >= 7.0) return 'AAA';
        if (ratio >= 4.5) return 'AA';
        return 'Fail';
    }
}

/**
 * Generate accessibility report for a theme palette
 * @param {Object} palette - Theme palette object
 * @returns {Object} Detailed accessibility report
 */
export function generateAccessibilityReport(palette) {
    const validation = validateThemePalette(palette);

    return {
        themeName: palette.name || 'Unknown',
        displayName: palette.displayName || 'Unknown Theme',
        overallCompliance: validation.warnings.length === 0 ? 'WCAG AA' : 'Non-compliant',
        contrastResults: validation.contrastResults || [],
        warnings: validation.warnings,
        errors: validation.errors,
        recommendations: generateRecommendations(validation)
    };
}

/**
 * Generate recommendations based on validation results
 * @param {Object} validation - Validation result object
 * @returns {string[]} Array of recommendations
 */
function generateRecommendations(validation) {
    const recommendations = [];

    if (validation.warnings.length === 0) {
        recommendations.push('Theme meets WCAG AA accessibility standards');
    } else {
        recommendations.push('Consider adjusting colors to meet WCAG AA standards (4.5:1 contrast ratio)');

        if (validation.contrastResults) {
            const failedChecks = validation.contrastResults.filter(r => !r.passes);
            if (failedChecks.length > 0) {
                recommendations.push(`${failedChecks.length} color combination(s) need improvement`);
            }
        }
    }

    return recommendations;
}

/**
 * Listen for high contrast mode changes
 * @param {Function} callback - Callback function to execute when high contrast mode changes
 * @returns {Function} Cleanup function to remove listener
 */
export function onHighContrastChange(callback) {
    if (typeof window === 'undefined' || !window.matchMedia) {
        return () => { }; // No-op cleanup
    }

    const queries = [
        window.matchMedia('(forced-colors: active)'),
        window.matchMedia('(prefers-contrast: high)'),
        window.matchMedia('(prefers-contrast: more)')
    ];

    const handler = (e) => {
        if (e.matches) {
            callback(true);
        } else {
            // Check if any other query still matches
            const anyMatch = queries.some(q => q.matches);
            callback(anyMatch);
        }
    };

    queries.forEach(query => {
        if (query.addEventListener) {
            query.addEventListener('change', handler);
        } else if (query.addListener) {
            query.addListener(handler);
        }
    });

    // Return cleanup function
    return () => {
        queries.forEach(query => {
            if (query.removeEventListener) {
                query.removeEventListener('change', handler);
            } else if (query.removeListener) {
                query.removeListener(handler);
            }
        });
    };
}