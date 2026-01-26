<template>
    <div class="ethereal-node" :style="{ '--node-depth': depth }">
        <div class="node-content" :class="{
            'is-folder': node.type === 'folder',
            'is-file': node.type === 'file',
            'is-current': isCurrentFile,
            'is-expanded': isExpanded,
            'is-dragging': isDragging,
            'is-drag-over': isDragOver
        }" @click="handleClick" @contextmenu.prevent="handleContextMenu" :draggable="node.type === 'file'"
            @dragstart="handleDragStart" @dragend="handleDragEnd" @dragover="handleDragOver"
            @dragleave="handleDragLeave" @drop="handleDrop">

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
                <svg class="folder-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
                </svg>
            </div>

            <!-- 文件图标 -->
            <div v-else class="node-icon file-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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

        <!-- 子节点（递归） -->
        <transition name="expand">
            <div v-if="node.type === 'folder' && isExpanded && node.children" class="node-children">
                <FileTreeNode v-for="child in node.children" :key="child.path" :node="child" :current-file="currentFile"
                    :depth="depth + 1" @select="$emit('select', $event)" @create="$emit('create', $event)"
                    @delete="$emit('delete', $event)" @move="$emit('move', $event)" @rename="$emit('rename', $event)"
                    @folder-create="$emit('folder-create', $event)" @folder-delete="$emit('folder-delete', $event)" />
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

const emit = defineEmits(['select', 'create', 'delete', 'move', 'rename', 'folder-create', 'folder-delete']);

// State
const isExpanded = ref(false);
const showContextMenu = ref(false);
const contextMenuStyle = ref({});
const isDragging = ref(false);
const isDragOver = ref(false);

// Computed
const isCurrentFile = computed(() => {
    return props.currentFile && props.currentFile.path === props.node.path;
});

// Handle click
const handleClick = () => {
    if (props.node.type === 'folder') {
        isExpanded.value = !isExpanded.value;
    } else if (props.node.type === 'file') {
        emit('select', props.node);
    }
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
        e.dataTransfer.dropEffect = 'move';
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

const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    isDragOver.value = false;

    if (props.node.type === 'folder') {
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
    background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
    border-radius: 0 2px 2px 0;
    transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1;
}

.node-content.is-current .selection-indicator {
    height: 60%;
}

/* 悬停效果 */
.node-content:hover {
    background: rgba(99, 102, 241, 0.06);
}

.node-content.is-current {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(139, 92, 246, 0.12) 100%);
    font-weight: 600;
}

.node-content.is-current:hover {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.16) 0%, rgba(139, 92, 246, 0.16) 100%);
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
    color: #94a3b8;
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
    color: #64748b;
    transition: all 0.2s;
}

.node-content:hover .file-icon svg {
    color: #475569;
    transform: scale(1.1);
}

.node-content.is-current .file-icon svg {
    color: #6366f1;
}

/* 节点名称 */
.node-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 13px;
    font-weight: 500;
    color: #475569;
    letter-spacing: -0.01em;
    transition: color 0.2s;
    z-index: 1;
}

.node-content:hover .node-name {
    color: #1e293b;
}

.node-content.is-current .node-name {
    color: #1e293b;
    font-weight: 600;
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
    background: rgba(255, 255, 255, 0.98);
    border-radius: 12px;
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(148, 163, 184, 0.15);
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
    color: #475569;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    border-radius: 8px;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    width: 100%;
    text-align: left;
}

.context-item:hover {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
    color: #1e293b;
    transform: translateX(2px);
}

.context-item.danger:hover {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(220, 38, 38, 0.08) 100%);
    color: #dc2626;
}

.item-icon {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
}

.context-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(148, 163, 184, 0.2) 50%, transparent 100%);
    margin: 4px 0;
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
