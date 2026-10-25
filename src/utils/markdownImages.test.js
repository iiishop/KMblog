import { describe, expect, it } from 'vitest';
import md from '@/components/MarkdownPanelComps/MarkdownRenender';
import { prepareMarkdownImages, resolvePostImageUrl } from './markdownImages';

describe('Markdown image compatibility', () => {
    it.each([
        ['photo.png', '/Posts/Images/photo.png'],
        ['目录/照片 1.png', '/Posts/Images/%E7%9B%AE%E5%BD%95/%E7%85%A7%E7%89%87%201.png'],
        ['folder\\photo.png', '/Posts/Images/folder/photo.png'],
        ['a%20b%23c%2Fd.png', '/Posts/Images/a%20b%23c%2Fd.png'],
        ['100%.png', '/Posts/Images/100%25.png'],
        ['/Posts/Images/photo.png', '/Posts/Images/photo.png'],
        ['//cdn.example.com/a.png', '//cdn.example.com/a.png'],
        ['https://example.com/a.png', 'https://example.com/a.png'],
        ['data:image/png;base64,YQ==', 'data:image/png;base64,YQ=='],
        ['blob:https://example.com/id', 'blob:https://example.com/id']
    ])('resolves %s without corrupting the URL', (source, expected) => {
        expect(resolvePostImageUrl(source)).toBe(expected);
    });

    it.each([
        ['![photo](image.png "A title")', '/Posts/Images/image.png', 'A title'],
        ['![photo](my image.png "A title")', '/Posts/Images/my%20image.png', 'A title'],
        ['![photo](my image.png)', '/Posts/Images/my%20image.png', null],
        ['![photo](/images/photo.png)', '/images/photo.png', null],
        ['![photo](data:image/png;base64,YQ==)', 'data:image/png;base64,YQ==', null],
        ['![photo](100%.png)', '/Posts/Images/100%25.png', null],
        ['![photo](encoded%2Fname.png)', '/Posts/Images/encoded%2Fname.png', null]
    ])('renders %s through the Markdown pipeline', (input, src, title) => {
        const container = document.createElement('div');
        container.innerHTML = md.render(prepareMarkdownImages(input));
        expect(container.querySelector('img').getAttribute('src')).toBe(src);
        expect(container.querySelector('img').getAttribute('title')).toBe(title);
    });

    it('preserves Mermaid labels containing HTML as diagram source text', () => {
        const source = 'graph TD\n A["<b>A & B</b>"] --> C';
        const container = document.createElement('div');
        container.innerHTML = md.render('```mermaid\n' + source + '\n```');
        expect(container.querySelector('.mermaid').textContent).toBe(source);
        expect(container.querySelector('.mermaid b')).toBeNull();
    });
});
