<template>
    <div v-if="!shouldHideNode" class="ethereal-node" :style="{ '--node-depth': depth }">
        <div class="node-content" :class="{
            'is-folder': node.type === 'folder',
            'is-file': node.type === 'file',
            'is-current': isCurrentFile,
            'is-expanded': isExpanded,
            'is-dragging': isDragging,
            'is-drag-over': isDragOver,
            'is-waterfall-folder': isWaterfallFolder
        }" @click="handleClick" @contextmenu.prevent="handleContextMenu" :draggable="node.type === 'file'"
            @dragstart="handleDragStart" @dragend="handleDragEnd" @dragover="handleDragOver"
            @dragleave="handleDragLeave" @drop="handleDrop" @mouseenter="handleMouseEnter"
            @mouseleave="handleMouseLeave">

            <!-- 树状层级线 -->
            <div class="tree-lines" v-if="depth > 0">
                <div class="vertical-line"></div>
                <div class="horizontal-line"></div>
            </div>

            <!-- 选中指示器 -->
            <div class="selection-indicator"></div>

            <!-- 文件夹图标/展开箭头 -->
            <div v-if="node.type === 'folder'" class="node-icon folder-icon">
                <svg class="expand-arrow" :class="{ 'expanded': isExpanded }" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M10 17l5-5-5-5v10z" />
                </svg>
                <!-- WaterfallGraph 特殊图标 -->
                <svg v-if="isWaterfallFolder" class="folder-svg waterfall-icon" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2">
                    <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
                    <rect x="8" y="10" width="3" height="6" rx="0.5" opacity="0.7" />
                    <rect x="12" y="8" width="3" height="8" rx="0.5" opacity="0.8" />
                    <rect x="16" y="11" width="3" height="5" rx="0.5" opacity="0.6" />
                </svg>
                <!-- 普通文件夹图标 -->
                <svg v-else class="folder-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
                </svg>
            </div>

            <!-- 文件图标 -->
            <div v-else class="node-icon file-icon" :class="{ 'is-image': isImageFile }">
                <!-- 34.1 创建图片文件 SVG 图标 -->
                <svg v-if="isImageFile" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21 15 16 10 5 21" />
                </svg>
                <!-- 普通文件图标 -->
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                </svg>
            </div>

            <!-- 节点名称 -->
            <span class="node-name">{{ node.name }}</span>

            <!-- 拖拽提示 -->
            <div v-if="isDragOver" class="drop-hint">
                <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
                </svg>
            </div>
        </div>

        <!-- 图片悬停预览 -->
        <teleport to="body">
            <transition name="preview-fade">
                <div v-if="showImagePreview && isImageFile" class="image-preview-tooltip" :style="imagePreviewStyle">
                    <div class="preview-backdrop"></div>
                    <div class="preview-content">
                        <img :src="imagePreviewUrl" :alt="node.name" @error="handleImageError" />
                        <div class="preview-filename">{{ node.name }}</div>
                    </div>
                </div>
            </transition>
        </teleport>

        <!-- 子节点（递归） -->
        <transition name="expand">
            <div v-if="node.type === 'folder' && isExpanded && node.children" class="node-children">
                <FileTreeNode v-for="child in node.children" :key="child.path" :node="child" :current-file="currentFile"
                    :depth="depth + 1" @select="$emit('select', $event)" @create="$emit('create', $event)"
                    @delete="$emit('delete', $event)" @move="$emit('move', $event)" @rename="$emit('rename', $event)"
                    @folder-create="$emit('folder-create', $event)" @folder-delete="$emit('folder-delete', $event)"
                    @image-file-select="$emit('image-file-select', $event)"
                    @external-file-drop="$emit('external-file-drop', $event)" />
            </div>
        </transition>

        <!-- 右键菜单 -->
        <teleport to="body">
            <transition name="context-fade">
                <div v-if="showContextMenu" class="ethereal-context-menu" :style="contextMenuStyle" @click.stop>
                    <div class="context-backdrop"></div>
                    <div class="context-content">
                        <!-- 文件夹选项 -->
                        <template v-if="node.type === 'folder'">
                            <button class="context-item" @click="handleCreateFile">
                                <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                                    <polyline points="14 2 14 8 20 8" />
                                </svg>
                                <span>新建文件</span>
                            </button>
                            <button class="context-item" @click="handleCreateFolder">
                                <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
                                </svg>
                                <span>新建文件夹</span>
                            </button>
                            <div class="context-divider"></div>
                            <button class="context-item" @click="handleRename">
                                <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                                    <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                                </svg>
                                <span>重命名</span>
                            </button>
                            <button class="context-item danger" @click="handleDeleteFolder">
                                <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <polyline points="3 6 5 6 21 6" />
                                    <path
                                        d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                                </svg>
                                <span>删除文件夹</span>
                            </button>
                        </template>

                        <!-- 文件选项 -->
                        <template v-if="node.type === 'file'">
                            <button class="context-item" @click="handleRename">
                                <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                                    <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                                </svg>
                                <span>重命名</span>
                            </button>
                            <button class="context-item danger" @click="handleDeleteFile">
                                <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <polyline points="3 6 5 6 21 6" />
                                    <path
                                        d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                                </svg>
                                <span>删除文件</span>
                            </button>
                        </template>
                    </div>
                </div>
            </transition>
        </teleport>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';

