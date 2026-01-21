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

import markdownItKatex from 'markdown-it-katex';
import 'katex/dist/katex.min.css'; // 引入katex的CSS
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

// 添加对LaTeX的支持
md.use(markdownItKatex);

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

// 自定义插件处理 steam-game 标记
md.use((md) => {
    const defaultFence = md.renderer.rules.fence || function (tokens, idx, options, env, self) {
        return self.renderToken(tokens, idx, options);
    };

    md.renderer.rules.fence = function (tokens, idx, options, env, self) {
        const token = tokens[idx];
        if (token.info.trim() === 'steam-game') {
            const url = token.content.trim();
            return `<SteamGameBlock :gameUrl="'${url}'" ></SteamGameBlock>`;
        }
        return defaultFence(tokens, idx, options, env, self);
    };
});

// 自定义插件处理 bangumi 标记
md.use((md) => {
    const defaultFence = md.renderer.rules.fence || function (tokens, idx, options, env, self) {
        return self.renderToken(tokens, idx, options);
    };

    md.renderer.rules.fence = function (tokens, idx, options, env, self) {
        const token = tokens[idx];
        if (token.info.trim() === 'bangumi') {
            const url = token.content.trim();
            return `<BangumiBlock :bangumiUrl="'${url}'" ></BangumiBlock>`;
        }
        return defaultFence(tokens, idx, options, env, self);
    };
});
export default md;