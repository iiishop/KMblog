<template>
    <div class="file-tree-node">
        <div class="node-content" :class="{
            'is-folder': node.type === 'folder',
            'is-file': node.type === 'file',
            'is-current': isCurrentFile,
            'is-expanded': isExpanded
        }" @click="handleClick" @contextmenu.prevent="handleContextMenu" :draggable="node.type === 'file'"
            @dragstart="handleDragStart" @dragend="handleDragEnd" @dragover="handleDragOver"
            @dragleave="handleDragLeave" @drop="handleDrop">
            <!-- Folder icon or expand/collapse arrow -->
            <span v-if="node.type === 'folder'" class="node-icon folder-icon">
                <svg v-if="isExpanded" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 11L3 6h10z" />
                </svg>
                <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M6 3l5 5-5 5z" />
                </svg>
            </span>

            <!-- File icon -->
            <span v-else class="node-icon file-icon">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M4 1h5l3 3v9a1 1 0 01-1 1H4a1 1 0 01-1-1V2a1 1 0 011-1z" />
                    <path d="M9 1v3h3" fill="none" stroke="currentColor" stroke-width="1" />
                </svg>
            </span>

            <!-- Node name -->
            <span class="node-name">{{ node.name }}</span>
        </div>

        <!-- Children (recursive) -->
        <div v-if="node.type === 'folder' && isExpanded && node.children" class="node-children">
            <FileTreeNode v-for="child in node.children" :key="child.path" :node="child" :current-file="currentFile"
                @select="$emit('select', $event)" @create="$emit('create', $event)" @delete="$emit('delete', $event)"
                @move="$emit('move', $event)" @rename="$emit('rename', $event)"
                @folder-create="$emit('folder-create', $event)" @folder-delete="$emit('folder-delete', $event)" />
        </div>

        <!-- Context menu -->
        <div v-if="showContextMenu" class="context-menu" :style="contextMenuStyle" @click.stop>
            <!-- Folder options -->
            <template v-if="node.type === 'folder'">
                <div class="context-menu-item" @click="handleCreateFile">
                    <span class="menu-icon">📄</span>
                    <span>新建文件</span>
                </div>
                <div class="context-menu-item" @click="handleCreateFolder">
                    <span class="menu-icon">📁</span>
                    <span>新建文件夹</span>
                </div>
                <div class="context-menu-item" @click="handleRename">
                    <span class="menu-icon">✏️</span>
                    <span>重命名</span>
                </div>
                <div class="context-menu-item" @click="handleDeleteFolder">
                    <span class="menu-icon">🗑️</span>
                    <span>删除文件夹</span>
                </div>
            </template>

            <!-- File options -->
            <template v-if="node.type === 'file'">
                <div class="context-menu-item" @click="handleRename">
                    <span class="menu-icon">✏️</span>
                    <span>重命名</span>
                </div>
                <div class="context-menu-item" @click="handleDeleteFile">
                    <span class="menu-icon">🗑️</span>
                    <span>删除文件</span>
                </div>
            </template>
        </div>
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
    }
});

const emit = defineEmits(['select', 'create', 'delete', 'move', 'rename', 'folder-create', 'folder-delete']);

// State
const isExpanded = ref(false);
const showContextMenu = ref(false);
const contextMenuStyle = ref({});

// Computed
const isCurrentFile = computed(() => {
    return props.currentFile && props.currentFile.path === props.node.path;
});

// Handle click
const handleClick = () => {
    if (props.node.type === 'folder') {
        // Toggle folder expansion
        isExpanded.value = !isExpanded.value;
    } else if (props.node.type === 'file') {
        // Select file
        emit('select', props.node);
    }
};

// Handle context menu
const handleContextMenu = (e) => {
    showContextMenu.value = true;

    // Position context menu at cursor
    contextMenuStyle.value = {
        top: `${e.clientY}px`,
        left: `${e.clientX}px`
    };

    // Close menu when clicking outside
    const closeMenu = () => {
        showContextMenu.value = false;
        document.removeEventListener('click', closeMenu);
    };

    // Delay to prevent immediate close
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
    // Remove .md extension for files when prompting
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
    console.log('[FileTreeNode] Drag start:', props.node.name, props.node.type);

    if (props.node.type === 'file') {
        // Store node data in dataTransfer
        const dragData = JSON.stringify({
            path: props.node.path,
            name: props.node.name,
            type: props.node.type
        });

        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('application/json', dragData);
        e.dataTransfer.setData('text/plain', props.node.path); // Fallback

        console.log('[FileTreeNode] Drag data set:', dragData);

        // Add dragging class
        e.currentTarget.classList.add('dragging');
    }
};

