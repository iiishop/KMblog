import MarkdownIt from 'markdown-it';
import { resolvePostImageUrl } from '@/utils/markdownImages';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css'; // Prism 的暗色主题

// 导入核心语言（必须按依赖顺序导入）
import 'prismjs/components/prism-markup';
import 'prismjs/components/prism-css';
import 'prismjs/components/prism-clike';
import 'prismjs/components/prism-javascript';

// JavaScript 系列（依赖 javascript）
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-jsx';
import 'prismjs/components/prism-tsx';

// C 系列（依赖 clike）
import 'prismjs/components/prism-c';
import 'prismjs/components/prism-cpp';
import 'prismjs/components/prism-csharp';
import 'prismjs/components/prism-java';

// 独立语言
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-go';
import 'prismjs/components/prism-rust';
import 'prismjs/components/prism-ruby';
import 'prismjs/components/prism-swift';
import 'prismjs/components/prism-kotlin';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-yaml';
import 'prismjs/components/prism-markdown';
import 'prismjs/components/prism-scss';

// PHP 需要特殊处理（依赖 markup-templating）
import 'prismjs/components/prism-markup-templating';
import 'prismjs/components/prism-php';

import markdownItTexmath from 'markdown-it-texmath';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import markdownItTaskLists from 'markdown-it-task-lists';
import markdownItMultimdTable from 'markdown-it-multimd-table';
import markdownItCodeCopy from 'markdown-it-code-copy';

// 语言别名映射
const languageAliases = {
    'js': 'javascript',
    'ts': 'typescript',
    'py': 'python',
    'rb': 'ruby',
    'sh': 'bash',
    'yml': 'yaml',
    'html': 'markup',
    'xml': 'markup',
    'svg': 'markup',
    'cs': 'csharp',
    'cpp': 'cpp',
    'c++': 'cpp',
};

// 创建 markdown-it 实例
const md = new MarkdownIt({
    html: true, // 启用HTML标签解析
    xhtmlOut: false,
    breaks: false,
    langPrefix: 'language-',
    linkify: true,
    typographer: true,
    highlight: function (str, lang) {
        const langLabel = lang || 'text';
        let highlightedCode = '';

        // 标准化语言名称
        const normalizedLang = languageAliases[lang?.toLowerCase()] || lang?.toLowerCase();

        // 尝试使用 Prism 进行高亮
        if (normalizedLang && Prism.languages[normalizedLang]) {
            try {
                highlightedCode = Prism.highlight(str, Prism.languages[normalizedLang], normalizedLang);
            } catch (e) {
                console.warn('Prism highlight failed for language:', normalizedLang, e);
                highlightedCode = md.utils.escapeHtml(str);
            }
        } else {
            if (normalizedLang && normalizedLang !== 'text') {
                console.warn('Language not supported by Prism:', normalizedLang);
            }
            highlightedCode = md.utils.escapeHtml(str);
        }

        // 为每行添加行号
        const lines = highlightedCode.split('\n');
        const numberedLines = lines.map((line, index) => {
            const lineNumber = index + 1;
            return `<span class="code-line"><span class="line-number">${lineNumber}</span><span class="line-content">${line}</span></span>`;
        }).join('\n');

        return '<div class="code-block-wrapper">' +
            '<div class="code-language">' + langLabel + '</div>' +
            '<pre class="language-' + normalizedLang + '"><code class="language-' + normalizedLang + '">' +
            numberedLines +
            '</code></pre>' +
            '</div>';
    }
});

// 添加对 LaTeX 的支持（使用 KaTeX 引擎）
md.use(markdownItTexmath, {
    engine: katex,
    delimiters: 'dollars',
    katexOptions: {
        throwOnError: false,
        errorColor: '#cc0000',
        strict: false
    }
});

// 添加对任务列表的支持
md.use(markdownItTaskLists, { enabled: true });

// 添加对表格的支持
md.use(markdownItMultimdTable);

md.use(markdownItCodeCopy, {
    buttonText: 'copy',
    successText: 'copied',
});

// 自定义插件：在解析前移除 <!-- more --> 标记
md.core.ruler.before('normalize', 'remove_more_tag', function (state) {
    state.src = state.src.replace(/<!--\s*more\s*-->/gi, '');
});

// 自定义插件处理图片路径
md.use((md) => {
    const defaultRender = md.renderer.rules.image || function (tokens, idx, options, env, self) {
        return self.renderToken(tokens, idx, options);
    };

    md.renderer.rules.image = function (tokens, idx, options, env, self) {
        const token = tokens[idx];
        const srcIndex = token.attrIndex('src');
        if (srcIndex >= 0) {
            const src = token.attrs[srcIndex][1];
            token.attrs[srcIndex][1] = resolvePostImageUrl(src);
        }
        return defaultRender(tokens, idx, options, env, self);
    };
});

