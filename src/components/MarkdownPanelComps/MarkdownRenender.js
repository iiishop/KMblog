import MarkdownIt from 'markdown-it';

// 创建 markdown-it 实例
const md = new MarkdownIt();

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

// 你可以在这里添加更多的自定义规则和插件

export default md;