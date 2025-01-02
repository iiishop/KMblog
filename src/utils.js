import yaml from 'yaml';
// 解析 Markdown 文档的函数，只解析 meta 数据
export function parseMarkdown(content) {
    const metadataRegex = /^---\n([\s\S]*?)\n---/;
    const match = content.match(metadataRegex);

    if (match) {
        const meta = yaml.parse(match[1]);
        return { meta };
    } else {
        return { meta: {} };
    }
}

export function openLink(url) {
    window.open(url, '_blank');
}