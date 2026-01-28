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
        // 深色主题配置
        return {
            theme: 'dark',
            themeVariables: {
                // 基础颜色 - 深色模式
                primaryColor: '#1e293b',          // 节点背景色 (深蓝灰)
                primaryTextColor: '#e2e8f0',      // 节点文字颜色 (浅灰)
                primaryBorderColor: '#818cf8',    // 节点边框 (靛蓝)
                lineColor: '#94a3b8',             // 连线颜色 (浅灰)
                secondaryColor: '#312e81',        // 次要节点背景
                tertiaryColor: '#1e1e1e',         // 第三级背景

                // 流程图特定
                mainBkg: '#1e293b',
                nodeBorder: '#818cf8',
                clusterBkg: '#0f172a',            // 子图背景
                clusterBorder: '#475569',

                // 序列图特定
                actorBkg: '#312e81',
                actorBorder: '#818cf8',
                actorTextColor: '#e2e8f0',
                signalColor: '#cbd5e1',
                signalTextColor: '#f1f5f9',
                labelBoxBkgColor: '#1e293b',
                labelBoxBorderColor: '#475569',
                labelTextColor: '#e2e8f0',

                // 文字颜色
                textColor: '#e2e8f0',
                fontSize: '15px',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
            }
        };
    } else {
        // 浅色主题配置
        return {
            theme: 'base',
            themeVariables: {
                // 基础颜色 - 浅色模式
                primaryColor: '#eef2ff',          // 节点背景色 (极浅的靛蓝)
                primaryTextColor: '#374151',      // 节点文字颜色 (深灰)
                primaryBorderColor: '#818cf8',    // 节点边框 (柔和的靛蓝)
                lineColor: '#6b7280',             // 连线颜色 (灰色)
                secondaryColor: '#fdf2f8',        // 次要节点背景
                tertiaryColor: '#fff',            // 第三级背景

                // 流程图特定
                mainBkg: '#eef2ff',
                nodeBorder: '#818cf8',
                clusterBkg: '#f9fafb',            // 子图背景
                clusterBorder: '#d1d5db',

                // 序列图特定
                actorBkg: '#e0e7ff',
                actorBorder: '#6366f1',
                actorTextColor: '#1f2937',
                signalColor: '#374151',
                signalTextColor: '#111827',
                labelBoxBkgColor: '#ffffff',
                labelBoxBorderColor: '#e5e7eb',

                // 文字颜色
                textColor: '#374151',
                fontSize: '15px',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
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
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        // 宽度适配配置
        maxWidth: '100%',
        useMaxWidth: true,
        ...themeConfig,
        flowchart: {
            curve: 'basis', // 更平滑的曲线
            htmlLabels: true,
            useMaxWidth: true
        },
        gantt: {
            useWidth: undefined, // 让 Gantt 使用容器宽度
            numberSectionStyles: 4,
            gridLineStartPadding: '350px' // 确保标签有足够空间
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
                token.attrs[srcIndex][1] = `/Posts/Images/${src}`;
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
        if (info === 'mermaid') {
            const uniqueId = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
            return `<div class="mermaid-wrapper"><div id="${uniqueId}" class="mermaid">${content}</div></div>`;
        }

        return defaultFence(tokens, idx, options, env, self);
    };
});

export default md;