const props = defineProps({
    node: {
        type: Object,
        required: true
    },
    currentFile: {
        type: Object,
        default: null
    },
    depth: {
        type: Number,
        default: 0
    }
});

const emit = defineEmits(['select', 'create', 'delete', 'move', 'rename', 'folder-create', 'folder-delete', 'image-file-select', 'external-file-drop']);

// 33.1 定义图片文件扩展名常量
const IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.avif'];

// 检查是否为 WaterfallGraph 文件夹
const isWaterfallFolder = computed(() => {
    return props.node.type === 'folder' &&
        (props.node.name === 'WaterfallGraph' || props.node.path.includes('WaterfallGraph'));
});

// 检查当前节点是否在 WaterfallGraph 文件夹内
const isInWaterfallFolder = computed(() => {
    return props.node.path.includes('WaterfallGraph');
});

// 检查是否应该隐藏该节点
const shouldHideNode = computed(() => {
    if (props.node.type !== 'file') return false;

    const fileName = props.node.name.toLowerCase();

    // 在 WaterfallGraph 文件夹内
    if (isInWaterfallFolder.value) {
        // 隐藏所有 .md 文件，除了 README.md
        if (fileName.endsWith('.md') && fileName !== 'readme.md') {
            return true;
        }
    } else {
        // 在其他文件夹内 - 隐藏所有图片文件
        const ext = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();
        if (IMAGE_EXTENSIONS.includes(ext)) {
            return true;
        }
    }

    return false;
});

// State
const isExpanded = ref(false);
const showContextMenu = ref(false);
const contextMenuStyle = ref({});
const isDragging = ref(false);
const isDragOver = ref(false);
const showImagePreview = ref(false);
const imagePreviewStyle = ref({});
const imagePreviewUrl = ref('');
let imagePreviewTimer = null;

// Computed
const isCurrentFile = computed(() => {
    return props.currentFile && props.currentFile.path === props.node.path;
});

// 33.2 创建 isImageFile 判断函数
const isImageFile = computed(() => {
    if (props.node.type !== 'file') return false;
    const ext = props.node.name.substring(props.node.name.lastIndexOf('.')).toLowerCase();
    return IMAGE_EXTENSIONS.includes(ext);
});

// 33.4 创建 checkMdFileExists 函数
async function checkMdFileExists(mdPath) {
    // 简化：直接返回 false，让后端 API 来检查文件是否存在
    // 这样可以避免前端的跨域和路径问题
    // EditorPage 会通过后端 API 来加载文件，如果文件不存在会创建模板
    return false;
}

