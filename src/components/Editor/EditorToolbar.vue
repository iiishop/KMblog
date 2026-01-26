<template>
    <div class="editor-toolbar">
        <div class="toolbar-left">
            <!-- File Tree Toggle -->
            <button @click="$emit('toggle-file-tree')" class="toolbar-btn" title="切换文件树">
                <span class="icon">📁</span>
            </button>

            <!-- File Name -->
            <span class="file-name">{{ fileName || '未选择文件' }}</span>

            <!-- Separator -->
            <div class="separator"></div>

            <!-- Format Buttons -->
            <button @click="insertFormat('bold')" class="toolbar-btn format-btn" title="粗体 (Ctrl+B)">
                <span class="icon">B</span>
            </button>

            <button @click="insertFormat('italic')" class="toolbar-btn format-btn" title="斜体 (Ctrl+I)">
                <span class="icon">I</span>
            </button>

            <button @click="insertFormat('heading')" class="toolbar-btn format-btn" title="标题">
                <span class="icon">H</span>
            </button>

            <button @click="insertFormat('link')" class="toolbar-btn format-btn" title="链接 (Ctrl+K)">
                <span class="icon">🔗</span>
            </button>

            <button @click="insertFormat('image')" class="toolbar-btn format-btn" title="图片">
                <span class="icon">🖼️</span>
            </button>

            <button @click="insertFormat('code')" class="toolbar-btn format-btn" title="代码块">
                <span class="icon">&lt;/&gt;</span>
            </button>

            <!-- Separator -->
            <div class="separator"></div>

            <!-- Block Insert Dropdown -->
            <div class="dropdown" ref="dropdownRef">
                <button @click="toggleDropdown" class="toolbar-btn dropdown-btn" title="插入Block">
                    <span class="icon">➕</span>
                    <span>插入Block</span>
                    <span class="arrow">▼</span>
                </button>

                <div v-if="dropdownVisible" class="dropdown-menu">
                    <button v-for="(template, key) in blockTemplates" :key="key" @click="insertBlock(key)"
                        class="dropdown-item">
                        {{ getBlockDisplayName(key) }}
                    </button>
                </div>
            </div>
        </div>

        <div class="toolbar-right">
            <!-- Save Status -->
            <span class="save-status" :class="saveStatusClass">
                {{ saveStatusText }}
            </span>

            <!-- Save Button -->
            <button @click="$emit('save')" class="toolbar-btn save-btn" :disabled="saveStatus === 'saved'"
                title="保存 (Ctrl+S)">
                <span class="icon">💾</span>
                <span>保存</span>
            </button>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';

const props = defineProps({
    saveStatus: {
        type: String,
        default: 'saved',
        validator: (value) => ['saved', 'saving', 'unsaved'].includes(value)
    },
    fileName: {
        type: String,
        default: ''
    }
});

const emit = defineEmits(['save', 'insert-format', 'insert-block', 'toggle-file-tree']);

// Dropdown state
const dropdownVisible = ref(false);
const dropdownRef = ref(null);

// Block templates
const blockTemplates = {
    'bilibili-video': '```bilibili-video\nhttps://www.bilibili.com/video/BV...\n```',
    'steam-game': '```steam-game\nhttps://store.steampowered.com/app/...\n```',
    'bangumi-card': '```bangumi-card\nhttps://bgm.tv/subject/...\n```',
    'github-repo': '```github-repo\nhttps://github.com/user/repo\n```',
    'xiaohongshu-note': '```xiaohongshu-note\nhttps://www.xiaohongshu.com/explore/...\n```',
    'mermaid': '```mermaid\ngraph TD\n  A[开始] --> B[结束]\n```'
};

// Get display name for block
const getBlockDisplayName = (key) => {
    const names = {
        'bilibili-video': 'Bilibili视频',
        'steam-game': 'Steam游戏',
        'bangumi-card': 'Bangumi卡片',
        'github-repo': 'GitHub仓库',
        'xiaohongshu-note': '小红书笔记',
        'mermaid': 'Mermaid图表'
    };
    return names[key] || key;
};

// Computed
const saveStatusClass = computed(() => {
    return {
        'status-saved': props.saveStatus === 'saved',
        'status-saving': props.saveStatus === 'saving',
        'status-unsaved': props.saveStatus === 'unsaved'
    };
});

