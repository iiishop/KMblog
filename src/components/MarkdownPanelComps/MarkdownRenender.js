import MarkdownIt from 'markdown-it';
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
import mermaid from 'mermaid';

// 获取当前主题
function getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'day';
}

// 根据主题返回 Mermaid 配置
function getMermaidThemeConfig(theme) {
    const isDark = theme === 'dark' || theme === 'night';

    if (isDark) {
        // 深色主题配置 - 极致优雅
        return {
            theme: 'dark',
            themeVariables: {
                // 基础颜色 - 深色模式
                primaryColor: '#1e293b',
                primaryTextColor: '#f1f5f9',
                primaryBorderColor: '#818cf8',
                lineColor: '#94a3b8',
                secondaryColor: '#312e81',
                tertiaryColor: '#1e1e1e',

                // 流程图
                mainBkg: '#1e293b',
                nodeBorder: '#818cf8',
                clusterBkg: '#0f172a',
                clusterBorder: '#475569',

                // 序列图
                actorBkg: '#312e81',
                actorBorder: '#818cf8',
                actorTextColor: '#f1f5f9',
                signalColor: '#cbd5e1',
                signalTextColor: '#f1f5f9',
                labelBoxBkgColor: '#1e293b',
                labelBoxBorderColor: '#475569',
                labelTextColor: '#f1f5f9',

                // Gantt 图专属配置
                gridColor: '#334155',
                todayLineColor: '#818cf8',

                // 任务条颜色
                taskBkgColor: '#3b82f6',
                taskBorderColor: '#2563eb',
                taskTextColor: '#ffffff',
                taskTextOutsideColor: '#f1f5f9',
                taskTextLightColor: '#1e293b',
                taskTextDarkColor: '#f1f5f9',

                // Section 颜色
                sectionBkgColor: '#1e293b',
                sectionBkgColor2: '#312e81',
                altSectionBkgColor: '#0f172a',

                // 已完成任务
                doneTaskBkgColor: '#10b981',
                doneTaskBorderColor: '#059669',

                // 进行中任务
                activeTaskBkgColor: '#3b82f6',
                activeTaskBorderColor: '#2563eb',

                // 重要任务
                critBkgColor: '#ef4444',
                critBorderColor: '#dc2626',

                // 文字颜色
                textColor: '#f1f5f9',
                fontSize: '16px',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji"'
            }
        };
    } else {
        // 浅色主题配置 - 极致优雅
        return {
            theme: 'base',
            themeVariables: {
                // 基础颜色 - 浅色模式
                primaryColor: '#eef2ff',
                primaryTextColor: '#1e293b',
                primaryBorderColor: '#6366f1',
                lineColor: '#64748b',
                secondaryColor: '#fdf2f8',
                tertiaryColor: '#ffffff',

                // 流程图
                mainBkg: '#eef2ff',
                nodeBorder: '#6366f1',
                clusterBkg: '#f9fafb',
                clusterBorder: '#d1d5db',

                // 序列图
                actorBkg: '#e0e7ff',
                actorBorder: '#6366f1',
                actorTextColor: '#1e293b',
                signalColor: '#475569',
                signalTextColor: '#0f172a',
                labelBoxBkgColor: '#ffffff',
                labelBoxBorderColor: '#e5e7eb',
                labelTextColor: '#1e293b',

                // Gantt 图专属配置
                gridColor: '#e2e8f0',
                todayLineColor: '#6366f1',

                // 任务条颜色
                taskBkgColor: '#3b82f6',
                taskBorderColor: '#2563eb',
                taskTextColor: '#ffffff',
                taskTextOutsideColor: '#1e293b',
                taskTextLightColor: '#ffffff',
                taskTextDarkColor: '#1e293b',

                // Section 颜色
                sectionBkgColor: '#f8fafc',
                sectionBkgColor2: '#f1f5f9',
                altSectionBkgColor: '#ffffff',

                // 已完成任务
                doneTaskBkgColor: '#10b981',
                doneTaskBorderColor: '#059669',

                // 进行中任务
                activeTaskBkgColor: '#3b82f6',
                activeTaskBorderColor: '#2563eb',

                // 重要任务
                critBkgColor: '#ef4444',
                critBorderColor: '#dc2626',

                // 文字颜色
                textColor: '#1e293b',
                fontSize: '16px',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji"'
            }
        };
    }
}

// 初始化 mermaid
function initializeMermaid() {
    const currentTheme = getCurrentTheme();
    const themeConfig = getMermaidThemeConfig(currentTheme);

    mermaid.initialize({
        startOnLoad: true,
        securityLevel: 'loose',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
        // 宽度适配配置
        maxWidth: '100%',
        useMaxWidth: true,
        ...themeConfig,
        flowchart: {
            curve: 'basis',
            htmlLabels: true,
            useMaxWidth: true,
            padding: 20
        },
        gantt: {
            useWidth: undefined,
            numberSectionStyles: 6,
            axisFormat: '%m-%d',
            topPadding: 50,
            sidePadding: 75,
            gridLineStartPadding: 10,
            fontSize: 14,
            sectionFontSize: 16,
            numberSectionStyles: 4,
            // 任务高度和间距
            barHeight: 32,
            barGap: 8,
            topAxis: true,
            // 左侧标签宽度
            leftPadding: 200
        },
        sequence: {
            diagramMarginX: 50,
            diagramMarginY: 30,
            actorMargin: 80,
            width: 200,
            height: 65,
            boxMargin: 15,
            boxTextMargin: 8,
            noteMargin: 15,
            messageMargin: 50
        },
        pie: {
            textPosition: 0.65
        },
        class: {
            padding: 20
        }
    });
}

// 初始化
initializeMermaid();

// 监听主题变化
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
            console.log('[Mermaid] Theme changed, reinitializing...');
            initializeMermaid();
            // 重新渲染所有 mermaid 图表
            document.querySelectorAll('.mermaid').forEach((element) => {
                if (element.getAttribute('data-processed')) {
                    element.removeAttribute('data-processed');
                    mermaid.init(undefined, element);
                }
            });
        }
    });
});

observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme']
});

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
            if (!src.startsWith('http')) {
                // 先解码再编码，避免双重编码
                const decodedSrc = decodeURIComponent(src);
                const encodedSrc = encodeURI(decodedSrc);
                token.attrs[srcIndex][1] = `/Posts/Images/${encodedSrc}`;
            }
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
            return `<div class="mermaid-wrapper"><div id="${uniqueId}" class="mermaid">${content}</div></div>`;
        }

        return defaultFence(tokens, idx, options, env, self);
    };
});

export default md;