// 33.3 修改 handleFileSelect 处理图片文件
const handleClick = async () => {
    if (props.node.type === 'folder') {
        isExpanded.value = !isExpanded.value;
    } else if (props.node.type === 'file') {
        // 检查是否为图片文件
        if (isImageFile.value) {
            console.log('[FileTreeNode] Image file clicked:', props.node.name);

            // 33.5 触发 image-file-select 事件
            const mdFileName = props.node.name.replace(/\.[^.]+$/, '.md');
            const mdFilePath = props.node.path.replace(props.node.name, mdFileName);

            console.log('[FileTreeNode] Image path:', props.node.path);
            console.log('[FileTreeNode] MD path:', mdFilePath);

            // 简化：总是假设 .md 文件不存在，让 EditorPage 通过 API 检查
            const exists = false;

            emit('image-file-select', {
                imagePath: props.node.path,
                mdPath: mdFilePath,
                exists: exists,
                imageNode: props.node
            });
        } else {
            // 普通文件 - 正常打开
            emit('select', props.node);
        }
    }
};

// 处理鼠标悬停 - 显示图片预览
const handleMouseEnter = (e) => {
    if (isImageFile.value && isInWaterfallFolder.value) {
        // 延迟显示预览，避免快速移动时闪烁
        imagePreviewTimer = setTimeout(() => {
            // 检查事件目标是否存在
            if (!e.currentTarget) {
                console.warn('[FileTreeNode] currentTarget is null, skipping preview');
                return;
            }

            // 构建图片 URL
            imagePreviewUrl.value = props.node.path;

            // 计算预览位置
            const rect = e.currentTarget.getBoundingClientRect();
            imagePreviewStyle.value = {
                top: `${rect.top}px`,
                left: `${rect.right + 10}px`
            };

            showImagePreview.value = true;
        }, 500); // 500ms 延迟
    }
};

// 处理鼠标离开 - 隐藏图片预览
const handleMouseLeave = () => {
    if (imagePreviewTimer) {
        clearTimeout(imagePreviewTimer);
        imagePreviewTimer = null;
    }
    showImagePreview.value = false;
};

// 处理图片加载错误
const handleImageError = () => {
    console.error('[FileTreeNode] Failed to load image preview:', props.node.path);
    showImagePreview.value = false;
};

// Handle context menu
const handleContextMenu = (e) => {
    showContextMenu.value = true;

    contextMenuStyle.value = {
        position: 'fixed',
        top: `${e.clientY}px`,
        left: `${e.clientX}px`
    };

    const closeMenu = () => {
        showContextMenu.value = false;
        document.removeEventListener('click', closeMenu);
    };

    setTimeout(() => {
        document.addEventListener('click', closeMenu);
    }, 0);
};

// Handle create file
const handleCreateFile = () => {
    const fileName = prompt('请输入文件名 (不含.md扩展名):');
    if (fileName) {
        emit('create', {
            folder: props.node,
            fileName: fileName.trim()
        });
    }
    showContextMenu.value = false;
};

// Handle delete file
const handleDeleteFile = () => {
    const confirmed = confirm(`确定要删除文件 "${props.node.name}" 吗?`);
    if (confirmed) {
        emit('delete', props.node);
    }
    showContextMenu.value = false;
};

// Handle rename
const handleRename = () => {
    const currentName = props.node.name;
    const displayName = props.node.type === 'file' && currentName.endsWith('.md')
        ? currentName.slice(0, -3)
        : currentName;

    const newName = prompt(
        props.node.type === 'file' ? '请输入新文件名 (不含.md扩展名):' : '请输入新文件夹名:',
        displayName
    );

    if (newName && newName.trim() !== '' && newName.trim() !== displayName) {
        emit('rename', {
            node: props.node,
            newName: newName.trim()
        });
    }
    showContextMenu.value = false;
};