const saveStatusText = computed(() => {
    switch (props.saveStatus) {
        case 'saved':
            return '已保存';
        case 'saving':
            return '保存中...';
        case 'unsaved':
            return '未保存';
        default:
            return '';
    }
});

// Methods
const insertFormat = (format) => {
    emit('insert-format', format);
};

const insertBlock = (blockType) => {
    emit('insert-block', blockType);
    dropdownVisible.value = false;
};

const toggleDropdown = () => {
    dropdownVisible.value = !dropdownVisible.value;
};

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
    if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
        dropdownVisible.value = false;
    }
};

// Lifecycle
onMounted(() => {
    document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
    document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.editor-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--theme-border-color, #e0e0e0);
    background-color: var(--theme-toolbar-bg, #fafafa);
    gap: 1rem;
}

.toolbar-left,
.toolbar-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.toolbar-left {
    flex: 1;
    overflow-x: auto;
}

/* Toolbar Button */
.toolbar-btn {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--theme-border-color, #e0e0e0);
    background-color: var(--theme-button-bg, #ffffff);
    color: var(--theme-text-color, #333333);
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    transition: all 0.2s;
    white-space: nowrap;
}

.toolbar-btn:hover:not(:disabled) {
    background-color: var(--theme-hover-bg, #f0f0f0);
    border-color: var(--theme-primary-color, #4a90e2);
}

.toolbar-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.toolbar-btn .icon {
    font-size: 1rem;
    line-height: 1;
}

/* Format Buttons */
.format-btn {
    min-width: 2.5rem;
    justify-content: center;
    padding: 0.5rem;
}

.format-btn .icon {
    font-weight: bold;
}

/* Save Button */
.save-btn {
    background-color: var(--theme-primary-color, #4a90e2);
    color: white;
    border-color: var(--theme-primary-color, #4a90e2);
}

.save-btn:hover:not(:disabled) {
    background-color: var(--theme-primary-hover, #357abd);
}

/* File Name */
.file-name {
    font-weight: 500;
    color: var(--theme-text-secondary, #666666);
    font-size: 0.875rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 200px;
}

/* Separator */
.separator {
    width: 1px;
    height: 1.5rem;
    background-color: var(--theme-border-color, #e0e0e0);
    margin: 0 0.25rem;
}

/* Save Status */
.save-status {
    font-size: 0.875rem;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    font-weight: 500;
    white-space: nowrap;
}

.status-saved {
    color: #22c55e;
    background-color: #f0fdf4;
}

.status-saving {
    color: #f59e0b;
    background-color: #fffbeb;
}

.status-unsaved {
    color: #ef4444;
    background-color: #fef2f2;
}

/* Dropdown */
.dropdown {
    position: relative;
}

.dropdown-btn {
    gap: 0.5rem;
}

.dropdown-btn .arrow {
    font-size: 0.75rem;
    transition: transform 0.2s;
}

.dropdown-menu {
    position: absolute;
    top: calc(100% + 0.25rem);
    left: 0;
    min-width: 200px;
    background-color: var(--theme-button-bg, #ffffff);
    border: 1px solid var(--theme-border-color, #e0e0e0);
    border-radius: 4px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    max-height: 300px;
    overflow-y: auto;
}

.dropdown-item {
    display: block;
    width: 100%;
    padding: 0.75rem 1rem;
    border: none;
    background: none;
    color: var(--theme-text-color, #333333);
    text-align: left;
    cursor: pointer;
    font-size: 0.875rem;
    transition: background-color 0.2s;
}

.dropdown-item:hover {
    background-color: var(--theme-hover-bg, #f0f0f0);
}

.dropdown-item:not(:last-child) {
    border-bottom: 1px solid var(--theme-border-color, #e0e0e0);
}

/* Responsive */
@media (max-width: 768px) {
    .editor-toolbar {
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .toolbar-left {
        flex-wrap: wrap;
    }

    .file-name {
        max-width: 150px;
    }

    .toolbar-btn span:not(.icon) {
        display: none;
    }

    .format-btn {
        min-width: 2rem;
        padding: 0.4rem;
    }
}
</style>
