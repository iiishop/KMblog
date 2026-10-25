import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';
import YAML from 'yaml';
import CalendarPanel from './CalendarPanel.vue';

const readPublic = path => readFileSync(resolve('public', path.replace(/^\//, '')), 'utf8');

// Article bodies and generated directories are local blog content, excluded
// from Git. Run these parity checks when that content is available.
const hasLocalContent = existsSync(resolve('public/assets/PostDirectory.json'))
    && JSON.parse(readPublic('/assets/Metadata.json')).every(entry =>
        existsSync(resolve('public', entry.path.replace(/^\//, '')))
    );

describe.skipIf(!hasLocalContent)('homepage index display parity', () => {
    it('keeps every displayed metadata field identical to the article source', () => {
        const index = JSON.parse(readPublic('/assets/Metadata.json'));
        for (const entry of index) {
            const source = readPublic(entry.path);
            const meta = YAML.parse(source.match(/^---\r?\n([\s\S]*?)\r?\n---/)[1]);
            for (const field of ['title', 'date', 'pre', 'tags', 'categories']) {
                const fallback = ['tags', 'categories'].includes(field) ? [] : '';
                expect(entry[field] ?? fallback, `${entry.path}: ${field}`).toEqual(meta[field] ?? fallback);
            }
        }
    });

    it('produces the same calendar events as scanning the full article directory', () => {
        const parse = CalendarPanel.methods.parseMermaidGantt;
        const paths = [];
        const collect = value => {
            if (Array.isArray(value)) {
                value.forEach(entry => { if (entry.path) paths.push(entry.path); });
            } else if (value && typeof value === 'object') {
                Object.values(value).forEach(collect);
            }
        };
        collect(JSON.parse(readPublic('/assets/PostDirectory.json')));
        const previous = paths.flatMap(path => {
            const content = readPublic(path);
            const date = content.match(/^---\s*\n[\s\S]*?date:\s*(.+?)\n[\s\S]*?---/)?.[1].trim() || null;
            return parse(content, path, date);
        });
        const indexed = JSON.parse(readPublic('/assets/Calendar.json')).flatMap(entry =>
            parse(entry.content, entry.path, entry.date || null)
        );
        const canonical = events => events.map(event => JSON.stringify(event)).sort();
        expect(previous.length).toBeGreaterThan(0);
        expect(canonical(indexed)).toEqual(canonical(previous));
    });
});
