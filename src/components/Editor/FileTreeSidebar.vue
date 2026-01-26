<template>
    <div class="file-tree-sidebar" :class="{ 'collapsed': !visible }" :style="{ width: visible ? width + 'px' : '0' }">
        <div class="sidebar-header">
            <h3>文件</h3>
            <button @click="$emit('update:visible', false)" class="close-btn" title="隐藏文件树">
                ×
            </button>
        </div>

        <div class="file-tree" @contextmenu.prevent="handleTreeContextMenu">
            <FileTreeNode v-for="node in files" :key="node.path" :node="node" :current-file="currentFile"
                @select="$emit('file-select', $event)" @create="$emit('file-create', $event)"
                @delete="$emit('file-delete', $event)" @move="$emit('file-move', $event)"
                @rename="$emit('file-rename', $event)" @folder-create="$emit('folder-create', $event)"
                @folder-delete="$emit('folder-delete', $event)" />

            <!-- Context menu for empty space -->
            <div v-if="showTreeContextMenu" class="tree-context-menu" :style="treeContextMenuStyle" @click.stop>
                <div class="context-menu-item" @click="handleCreateFileInRoot">
                    <span class="menu-icon">📄</span>
                    <span>新建文件</span>
                </div>
                <div class="context-menu-item" @click="handleCreateFolderInRoot">
                    <span class="menu-icon">📁</span>
                    <span>新建文件夹</span>
                </div>
            </div>
        </div>

        <!-- Resize handle for dragging -->
        <div v-if="visible" class="resize-handle" @mousedown="startResize" title="拖动调整宽度" />
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
.file-tree-sidebar {
    position: relative;
    border-right: 1px solid var(--theme-border-color, #e0e0e0);
    background-color: var(--theme-sidebar-bg, #f5f5f5);
    display: flex;
    flex-direction: column;
    min-width: 200px;
    max-width: 500px;
    transition: width 0.2s ease;
    overflow: hidden;
}

.file-tree-sidebar.collapsed {
    width: 0 !important;
    min-width: 0;
    border-right: none;
}

.sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--theme-border-color, #e0e0e0);
    background-color: var(--theme-sidebar-header-bg, #fafafa);
    flex-shrink: 0;
}

.sidebar-header h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--theme-text-color, #333333);
}

.close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: var(--theme-text-color, #333333);
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    transition: background-color 0.2s;
}

.close-btn:hover {
    background-color: var(--theme-hover-bg, #e0e0e0);
}

.file-tree {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 0.5rem 0;
}

/* Custom scrollbar */
.file-tree::-webkit-scrollbar {
    width: 8px;
}

.file-tree::-webkit-scrollbar-track {
    background: transparent;
}

.file-tree::-webkit-scrollbar-thumb {
    background: var(--theme-scrollbar-thumb, #c0c0c0);
    border-radius: 4px;
}

.file-tree::-webkit-scrollbar-thumb:hover {
    background: var(--theme-scrollbar-thumb-hover, #a0a0a0);
}

.resize-handle {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    cursor: col-resize;
    background-color: transparent;
    transition: background-color 0.2s;
    z-index: 10;
}

.resize-handle:hover {
    background-color: var(--theme-primary-color, #4a90e2);
}

.resize-handle:active {
    background-color: var(--theme-primary-hover, #357abd);
}

/* Tree Context Menu */
.tree-context-menu {
    position: fixed;
    background-color: var(--theme-menu-bg, #ffffff);
    border: 1px solid var(--theme-border-color, #e0e0e0);
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    padding: 0.25rem 0;
    min-width: 150px;
    z-index: 1000;
    animation: fadeIn 0.15s ease-out;
}

.context-menu-item {
    display: flex;
    align-items: center;
    padding: 0.5rem 1rem;
    cursor: pointer;
    font-size: 0.875rem;
    color: var(--theme-text-color, #333333);
    transition: background-color 0.15s;
}

.context-menu-item:hover {
    background-color: var(--theme-hover-bg, #f0f0f0);
}

.menu-icon {
    margin-right: 0.5rem;
    font-size: 1rem;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

/* Responsive */
@media (max-width: 768px) {
    .file-tree-sidebar {
        max-width: 300px;
    }
}
</style>
