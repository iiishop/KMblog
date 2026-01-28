<template>
    <div class="ethereal-sidebar" :class="{ 'collapsed': !visible }" :style="{ width: visible ? width + 'px' : '0' }">
        <!-- 侧边栏光晕背景 -->
        <div class="sidebar-glow"></div>

        <div class="sidebar-header">
            <div class="header-content">
                <svg class="header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                </svg>
                <h3>文件浏览器</h3>
            </div>
        </div>

        <div class="file-tree" @contextmenu.prevent="handleTreeContextMenu">
            <FileTreeNode v-for="node in files" :key="node.path" :node="node" :current-file="currentFile"
                @select="$emit('file-select', $event)" @create="$emit('file-create', $event)"
                @delete="$emit('file-delete', $event)" @move="$emit('file-move', $event)"
                @rename="$emit('file-rename', $event)" @folder-create="$emit('folder-create', $event)"
                @folder-delete="$emit('folder-delete', $event)" />

            <!-- 空状态提示 -->
            <div v-if="files.length === 0" class="empty-state">
                <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
                </svg>
                <p>暂无文件</p>
            </div>

            <!-- 右键菜单 -->
            <teleport to="body">
                <transition name="context-fade">
                    <div v-if="showTreeContextMenu" class="ethereal-context-menu" :style="treeContextMenuStyle"
                        @click.stop>
                        <div class="context-backdrop"></div>
                        <div class="context-content">
                            <button class="context-item" @click="handleCreateFileInRoot">
                                <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                                    <polyline points="14 2 14 8 20 8" />
                                </svg>
                                <span>新建文件</span>
                            </button>
                            <button class="context-item" @click="handleCreateFolderInRoot">
                                <svg class="item-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
                                </svg>
                                <span>新建文件夹</span>
                            </button>
                        </div>
                    </div>
                </transition>
            </teleport>
        </div>

        <!-- 优雅的调整手柄 -->
        <div v-if="visible" class="resize-handle" @mousedown="startResize" title="拖动调整宽度">
            <div class="handle-indicator"></div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import FileTreeNode from './FileTreeNode.vue';

const props = defineProps({
    visible: {
        type: Boolean,
        required: true
    },
    width: {
        type: Number,
        required: true
    },
    files: {
        type: Array,
        required: true
    },
    currentFile: {
        type: Object,
        default: null
    }
});

const emit = defineEmits([
    'update:visible',
    'update:width',
    'file-select',
    'file-create',
    'file-delete',
    'file-move',
    'file-rename',
    'folder-create',
    'folder-delete'
]);

// Tree context menu state
const showTreeContextMenu = ref(false);
const treeContextMenuStyle = ref({});

// Handle context menu on empty space
const handleTreeContextMenu = (e) => {
    // Only show menu if clicking on the tree container itself, not on nodes
    if (e.target.classList.contains('file-tree')) {
        showTreeContextMenu.value = true;

        // Position context menu at cursor
        treeContextMenuStyle.value = {
            top: `${e.clientY}px`,
            left: `${e.clientX}px`
        };

        // Close menu when clicking outside
        const closeMenu = () => {
            showTreeContextMenu.value = false;
            document.removeEventListener('click', closeMenu);
        };

        // Delay to prevent immediate close
        setTimeout(() => {
            document.addEventListener('click', closeMenu);
        }, 0);
    }
};

// Handle create file in root (Markdowns folder)
const handleCreateFileInRoot = () => {
    const fileName = prompt('请输入文件名 (不含.md扩展名):');
    if (fileName && fileName.trim() !== '') {
        // Find Markdowns folder or use first folder as default
        const markdownsFolder = props.files.find(f => f.name === 'Markdowns') || props.files[0];

        if (markdownsFolder && markdownsFolder.type === 'folder') {
            emit('file-create', {
                folder: markdownsFolder,
                fileName: fileName.trim()
            });
        } else {
            alert('未找到可用的文件夹');
        }
    }
    showTreeContextMenu.value = false;
};