// Handle create folder
const handleCreateFolder = () => {
    const folderName = prompt('请输入文件夹名:');
    if (folderName && folderName.trim() !== '') {
        emit('folder-create', {
            parentFolder: props.node,
            folderName: folderName.trim()
        });
    }
    showContextMenu.value = false;
};

// Handle delete folder
const handleDeleteFolder = () => {
    const confirmed = confirm(
        `确定要删除文件夹 "${props.node.name}" 及其所有内容吗?\n\n此操作不可撤销!`
    );
    if (confirmed) {
        emit('folder-delete', props.node);
    }
    showContextMenu.value = false;
};

// Drag and drop handlers
const handleDragStart = (e) => {
    if (props.node.type === 'file') {
        isDragging.value = true;
        const dragData = JSON.stringify({
            path: props.node.path,
            name: props.node.name,
            type: props.node.type
        });

        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('application/json', dragData);
        e.dataTransfer.setData('text/plain', props.node.path);
    }
};

const handleDragOver = (e) => {
    if (props.node.type === 'folder') {
        e.preventDefault();

        // 检查是否为外部文件拖入
        const hasFiles = e.dataTransfer.types.includes('Files');

        if (hasFiles && isWaterfallFolder.value) {
            // WaterfallGraph 文件夹接受外部图片文件
            e.dataTransfer.dropEffect = 'copy';
        } else {
            // 普通文件夹只接受内部移动
            e.dataTransfer.dropEffect = 'move';
        }

        isDragOver.value = true;
    }
};

const handleDragLeave = (e) => {
    const target = e.currentTarget;
    const rect = target.getBoundingClientRect();
    const x = e.clientX;
    const y = e.clientY;

    if (x < rect.left || x >= rect.right || y < rect.top || y >= rect.bottom) {
        isDragOver.value = false;
    }
};

const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    isDragOver.value = false;

    if (props.node.type === 'folder') {
        // 检查是否为外部文件拖入
        const files = e.dataTransfer.files;

        if (files && files.length > 0 && isWaterfallFolder.value) {
            // 处理外部文件拖入到 WaterfallGraph 文件夹
            console.log('[FileTreeNode] External files dropped:', files.length);

            // 过滤出图片文件
            const imageFiles = Array.from(files).filter(file => {
                const ext = '.' + file.name.split('.').pop().toLowerCase();
                return IMAGE_EXTENSIONS.includes(ext);
            });

            if (imageFiles.length === 0) {
                alert('⚠️ 只能上传图片文件\n\n支持的格式: PNG, JPG, JPEG, GIF, WEBP, SVG, AVIF');
                return;
            }

            if (imageFiles.length !== files.length) {
                alert(`⚠️ 已过滤掉 ${files.length - imageFiles.length} 个非图片文件\n\n将上传 ${imageFiles.length} 个图片文件`);
            }

            // 触发外部文件上传事件
            emit('external-file-drop', {
                files: imageFiles,
                targetFolder: props.node
            });

            return;
        }

        // 处理内部文件移动
        try {
            const jsonData = e.dataTransfer.getData('application/json');
            let draggedNode;

            if (jsonData) {
                draggedNode = JSON.parse(jsonData);
            } else {
                const path = e.dataTransfer.getData('text/plain');
                if (!path) return;
                const name = path.split('/').pop();
                draggedNode = { path, name, type: 'file' };
            }

            const sourceFolderPath = draggedNode.path.substring(0, draggedNode.path.lastIndexOf('/'));
            if (sourceFolderPath === props.node.path) {
                return;
            }

            emit('move', {
                file: draggedNode,
                targetFolder: props.node
            });
        } catch (error) {
            console.error('[FileTreeNode] Error handling drop:', error);
        }
    }
};

const handleDragEnd = () => {
    isDragging.value = false;
};

// Auto-expand folders on mount if they contain the current file
onMounted(() => {
    if (props.node.type === 'folder' && props.currentFile && props.node.children) {
        const containsCurrentFile = (node) => {
            if (node.path === props.currentFile.path) {
                return true;
            }
            if (node.children) {
                return node.children.some(containsCurrentFile);
            }
            return false;
        };

        if (containsCurrentFile(props.node)) {
            isExpanded.value = true;
        }
    }
});

