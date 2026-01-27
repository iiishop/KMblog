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
        // 禁用 Monaco 的智能粘贴功能，让我们自己处理
        'bracketPairColorization.enabled': false,
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
