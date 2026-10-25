// Only relative image names belong under Posts/Images. Preserve URL schemes,
// root-relative paths and existing escapes (especially encoded '/' and '#').
export function resolvePostImageUrl(source) {
    if (!source || typeof source !== 'string') return '';
    if (/^(?:[a-z][a-z\d+.-]*:|\/|#)/i.test(source)) return source;
    const path = source.replace(/\\/g, '/');
    return `/Posts/Images/${encodeURI(path).replace(/%25([\da-f]{2})/gi, '%$1')}`;
}

// Support local filenames with spaces without swallowing Markdown image titles.
export function prepareMarkdownImages(markdown) {
    return markdown.replace(/!\[([^\]\r\n]*)\]\(([^()<>\r\n]+)\)/g, (original, alt, value) => {
        const title = value.match(/^(.*?)\s+("[^"]*"|'[^']*')$/);
        const path = title ? title[1] : value;
        if (!/\s/.test(path)) return original;
        return `![${alt}](<${path}>${title ? ` ${title[2]}` : ''})`;
    });
}