// 自定义插件处理所有嵌入式组件标记 (Bilibili, Steam, Bangumi, GitHub, Mermaid)
md.use((md) => {
    const defaultFence = md.renderer.rules.fence || function (tokens, idx, options, env, self) {
        return self.renderToken(tokens, idx, options);
    };

    md.renderer.rules.fence = function (tokens, idx, options, env, self) {
        const token = tokens[idx];
        const info = token.info.trim();
        const content = token.content.trim();

        if (info === 'bilibili-video') {
            return `<BilibiliVideoBlock :videoUrl="'${content}'" ></BilibiliVideoBlock>`;
        }
        if (info === 'steam-game') {
            return `<SteamGameBlock :gameUrl="'${content}'" ></SteamGameBlock>`;
        }
        if (info === 'bangumi-card' || info === 'bangumi') {
            return `<BangumiBlock :bangumiUrl="'${content}'" ></BangumiBlock>`;
        }
        if (info === 'github-repo') {
            return `<GithubRepoBlock :repoUrl="'${content}'" ></GithubRepoBlock>`;
        }
        if (info === 'xiaohongshu-note' || info === 'xiaohongshu') {
            return `<XiaohongshuNoteBlock :noteUrl="'${content}'" ></XiaohongshuNoteBlock>`;
        }
        if (info === 'carousel') {
            console.log('[Carousel] Processing carousel block with content:', content);
            // 解析轮播图内容
            const images = [];
            const lines = content.split('\n').filter(line => line.trim());
            console.log('[Carousel] Found lines:', lines);

            for (const line of lines) {
                let imageObj = null;

                // 格式1: Markdown 图片语法 - 支持所有标准格式
                // ![alt](path), ![alt](path "title"), ![alt](<path>), ![alt](<path> "title"), ![alt](<path "title">)
                const mdMatch = line.match(/!\[([^\]]*)\]\(<?([^>\s"]+)>?(?:\s+"([^"]*)")?>?\)/);
                if (mdMatch) {
                    const [, alt, src, title] = mdMatch;
                    const imageSrc = src.startsWith('http') || src.startsWith('/')
                        ? src
                        : `/Posts/Images/${src}`;

                    imageObj = {
                        src: imageSrc,
                        alt: alt || '',
                        title: title || alt || '',
                        description: alt || ''
                    };
                }
                // 格式2: 简化格式 path | description
                else if (line.includes('|')) {
                    const [path, description] = line.split('|').map(s => s.trim());
                    if (path) {
                        const cleanPath = path.trim();
                        const imageSrc = cleanPath.startsWith('http') || cleanPath.startsWith('/')
                            ? cleanPath
                            : `/Posts/Images/${cleanPath}`;

                        imageObj = {
                            src: imageSrc,
                            alt: description || '',
                            title: description || '',
                            description: description || ''
                        };
                    }
                }
                // 格式3: 仅路径（需要验证是图片文件）
                else if (line.trim()) {
                    const cleanPath = line.trim();
                    // 验证是否是有效的图片路径（有图片扩展名或是网络URL）
                    const isValidImagePath = /\.(jpg|jpeg|png|gif|webp|svg|bmp|ico)$/i.test(cleanPath)
                        || cleanPath.startsWith('http')
                        || cleanPath.startsWith('/');

                    if (isValidImagePath) {
                        const imageSrc = cleanPath.startsWith('http') || cleanPath.startsWith('/')
                            ? cleanPath
                            : `/Posts/Images/${cleanPath}`;

                        imageObj = {
                            src: imageSrc,
                            alt: '',
                            title: '',
                            description: ''
                        };
                    }
                }

                if (imageObj) {
                    console.log('[Carousel] Adding image:', imageObj);
                    images.push(imageObj);
                }
            }

            console.log('[Carousel] Total images found:', images.length);
            if (images.length > 0) {
                // 将对象转为 JSON 字符串，并进行 HTML 实体编码以安全地放入属性中
                const imagesJson = JSON.stringify(images).replace(/"/g, '&quot;');
                const result = `<carouselblock :images="${imagesJson}" ></carouselblock>`;
                console.log('[Carousel] Generated HTML:', result);
                return result;
            }
            console.log('[Carousel] No valid images found');
            return '<div class="carousel-error">No valid images found in carousel block</div>';
        }
        if (info === 'mermaid') {
            const uniqueId = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
            return `<div class="mermaid-wrapper"><div id="${uniqueId}" class="mermaid">${md.utils.escapeHtml(content)}</div></div>`;
        }

        return defaultFence(tokens, idx, options, env, self);
    };
});

export default md;