// Cleanup
onBeforeUnmount(() => {
    if (showContextMenu.value) {
        showContextMenu.value = false;
    }
    if (imagePreviewTimer) {
        clearTimeout(imagePreviewTimer);
    }
});
</script>

<style scoped>
/* === 文件树节点：精致的交互体验 === */

.ethereal-node {
    user-select: none;
    position: relative;
}

.node-content {
    position: relative;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 13px;
    padding-left: calc(13px + var(--node-depth, 0) * 20px);
    cursor: pointer;
    border-radius: 8px;
    margin: 2px 0;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

/* 树状层级线 */
.tree-lines {
    position: absolute;
    left: calc((var(--node-depth, 0) - 1) * 20px + 13px);
    top: 0;
    bottom: 0;
    width: 20px;
    pointer-events: none;
}

.vertical-line {
    position: absolute;
    left: 10px;
    top: 0;
    bottom: 0;
    width: 1px;
    background: linear-gradient(180deg, rgba(148, 163, 184, 0.3) 0%, rgba(148, 163, 184, 0.15) 100%);
}

.horizontal-line {
    position: absolute;
    left: 10px;
    top: 50%;
    width: 10px;
    height: 1px;
    background: rgba(148, 163, 184, 0.3);
}

/* 最后一个子节点的垂直线只到中间 */
.ethereal-node:last-child>.node-content .vertical-line {
    bottom: 50%;
}

/* 选中指示器 */
.selection-indicator {
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 0;
    background: var(--theme-gradient);
    border-radius: 0 2px 2px 0;
    transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1;
}

.node-content.is-current .selection-indicator {
    height: 60%;
}

/* 悬停效果 */
.node-content:hover {
    background: var(--theme-nav-hover-bg);
    transition: var(--theme-transition-colors);
}

.node-content.is-current {
    background: var(--theme-nav-active-bg);
    font-weight: 600;
    transition: var(--theme-transition-colors);
}

.node-content.is-current:hover {
    background: var(--theme-nav-active-bg);
    opacity: 0.9;
}

/* 拖拽状态 */
.node-content.is-dragging {
    opacity: 0.4;
    transform: scale(0.95);
}

.node-content.is-drag-over {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(249, 115, 22, 0.12) 100%);
    border: 2px dashed #f59e0b;
    padding: 6px 11px;
}

/* 图标系统 */
.node-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}

.folder-icon {
    gap: 4px;
}

.expand-arrow {
    width: 14px;
    height: 14px;
    color: var(--theme-meta-text);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.expand-arrow.expanded {
    transform: rotate(90deg);
}

.folder-svg {
    width: 18px;
    height: 18px;
    color: #f59e0b;
    transition: all 0.2s;
}

.node-content:hover .folder-svg {
    color: #ea580c;
    transform: scale(1.1);
}

.node-content.is-expanded .folder-svg {
    color: #f97316;
}

.file-icon svg {
    width: 16px;
    height: 16px;
    color: var(--theme-meta-text);
    transition: all 0.2s;
}

/* 34.3 为图片图标添加特殊样式 */
.file-icon.is-image svg {
    color: #10b981;
}

.node-content:hover .file-icon svg {
    color: var(--theme-panel-text);
    transform: scale(1.1);
}

/* 34.4 实现图标悬停效果 */
.node-content:hover .file-icon.is-image svg {
    color: #059669;
    filter: drop-shadow(0 0 4px rgba(16, 185, 129, 0.3));
}

.node-content.is-current .file-icon svg {
    color: var(--theme-primary);
}

/* 节点名称 */
.node-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 13px;
    font-weight: 500;
    color: var(--theme-panel-text);
    letter-spacing: -0.01em;
    transition: color 0.2s;
    z-index: 1;
}

.node-content:hover .node-name {
    color: var(--theme-heading-text);
}

