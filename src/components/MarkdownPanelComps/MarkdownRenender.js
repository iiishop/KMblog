import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/sunburst.css'; // 你可以选择其他样式
import markdownItKatex from 'markdown-it-katex';
import 'katex/dist/katex.min.css'; // 引入katex的CSS

// 创建 markdown-it 实例
const md = new MarkdownIt({
    highlight: function (str, lang) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return '<pre class="hljs"><code>' +
                    hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
                    '</code></pre>';
            } catch (__) { }
        }

        return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
    }
});

// 添加对LaTeX的支持
md.use(markdownItKatex);

// 添加自定义规则 - 将*&包裹的文字渲染成红色span
md.use((md) => {
    // 定义一个新的内联规则
    md.inline.ruler.before('emphasis', 'red_text', (state, silent) => {
        const start = state.pos;
        const marker = state.src.charCodeAt(start);

        // 检查是否以*&开头
        if (marker !== 0x2A /* * */ || state.src.charCodeAt(start + 1) !== 0x26 /* & */) {
            return false;
        }

        let pos = start + 2;
        const max = state.posMax;

        // 查找结束标记
        while (pos < max) {
            if (state.src.charCodeAt(pos) === 0x26 /* & */ && state.src.charCodeAt(pos + 1) === 0x2A /* * */) {
                if (!silent) {
                    const token = state.push('red_text_open', 'span', 1);
                    token.attrs = [['style', 'color: red']];
                    token.markup = '*&';

                    token = state.push('text', '', 0);
                    token.content = state.src.slice(start + 2, pos);

                    token = state.push('red_text_close', 'span', -1);
                    token.markup = '&*';
                }
                state.pos = pos + 2;
                return true;
            }
            pos++;
        }

        return false;
    });

    // 定义渲染规则
    md.renderer.rules.red_text_open = (tokens, idx) => {
        return `<span style="color: red;">`;
    };
    md.renderer.rules.red_text_close = (tokens, idx) => {
        return `</span>`;
    };
});

// 自定义插件处理图片路径
md.use((md) => {
    const defaultRender = md.renderer.rules.image || function(tokens, idx, options, env, self) {
        return self.renderToken(tokens, idx, options);
    };

    md.renderer.rules.image = function(tokens, idx, options, env, self) {
        const token = tokens[idx];
        const srcIndex = token.attrIndex('src');
        if (srcIndex >= 0) {
            const src = token.attrs[srcIndex][1];
            if (!src.startsWith('http')) {
                token.attrs[srcIndex][1] = `/src/Posts/Images/${src}`;
            }
        }
        return defaultRender(tokens, idx, options, env, self);
    };
});

export default md;