// Handle create folder in root
const handleCreateFolderInRoot = () => {
    const folderName = prompt('请输入文件夹名:');
    if (folderName && folderName.trim() !== '') {
        // Create folder at root level (Posts directory)
        // Use empty path to indicate root
        emit('folder-create', {
            parentFolder: {
                name: 'Posts',
                type: 'folder',
                path: ''  // Empty path for root
            },
            folderName: folderName.trim()
        });
    }
    showTreeContextMenu.value = false;
};

// Handle resize drag
const startResize = (e) => {
    e.preventDefault();

    const startX = e.clientX;
    const startWidth = props.width;

    const handleMouseMove = (e) => {
        const deltaX = e.clientX - startX;
        const newWidth = startWidth + deltaX;

        // Constrain width between 200px and 500px
        const constrainedWidth = Math.max(200, Math.min(500, newWidth));
        emit('update:width', constrainedWidth);
    };

    const handleMouseUp = () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
    };

    // Prevent text selection during drag
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
};
</script>

<style scoped>
/* === 侧边栏：优雅的文件导航 === */

.ethereal-sidebar {
    position: relative;
    background: var(--theme-panel-bg);
    border-right: 1px solid var(--theme-panel-border);
    display: flex;
    flex-direction: column;
    min-width: 200px;
    max-width: 500px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    isolation: isolate;
}

.ethereal-sidebar.collapsed {
    width: 0 !important;
    min-width: 0;
    border-right: none;
    opacity: 0;
}

/* 侧边栏光晕 */
.sidebar-glow {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 200px;
    background: radial-gradient(ellipse at top, rgba(99, 102, 241, 0.05) 0%, transparent 70%);
    pointer-events: none;
}

/* 头部区域 */
.sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 21px;
    border-bottom: 1px solid var(--theme-panel-border);
    background: var(--theme-surface-default);
    backdrop-filter: blur(10px);
    flex-shrink: 0;
    position: relative;
    z-index: 1;
    transition: var(--theme-transition-colors);
}

.header-content {
    display: flex;
    align-items: center;
    gap: 10px;
}

.header-icon {
    width: 20px;
    height: 20px;
    color: var(--theme-primary);
    stroke-width: 2;
    transition: var(--theme-transition-colors);
}

.sidebar-header h3 {
    margin: 0;
    font-size: 14px;
    font-weight: 700;
    color: var(--theme-heading-text);
    letter-spacing: -0.02em;
    transition: var(--theme-transition-colors);
}

.close-btn {
    background: none;
    border: none;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    cursor: pointer;
    color: #64748b;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 0;
}

.close-btn svg {
    width: 16px;
    height: 16px;
}

.close-btn:hover {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    transform: rotate(90deg);
}

/* 文件树区域 */
.file-tree {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 13px 8px;
    position: relative;
}

/* 优雅的滚动条 */
.file-tree::-webkit-scrollbar {
    width: 6px;
}

.file-tree::-webkit-scrollbar-track {
    background: transparent;
}

.file-tree::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.3);
    border-radius: 3px;
    transition: background 0.2s;
}

.file-tree::-webkit-scrollbar-thumb:hover {
    background: rgba(148, 163, 184, 0.5);
}

/* 空状态 */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    color: var(--theme-meta-text);
    transition: var(--theme-transition-colors);
}

.empty-icon {
    width: 48px;
    height: 48px;
    margin-bottom: 12px;
    opacity: 0.5;
}

.empty-state p {
    margin: 0;
    font-size: 13px;
    font-weight: 500;
}

/* 调整手柄 */
.resize-handle {
    position: absolute;
    right: -3px;
    top: 0;
    bottom: 0;
    width: 6px;
    cursor: col-resize;
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.handle-indicator {
    width: 2px;
    height: 40px;
    background: var(--theme-border-medium);
    border-radius: 1px;
    transition: all 0.2s;
}

.resize-handle:hover .handle-indicator {
    background: var(--theme-primary);
    height: 60px;
    box-shadow: 0 0 8px var(--theme-primary);
}

.resize-handle:active .handle-indicator {
    background: var(--theme-primary-hover);
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

.item-icon {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
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

/* 响应式 */
@media (max-width: 768px) {
    .ethereal-sidebar {
        max-width: 300px;
    }

    .sidebar-header {
        padding: 13px 16px;
    }

    .file-tree {
        padding: 10px 6px;
    }
}
</style>