.node-content.is-current .node-name {
    color: var(--theme-heading-text);
    font-weight: 600;
}

/* WaterfallGraph 文件夹特殊样式 */
.node-content.is-waterfall-folder .folder-svg {
    color: #06b6d4;
}

.node-content.is-waterfall-folder .waterfall-icon rect {
    fill: currentColor;
}

.node-content.is-waterfall-folder:hover .folder-svg {
    color: #0891b2;
}

.node-content.is-waterfall-folder.is-drag-over {
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(8, 145, 178, 0.15) 100%);
    border: 2px dashed #06b6d4;
}

/* 图片预览悬浮框 */
.image-preview-tooltip {
    position: fixed;
    z-index: 10000;
    pointer-events: none;
    max-width: 400px;
    max-height: 400px;
}

.preview-backdrop {
    position: absolute;
    inset: -8px;
    background: var(--theme-panel-bg);
    border-radius: 12px;
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--theme-panel-border);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    transition: var(--theme-transition-colors);
}

.preview-content {
    position: relative;
    padding: 8px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.preview-content img {
    max-width: 100%;
    max-height: 350px;
    object-fit: contain;
    border-radius: 8px;
    display: block;
}

.preview-filename {
    font-size: 12px;
    color: var(--theme-meta-text);
    text-align: center;
    padding: 4px 8px;
    background: var(--theme-surface-hover);
    border-radius: 6px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: var(--theme-transition-colors);
}

/* 预览动画 */
.preview-fade-enter-active,
.preview-fade-leave-active {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.preview-fade-enter-from {
    opacity: 0;
    transform: scale(0.95) translateX(-10px);
}

.preview-fade-leave-to {
    opacity: 0;
    transform: scale(0.95) translateX(10px);
}

/* 拖拽提示 */
.drop-hint {
    position: absolute;
    right: 8px;
    width: 20px;
    height: 20px;
    background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: bounce 0.6s ease-in-out infinite;
    z-index: 1;
}

.node-content.is-waterfall-folder.is-drag-over .drop-hint {
    background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
}

.drop-hint svg {
    width: 12px;
    height: 12px;
    color: #ffffff;
}

@keyframes bounce {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-4px);
    }
}

/* 子节点容器 */
.node-children {
    /* 子节点通过 depth prop 递增来实现缩进 */
}

/* 展开动画 */
.expand-enter-active,
.expand-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
    opacity: 0;
    max-height: 0;
    transform: translateY(-8px);
}

.expand-enter-to,
.expand-leave-from {
    opacity: 1;
    max-height: 1000px;
    transform: translateY(0);
}

/* 右键菜单 */
.ethereal-context-menu {
    position: fixed;
    z-index: 10000;
    filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.15));
}

.context-backdrop {
    position: absolute;
    inset: -6px;
    background: var(--theme-panel-bg);
    border-radius: 12px;
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--theme-panel-border);
    transition: var(--theme-transition-colors);
}

.context-content {
    position: relative;
    padding: 6px;
    min-width: 180px;
}

.context-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 13px;
    border: none;
    background: transparent;
    color: var(--theme-panel-text);
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    border-radius: 8px;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    width: 100%;
    text-align: left;
}

.context-item:hover {
    background: var(--theme-nav-active-bg);
    color: var(--theme-heading-text);
    transform: translateX(2px);
}

.context-item.danger:hover {
    background: var(--theme-error-disabled);
    color: var(--theme-error-hover);
}

.item-icon {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
}

.context-divider {
    height: 1px;
    background: var(--theme-divider);
    margin: 4px 0;
    transition: var(--theme-transition-colors);
}

/* 右键菜单动画 */
.context-fade-enter-active,
.context-fade-leave-active {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.context-fade-enter-from {
    opacity: 0;
    transform: scale(0.95) translateY(-4px);
}

.context-fade-leave-to {
    opacity: 0;
    transform: scale(0.95) translateY(4px);
}
</style>