const handleDragOver = (e) => {
    if (props.node.type === 'folder') {
        e.preventDefault(); // Required to allow drop
        e.dataTransfer.dropEffect = 'move';

        // Add visual feedback
        const target = e.currentTarget;
        if (!target.classList.contains('drag-over')) {
            target.classList.add('drag-over');
            console.log('[FileTreeNode] Drag over folder:', props.node.name);
        }
    }
};

const handleDragLeave = (e) => {
    // Only remove class if we're actually leaving the element
    const target = e.currentTarget;
    const rect = target.getBoundingClientRect();
    const x = e.clientX;
    const y = e.clientY;

    if (x < rect.left || x >= rect.right || y < rect.top || y >= rect.bottom) {
        target.classList.remove('drag-over');
        console.log('[FileTreeNode] Drag leave folder:', props.node.name);
    }
};

const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();

    console.log('[FileTreeNode] Drop on:', props.node.name, props.node.type);

    const target = e.currentTarget;
    target.classList.remove('drag-over');

    if (props.node.type === 'folder') {
        try {
            // Try to get JSON data first
            const jsonData = e.dataTransfer.getData('application/json');
            let draggedNode;

            if (jsonData) {
                draggedNode = JSON.parse(jsonData);
                console.log('[FileTreeNode] Dropped file data:', draggedNode);
            } else {
                // Fallback to text/plain
                const path = e.dataTransfer.getData('text/plain');
                console.log('[FileTreeNode] Fallback to text/plain:', path);

                if (!path) {
                    console.error('[FileTreeNode] No drag data available');
                    return;
                }

                // Extract name from path
                const name = path.split('/').pop();
                draggedNode = { path, name, type: 'file' };
            }

            // Don't move if dropping on the same folder
            const sourceFolderPath = draggedNode.path.substring(0, draggedNode.path.lastIndexOf('/'));
            if (sourceFolderPath === props.node.path) {
                console.log('[FileTreeNode] Same folder, ignoring drop');
                return;
            }

            console.log('[FileTreeNode] Emitting move event:', {
                file: draggedNode,
                targetFolder: props.node
            });

            // Emit move event
            emit('move', {
                file: draggedNode,
                targetFolder: props.node
            });
        } catch (error) {
            console.error('[FileTreeNode] Error handling drop:', error);
        }
    }
};

const handleDragEnd = (e) => {
    console.log('[FileTreeNode] Drag end');
    e.currentTarget.classList.remove('dragging');
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
.file-tree-node {
    user-select: none;
}

.node-content {
    display: flex;
    align-items: center;
    padding: 0.4rem 0.5rem;
    padding-left: calc(0.5rem + var(--indent-level, 0) * 1rem);
    cursor: pointer;
    border-radius: 4px;
    margin: 0 0.25rem;
    transition: background-color 0.15s;
    position: relative;
}

.node-content:hover {
    background-color: var(--theme-hover-bg, #e8e8e8);
}

.node-content.is-current {
    background-color: var(--theme-selected-bg, #d0e8ff);
    font-weight: 500;
}

.node-content.is-current:hover {
    background-color: var(--theme-selected-hover-bg, #c0d8ef);
}

.node-content.drag-over {
    background-color: var(--theme-primary-light, #e3f2fd);
    border: 2px dashed var(--theme-primary-color, #4a90e2);
}

.node-content.dragging {
    opacity: 0.5;
}

.node-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.5rem;
    flex-shrink: 0;
    color: var(--theme-icon-color, #666666);
}

.folder-icon {
    color: var(--theme-folder-color, #f59e0b);
}

.file-icon {
    color: var(--theme-file-color, #6b7280);
}

.node-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 0.875rem;
    color: var(--theme-text-color, #333333);
}

.node-children {
    --indent-level: calc(var(--indent-level, 0) + 1);
}

/* Context Menu */
.context-menu {
    position: fixed;
    background-color: var(--theme-menu-bg, #ffffff);
    border: 1px solid var(--theme-border-color, #e0e0e0);
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    padding: 0.25rem 0;
    min-width: 150px;
    z-index: 1000;
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
    font-weight: bold;
    color: var(--theme-icon-color, #666666);
}

/* Animations */
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

.context-menu {
    animation: fadeIn 0.15s ease-out;
}
</style>
