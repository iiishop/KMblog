import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { tagHue } from './tagColor';

describe('tag identity colors', () => {
    it('keeps identity across calls and Unicode normalization', () => {
        for (const tag of ['笔记', 'OpenGL', 'hello world', '🔖', 'a/b?#']) {
            expect(tagHue(tag)).toBe(tagHue(tag));
            expect(tagHue(tag)).toBeGreaterThanOrEqual(0);
            expect(tagHue(tag)).toBeLessThan(360);
        }
        expect(tagHue('café')).toBe(tagHue('cafe\u0301'));
        expect(new Set(['笔记', 'OpenGL', 'Unity', 'AI', '测试'].map(tagHue)).size).toBe(5);
    });

    // Exhaust all possible hues, using the real CSS palette rather than test-only colors.
    it('keeps tag text above 4.5:1 contrast in all four palettes', () => {
        const css = readFileSync(resolve('src/color.css'), 'utf8');
        const palettes = [...css.matchAll(/--theme-tag-saturation:\s*([\d.]+)%;\s*--theme-tag-ink-lightness:\s*([\d.]+)%;\s*--theme-tag-fill-lightness:\s*([\d.]+)%;/g)];
        expect(palettes).toHaveLength(4);
        const luminance = (h, s, l) => {
            s /= 100;
            l /= 100;
            const a = s * Math.min(l, 1 - l);
            const rgb = [0, 8, 4].map(n => {
                const k = (n + h / 30) % 12;
                const c = l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1));
                return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
            });
            return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
        };
        for (const [, saturation, ink, fill] of palettes) {
            for (let hue = 0; hue < 360; hue++) {
                const a = luminance(hue, +saturation, +ink);
                const b = luminance(hue, +saturation, +fill);
                expect((Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)).toBeGreaterThanOrEqual(4.5);
            }
        }
    });
});
