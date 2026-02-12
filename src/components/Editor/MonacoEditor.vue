<template>
    <div ref="editorContainer" class="monaco-editor-container"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, defineProps, defineEmits } from 'vue';
import * as monaco from 'monaco-editor';
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';

// Configure Monaco Editor workers
self.MonacoEnvironment = {
    getWorker(_, label) {
        return new editorWorker();
    }
};

const props = defineProps({
    modelValue: {
        type: String,
        default: ''
    },
    language: {
        type: String,
        default: 'markdown'
    },
    theme: {
        type: String,
        default: 'vs'
    },
    options: {
        type: Object,
        default: () => ({})
    },
    currentFileName: {
        type: String,
        default: ''
    },
    apiBase: {
        type: String,
        default: 'http://127.0.0.1:8000/api'
    },
    scrollSync: {
        type: Number,
        default: 0
    }
});

const emit = defineEmits(['update:modelValue', 'scroll', 'change', 'format-request']);

const editorContainer = ref(null);
let editor = null;
let isUpdatingFromProp = false;
let isScrollingFromPreview = false; // 标记是否来自预览面板的滚动
let isMobile = false; // 检测是否为移动设备

// 检测移动设备
const detectMobile = () => {
    return window.innerWidth <= 768 ||
        /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

// 获取响应式编辑器配置
const getEditorOptions = () => {
    isMobile = detectMobile();

    const baseOptions = {
        value: props.modelValue,
        language: props.language,
        theme: props.theme,
        automaticLayout: true,
        // 自动换行配置
        wordWrap: 'on',
        wrappingIndent: 'indent',
        wrappingStrategy: 'advanced', // 使用高级换行策略，更智能
        wordWrapBreakAfterCharacters: '\t})]?|/&,;¢°′″‰℃、。｡､￠，．：；？！％・･ゝゞヽヾーァィゥェォッャュョヮヵヶぁぃぅぇぉっゃゅょゎゕゖㇰㇱㇲㇳㇴㇵㇶㇷㇸㇹㇺㇻㇼㇽㇾㇿ々〻ｧｨｩｪｫｬｭｮｯｰ',
        wordWrapBreakBeforeCharacters: '([{\'"〈《「『【〔（［｛｢£¥$£€¤',
        // 滚动条配置
        scrollbar: {
            horizontal: 'hidden',
            vertical: 'auto',
            verticalScrollbarSize: 10,
            horizontalScrollbarSize: 0,
            useShadows: false,
            verticalHasArrows: false,
            horizontalHasArrows: false,
            verticalSliderSize: 10,
            horizontalSliderSize: 10
        },
        // 内边距配置
        padding: {
            top: 16,
            bottom: 200,
            right: 0,
            left: 0
        },
        // 行号和边距配置
        lineNumbers: 'on',
        lineNumbersMinChars: 3,
        glyphMargin: true,
        folding: true,
        lineDecorationsWidth: 10,
        // 其他编辑器选项
        scrollBeyondLastLine: true,
        smoothScrolling: true,
        cursorBlinking: 'smooth',
        cursorSmoothCaretAnimation: 'on',
        fontFamily: "'Cascadia Code', 'Fira Code', 'Monaco', 'Menlo', 'Consolas', 'Ubuntu Mono', monospace",
        fontLigatures: true,
        renderWhitespace: 'selection',
        renderControlCharacters: false,
        bracketPairColorization: {
            enabled: true
        },
        guides: {
            bracketPairs: true,
            indentation: true
        },
        suggest: {
            showWords: true,
            showSnippets: true
        },
        quickSuggestions: {
            other: true,
            comments: false,
            strings: false
        },
        acceptSuggestionOnCommitCharacter: true,
        acceptSuggestionOnEnter: 'on',
        tabCompletion: 'on',
        ...props.options
    };

    if (isMobile) {
        // 移动端优化配置
        return {
            ...baseOptions,
            fontSize: 14,
            lineHeight: 22,
            tabSize: 2,
            insertSpaces: true,
            // 移动端关闭 minimap
            minimap: {
                enabled: false
            },
            lineNumbersMinChars: 3,
            glyphMargin: false,
            folding: true,
            foldingStrategy: 'indentation',
            lineDecorationsWidth: 5,
            renderLineHighlight: 'line',
            overviewRulerLanes: 0,
            // 移动端交互优化
            mouseWheelZoom: false,
            contextmenu: true,
            snippetSuggestions: 'bottom',
            hover: {
                enabled: true,
                delay: 300,
                sticky: true
            },
            links: true,
            colorDecorators: false,
            scrollPredominantAxis: true
        };
    } else {
        // 桌面端配置
        return {
            ...baseOptions,
            fontSize: 14,
            lineHeight: 24,
            tabSize: 4,
            insertSpaces: true,
            // 桌面端 minimap 配置（标准右侧位置）
            minimap: {
                enabled: true,
                side: 'right',
                showSlider: 'mouseover',
                renderCharacters: false,
                maxColumn: 120,
                scale: 1
            },
            lineNumbersMinChars: 4,
            glyphMargin: true,
            folding: true,
            foldingStrategy: 'auto',
            lineDecorationsWidth: 10,
            overviewRulerLanes: 0,
            overviewRulerBorder: false,
            // 桌面端增强功能
            mouseWheelZoom: true,
            contextmenu: true,
            snippetSuggestions: 'inline',
            hover: {
                enabled: true,
                delay: 300,
                sticky: true
            },
            links: true,
            colorDecorators: true,
            dragAndDrop: true,
            copyWithSyntaxHighlighting: true,
            multiCursorModifier: 'ctrlCmd',
            multiCursorPaste: 'spread',
            formatOnPaste: false,
            formatOnType: false
        };
    }
};

// 处理图片上传
const uploadImage = async (file) => {
    try {
        console.log('[MonacoEditor] 开始上传图片...');
        console.log('[MonacoEditor] 文件名:', file.name);
        console.log('[MonacoEditor] 文件类型:', file.type);
        console.log('[MonacoEditor] 文件大小:', file.size, 'bytes');

        // 获取文章名（去掉.md扩展名和路径前缀）
        let articleName = props.currentFileName.replace(/\.md$/, '');
        // 移除路径前缀（如 /Posts/Markdowns/）
        articleName = articleName.split('/').pop() || 'default';

        console.log('[MonacoEditor] 文章名:', articleName);

        const formData = new FormData();
        formData.append('image', file);
        formData.append('article_name', articleName);

        // 从URL获取token
        const getHashParams = () => {
            const hash = window.location.hash;
            const queryString = hash.split('?')[1];
            if (!queryString) return new URLSearchParams();
            return new URLSearchParams(queryString);
        };
        const urlParams = getHashParams();
        const authToken = urlParams.get('token');

        console.log('[MonacoEditor] Auth token:', authToken ? '已获取' : '未找到');
        console.log('[MonacoEditor] API Base:', props.apiBase);

        const uploadUrl = `${props.apiBase}/images/upload`;
        console.log('[MonacoEditor] 上传URL:', uploadUrl);

        const response = await fetch(uploadUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Auth-Token': authToken || ''
            }
        });

        console.log('[MonacoEditor] 响应状态:', response.status);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('[MonacoEditor] 上传失败响应:', errorData);
            throw new Error(errorData.detail || `上传失败: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('[MonacoEditor] 上传成功响应:', data);

        // 返回相对路径（相对于 Images 目录）
        // 后端返回 "文章名/1.png"，直接使用即可
        const imagePath = data.path;
        console.log('[MonacoEditor] 最终图片路径:', imagePath);

        return imagePath;
    } catch (error) {
        console.error('[MonacoEditor] 图片上传失败:', error);
        throw error;
    }
};

// 处理粘贴事件
const handlePaste = async (e) => {
    console.log('='.repeat(50));
    console.log('[MonacoEditor] ✅ 粘贴事件触发！');
    console.log('[MonacoEditor] 事件对象:', e);
    console.log('[MonacoEditor] 事件类型:', e.type);
    console.log('[MonacoEditor] 时间戳:', new Date().toISOString());

    const items = e.clipboardData?.items;
    if (!items) {
        console.log('[MonacoEditor] ❌ 没有剪贴板数据');
        console.log('[MonacoEditor] clipboardData:', e.clipboardData);
        return;
    }

    console.log('[MonacoEditor] 剪贴板项目数量:', items.length);

    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        console.log(`[MonacoEditor] 项目 ${i}:`, item.type, item.kind);

        // 检查是否为图片
        if (item.type.indexOf('image') !== -1) {
            console.log('[MonacoEditor] 🎉 检测到图片！');
            console.log('[MonacoEditor] 阻止默认行为');
            e.preventDefault();
            e.stopPropagation();

            const file = item.getAsFile();
            if (!file) {
                console.log('[MonacoEditor] ❌ 无法获取文件对象');
                continue;
            }

            console.log('[MonacoEditor] ✅ 文件对象获取成功');
            console.log('[MonacoEditor] 文件信息:', {
                name: file.name,
                type: file.type,
                size: file.size
            });

            try {
                // 在编辑器中插入占位符
                const placeholder = '![上传中...](uploading)';
                const position = editor.getPosition();
                console.log('[MonacoEditor] 当前光标位置:', position);

                editor.executeEdits('paste-image', [{
                    range: {
                        startLineNumber: position.lineNumber,
                        startColumn: position.column,
                        endLineNumber: position.lineNumber,
                        endColumn: position.column
                    },
                    text: placeholder
                }]);

                console.log('[MonacoEditor] 占位符已插入，开始上传...');

                // 上传图片
                const imagePath = await uploadImage(file);

                console.log('[MonacoEditor] 图片上传完成，路径:', imagePath);

                // 替换占位符为实际的图片引用
                const model = editor.getModel();
                const content = model.getValue();
                const newContent = content.replace(placeholder, `![图片](${imagePath})`);

                isUpdatingFromProp = true;
                editor.setValue(newContent);
                isUpdatingFromProp = false;

                // 触发change事件
                emit('update:modelValue', newContent);
                emit('change', newContent);

                console.log('[MonacoEditor] ✅ 图片引用已插入到编辑器');
                console.log('='.repeat(50));
            } catch (error) {
                console.error('[MonacoEditor] ❌ 图片上传失败:', error);
                alert(`图片上传失败: ${error.message}`);

                // 移除占位符
                const model = editor.getModel();
                const content = model.getValue();
                const newContent = content.replace('![上传中...](uploading)', '');

                isUpdatingFromProp = true;
                editor.setValue(newContent);
                isUpdatingFromProp = false;
            }
        } else {
            console.log(`[MonacoEditor] 项目 ${i} 不是图片，跳过`);
        }
    }
};

// Initialize Monaco Editor
onMounted(() => {
    console.log('[MonacoEditor] onMounted - 开始初始化');

    if (!editorContainer.value) {
        console.error('[MonacoEditor] editorContainer.value 不存在！');
        return;
    }

    console.log('[MonacoEditor] editorContainer 存在，创建编辑器...');
    console.log('[MonacoEditor] 检测到设备类型:', detectMobile() ? '移动端' : '桌面端');

    // Create editor instance with responsive options
    editor = monaco.editor.create(editorContainer.value, getEditorOptions());

    // 延迟触发布局计算，确保正确渲染
    setTimeout(() => {
        if (editor) {
            editor.layout();
            console.log('[MonacoEditor] 布局已重新计算');
        }
    }, 50);

    // 注册右键菜单
    editor.addAction({
        id: 'format-bold',
        label: '粗体',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyB],
        contextMenuGroupId: 'format',
        contextMenuOrder: 1,
        run: () => emit('format-request', 'bold')
    });

    editor.addAction({
        id: 'format-italic',
        label: '斜体',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyI],
        contextMenuGroupId: 'format',
        contextMenuOrder: 2,
        run: () => emit('format-request', 'italic')
    });

    editor.addAction({
        id: 'format-strikethrough',
        label: '删除线',
        contextMenuGroupId: 'format',
        contextMenuOrder: 3,
        run: () => emit('format-request', 'strikethrough')
    });

    editor.addAction({
        id: 'format-underline',
        label: '下划线',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyU],
        contextMenuGroupId: 'format',
        contextMenuOrder: 4,
        run: () => emit('format-request', 'underline')
    });

    editor.addAction({
        id: 'format-code',
        label: '代码块',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyK],
        contextMenuGroupId: 'format',
        contextMenuOrder: 5,
        run: () => emit('format-request', 'code')
    });

    editor.addAction({
        id: 'format-inline-code',
        label: '行内代码',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Backquote],
        contextMenuGroupId: 'format',
        contextMenuOrder: 6,
        run: () => emit('format-request', 'inline-code')
    });

    editor.addAction({
        id: 'insert-heading-1',
        label: '一级标题',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Digit1],
        contextMenuGroupId: 'heading',
        contextMenuOrder: 1,
        run: () => emit('format-request', 'heading-1')
    });

    editor.addAction({
        id: 'insert-heading-2',
        label: '二级标题',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Digit2],
        contextMenuGroupId: 'heading',
        contextMenuOrder: 2,
        run: () => emit('format-request', 'heading-2')
    });

    editor.addAction({
        id: 'insert-heading-3',
        label: '三级标题',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Digit3],
        contextMenuGroupId: 'heading',
        contextMenuOrder: 3,
        run: () => emit('format-request', 'heading-3')
    });

    editor.addAction({
        id: 'insert-quote',
        label: '引用',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyQ],
        contextMenuGroupId: 'structure',
        contextMenuOrder: 1,
        run: () => emit('format-request', 'quote')
    });

    editor.addAction({
        id: 'insert-link',
        label: '插入链接',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyL],
        contextMenuGroupId: 'structure',
        contextMenuOrder: 2,
        run: () => emit('format-request', 'link')
    });

    editor.addAction({
        id: 'insert-image',
        label: '插入图片',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyI],
        contextMenuGroupId: 'structure',
        contextMenuOrder: 3,
        run: () => emit('format-request', 'image')
    });

    editor.addAction({
        id: 'insert-ul',
        label: '无序列表',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyU],
        contextMenuGroupId: 'list',
        contextMenuOrder: 1,
        run: () => emit('format-request', 'ul')
    });

    editor.addAction({
        id: 'insert-ol',
        label: '有序列表',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyO],
        contextMenuGroupId: 'list',
        contextMenuOrder: 2,
        run: () => emit('format-request', 'ol')
    });

    editor.addAction({
        id: 'insert-task',
        label: '任务列表',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyT],
        contextMenuGroupId: 'list',
        contextMenuOrder: 3,
        run: () => emit('format-request', 'task')
    });

    editor.addAction({
        id: 'insert-table',
        label: '插入表格',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyB],
        contextMenuGroupId: 'structure',
        contextMenuOrder: 4,
        run: () => emit('format-request', 'table')
    });

    editor.addAction({
        id: 'insert-hr',
        label: '分隔线',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyH],
        contextMenuGroupId: 'structure',
        contextMenuOrder: 5,
        run: () => emit('format-request', 'hr')
    });

    editor.addAction({
        id: 'align-center',
        label: '居中对齐',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyE],
        contextMenuGroupId: 'align',
        contextMenuOrder: 1,
        run: () => emit('format-request', 'align-center')
    });

    editor.addAction({
        id: 'align-left',
        label: '左对齐',
        contextMenuGroupId: 'align',
        contextMenuOrder: 2,
        run: () => emit('format-request', 'align-left')
    });

    editor.addAction({
        id: 'align-right',
        label: '右对齐',
        contextMenuGroupId: 'align',
        contextMenuOrder: 3,
        run: () => emit('format-request', 'align-right')
    });

    // Listen to content changes
    editor.onDidChangeModelContent(() => {
        if (!isUpdatingFromProp) {
            const value = editor.getValue();
            emit('update:modelValue', value);
            emit('change', value);
        }
    });

    // Listen to scroll events
    editor.onDidScrollChange((e) => {
        if (isScrollingFromPreview) return; // 如果是预览面板触发的滚动，忽略

        const scrollTop = e.scrollTop;
        const scrollHeight = editor.getScrollHeight();
        const clientHeight = editorContainer.value?.clientHeight || 0;

        if (scrollHeight > clientHeight) {
            const scrollPercentage = scrollTop / (scrollHeight - clientHeight);
            emit('scroll', scrollPercentage);
        }
    });

    // 添加粘贴事件监听 - 使用捕获阶段拦截 Monaco 的默认行为
    console.log('[MonacoEditor] 开始注册粘贴事件监听器...');

    // 策略 1: 在捕获阶段拦截粘贴事件（比 Monaco 的冒泡阶段监听器更早）
    const domNode = editor.getDomNode();
    if (domNode) {
        console.log('[MonacoEditor] 找到编辑器 DOM 节点，绑定粘贴事件（捕获阶段）');
        // 使用 capture: true 在捕获阶段拦截
        domNode.addEventListener('paste', handlePaste, { capture: true });
        console.log('[MonacoEditor] 粘贴事件已绑定到编辑器 DOM（捕获阶段）');
    } else {
        console.error('[MonacoEditor] 无法获取编辑器 DOM 节点！');
    }

    // 策略 2: 延迟绑定到 textarea（Monaco 的实际输入元素）
    setTimeout(() => {
        const textArea = domNode?.querySelector('textarea');
        if (textArea) {
            console.log('[MonacoEditor] 找到 textarea，直接绑定粘贴事件（捕获阶段）');
            textArea.addEventListener('paste', handlePaste, { capture: true });
        } else {
            console.log('[MonacoEditor] 未找到 textarea');
        }
    }, 100);

    // 策略 3: 全局监听器（用于调试和备用）
    const globalPasteHandler = (e) => {
        console.log('[MonacoEditor] 全局粘贴事件触发（捕获阶段）');
        console.log('[MonacoEditor] 事件目标:', e.target?.tagName, e.target?.className);

        // 检查是否是在编辑器内粘贴
        if (domNode && domNode.contains(e.target)) {
            console.log('[MonacoEditor] 粘贴发生在编辑器内');
            const items = e.clipboardData?.items;
            if (items) {
                for (let i = 0; i < items.length; i++) {
                    console.log(`[MonacoEditor] 剪贴板项目 ${i}:`, items[i].type);
                    if (items[i].type.indexOf('image') !== -1) {
                        console.log('[MonacoEditor] 检测到图片，立即调用 handlePaste');
                        // 直接调用 handlePaste 处理图片
                        handlePaste(e);
                        break;
                    }
                }
            }
        }
    };
    window.addEventListener('paste', globalPasteHandler, { capture: true });

    console.log('[MonacoEditor] 所有粘贴事件监听器已注册');

    // 监听窗口大小变化，动态调整编辑器配置
    const handleResize = () => {
        const wasMobile = isMobile;
        const nowMobile = detectMobile();

        if (wasMobile !== nowMobile) {
            console.log('[MonacoEditor] 设备类型变化，更新编辑器配置');
            isMobile = nowMobile;

            // 更新编辑器配置
            if (editor) {
                const options = getEditorOptions();
                editor.updateOptions(options);
                // 强制重新布局
                setTimeout(() => editor.layout(), 50);
            }
        } else if (editor) {
            // 即使设备类型未变化，也需要重新布局以适应窗口大小变化
            editor.layout();
        }
    };

    window.addEventListener('resize', handleResize);

    // 保存清理函数
    editor._resizeHandler = handleResize;
});

// Watch for external value changes
watch(() => props.modelValue, (newValue) => {
    if (editor && editor.getValue() !== newValue) {
        isUpdatingFromProp = true;
        const position = editor.getPosition();
        editor.setValue(newValue);
        if (position) {
            editor.setPosition(position);
        }
        isUpdatingFromProp = false;
    }
});

// Watch for theme changes
watch(() => props.theme, (newTheme) => {
    if (editor) {
        monaco.editor.setTheme(newTheme);
    }
});

// Watch for language changes
watch(() => props.language, (newLanguage) => {
    if (editor) {
        const model = editor.getModel();
        if (model) {
            monaco.editor.setModelLanguage(model, newLanguage);
        }
    }
});

// Watch for scroll sync from preview panel
watch(() => props.scrollSync, (scrollPercentage) => {
    if (editor && editorContainer.value) {
        isScrollingFromPreview = true;
        const scrollHeight = editor.getScrollHeight();
        const clientHeight = editorContainer.value.clientHeight;
        const maxScroll = scrollHeight - clientHeight;
        const targetScrollTop = maxScroll * scrollPercentage;

        editor.setScrollTop(targetScrollTop);

        // 重置标记
        setTimeout(() => {
            isScrollingFromPreview = false;
        }, 100);
    }
});

// Cleanup on unmount
onBeforeUnmount(() => {
    if (editor) {
        const domNode = editor.getDomNode();
        if (domNode) {
            domNode.removeEventListener('paste', handlePaste);
        }

        // 移除 resize 监听器
        if (editor._resizeHandler) {
            window.removeEventListener('resize', editor._resizeHandler);
        }

        editor.dispose();
        editor = null;
    }
});

// Expose editor instance for parent component
defineExpose({
    getEditor: () => editor,
    focus: () => editor?.focus(),
    getValue: () => editor?.getValue() || '',
    setValue: (value) => {
        if (editor) {
            editor.setValue(value);
        }
    },
    insertText: (text) => {
        if (editor) {
            const selection = editor.getSelection();
            const id = { major: 1, minor: 1 };
            const op = {
                identifier: id,
                range: selection,
                text: text,
                forceMoveMarkers: true
            };
            editor.executeEdits('insert-text', [op]);
            editor.focus();
        }
    }
});
</script>

<style scoped>
.monaco-editor-container {
    width: 100%;
    height: 100%;
    overflow: hidden;
    /* ✅ 确保容器不压榨编辑器内容区 */
    padding: 0;
    margin: 0;
    box-sizing: border-box;
    min-width: 300px;
}

/* ✅ 可选：如果想要 minimap 在右侧，取消下面注释来收窄 minimap 宽度 */
/*
.monaco-editor-container :deep(.monaco-editor .minimap) {
    width: 60px !important;
}
*/

/* ✅ 减少垂直滚动条占位，给内容区更多空间 */
.monaco-editor-container :deep(.monaco-editor .scrollbar.vertical) {
    width: 8px !important;
}

/* 修复 minimap 遮挡内容的问题 */
.monaco-editor-container :deep(.monaco-editor .minimap) {
    pointer-events: auto;
    z-index: 1;
}

.monaco-editor-container :deep(.monaco-scrollable-element.editor-scrollable) {
    z-index: 0;
}

/* 确保滚动条在正确的层级 */
.monaco-editor-container :deep(.monaco-scrollable-element .scrollbar) {
    z-index: 2;
}

/* 确保 minimap 不会遮挡文字内容 */
.monaco-editor-container :deep(.monaco-editor .overflow-guard) {
    position: relative;
}

/* 确保内容区域布局正确 */
.monaco-editor-container :deep(.monaco-editor .lines-content) {
    overflow: visible;
}

/* 优化行渲染 */
.monaco-editor-container :deep(.monaco-editor .view-lines) {
    box-sizing: border-box;
}

/* 优化光标显示 */
.monaco-editor-container :deep(.monaco-editor .cursor) {
    animation: cursor-blink 1s step-end infinite;
}

@keyframes cursor-blink {

    0%,
    50% {
        opacity: 1;
    }

    50.01%,
    100% {
        opacity: 0;
    }
}

/* 移动端优化 */
@media (max-width: 768px) {
    .monaco-editor-container {
        touch-action: pan-y;
        -webkit-overflow-scrolling: touch;
    }

    /* 移动端隐藏不必要的元素 */
    .monaco-editor-container :deep(.monaco-editor .minimap) {
        display: none !important;
    }

    /* 优化滚动条 */
    .monaco-editor-container :deep(.monaco-scrollable-element .scrollbar.vertical) {
        width: 8px !important;
    }

    /* 优化光标 */
    .monaco-editor-container :deep(.monaco-editor .cursor) {
        width: 2px !important;
    }

    /* 优化行高 */
    .monaco-editor-container :deep(.monaco-editor .view-line) {
        min-height: 22px;
    }

    /* 优化选中效果 */
    .monaco-editor-container :deep(.monaco-editor .selected-text) {
        background-color: rgba(100, 149, 237, 0.3) !important;
    }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
    .monaco-editor-container {
        -webkit-overflow-scrolling: touch;
        user-select: text;
        -webkit-user-select: text;
    }

    /* 增加触摸目标大小 */
    .monaco-editor-container :deep(.monaco-editor .view-line) {
        min-height: 28px;
        padding: 2px 0;
    }

    /* 优化触摸滚动 */
    .monaco-editor-container :deep(.monaco-scrollable-element) {
        touch-action: pan-y;
    }
}

/* 高分辨率屏幕优化 */
@media (-webkit-min-device-pixel-ratio: 2),
(min-resolution: 192dpi) {
    .monaco-editor-container :deep(.monaco-editor) {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
}

/* 优化滚动条外观 */
.monaco-editor-container :deep(.monaco-editor .scrollbar.vertical) {
    width: 8px !important;
    opacity: 0.6;
    transition: opacity 0.2s ease;
}

.monaco-editor-container :deep(.monaco-editor .scrollbar.vertical:hover) {
    opacity: 1;
}

/* 深色模式优化 */
@media (prefers-color-scheme: dark) {
    .monaco-editor-container :deep(.monaco-editor .scroll-decoration) {
        box-shadow: none;
    }
}
</style>
