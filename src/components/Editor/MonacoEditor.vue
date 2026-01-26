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
    }
});

const emit = defineEmits(['update:modelValue', 'scroll', 'change', 'format-request']);

const editorContainer = ref(null);
let editor = null;
let isUpdatingFromProp = false;

// 处理图片上传
const uploadImage = async (file) => {
    try {
        // 获取文章名（去掉.md扩展名）
        const articleName = props.currentFileName.replace(/\.md$/, '') || 'default';

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

        const response = await fetch(`${props.apiBase}/images/upload`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Auth-Token': authToken || ''
            }
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `上传失败: ${response.statusText}`);
        }

        const data = await response.json();
        return data.path; // 返回相对路径，如 "文章名/1.png"
    } catch (error) {
        console.error('[MonacoEditor] 图片上传失败:', error);
        throw error;
    }
};

// 处理粘贴事件
const handlePaste = async (e) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
        const item = items[i];

        // 检查是否为图片
        if (item.type.indexOf('image') !== -1) {
            e.preventDefault();

            const file = item.getAsFile();
            if (!file) continue;

            try {
                // 在编辑器中插入占位符
                const placeholder = '![上传中...](uploading)';
                const position = editor.getPosition();
                editor.executeEdits('paste-image', [{
                    range: {
                        startLineNumber: position.lineNumber,
                        startColumn: position.column,
                        endLineNumber: position.lineNumber,
                        endColumn: position.column
                    },
                    text: placeholder
                }]);

                // 上传图片
                const imagePath = await uploadImage(file);

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

                console.log('[MonacoEditor] 图片上传成功:', imagePath);
            } catch (error) {
                alert(`图片上传失败: ${error.message}`);

                // 移除占位符
                const model = editor.getModel();
                const content = model.getValue();
                const newContent = content.replace('![上传中...](uploading)', '');

                isUpdatingFromProp = true;
                editor.setValue(newContent);
                isUpdatingFromProp = false;
            }
        }
    }
};

// Initialize Monaco Editor
onMounted(() => {
    if (!editorContainer.value) return;

    // Create editor instance
    editor = monaco.editor.create(editorContainer.value, {
        value: props.modelValue,
        language: props.language,
        theme: props.theme,
        automaticLayout: true,
        wordWrap: 'on',
        lineNumbers: 'on',
        minimap: {
            enabled: true
        },
        scrollBeyondLastLine: false,
        fontSize: 14,
        lineHeight: 24,
        fontFamily: "'Monaco', 'Menlo', 'Ubuntu Mono', monospace",
        ...props.options
    });

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
        const scrollTop = e.scrollTop;
        const scrollHeight = editor.getScrollHeight();
        const clientHeight = editorContainer.value?.clientHeight || 0;

        if (scrollHeight > clientHeight) {
            const scrollPercentage = scrollTop / (scrollHeight - clientHeight);
            emit('scroll', scrollPercentage);
        }
    });

    // 添加粘贴事件监听
    const domNode = editor.getDomNode();
    if (domNode) {
        domNode.addEventListener('paste', handlePaste);
    }
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

// Cleanup on unmount
onBeforeUnmount(() => {
    if (editor) {
        const domNode = editor.getDomNode();
        if (domNode) {
            domNode.removeEventListener('paste', handlePaste);
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
}
</style>
