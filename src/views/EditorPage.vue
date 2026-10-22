<template>
    <div class="editor-container" :class="{ 'focus-mode': focusMode }">
        <!-- File Tree Sidebar -->
        <button v-if="fileTreeVisible && !focusMode" class="sidebar-backdrop" aria-label="关闭文件浏览器" @click="fileTreeVisible = false"></button>
        <FileTreeSidebar ref="fileTreeRef" :visible="fileTreeVisible && !focusMode" @update:visible="fileTreeVisible = $event" v-model:width="fileTreeWidth" :files="fileTree"
            :current-file="currentFile" @file-select="handleFileSelect" @file-create="handleFileCreate"
            @file-delete="handleFileDelete" @file-move="handleFileMove" @file-rename="handleFileRename"
            @folder-create="handleFolderCreate" @folder-delete="handleFolderDelete"
            @image-file-select="handleImageFileSelect" @external-file-drop="handleExternalFileDrop" />

        <!-- Main Editor Area -->
        <div class="main-editor">
            <!-- Toolbar -->
            <EditorToolbar :save-status="saveStatus" :file-name="currentFileName" :last-save-time="lastSaveTime"
                :disabled="!currentFile || isOpening || !!draft"
                @save="handleSave" @insert-format="handleInsertFormat" @insert-block="handleInsertBlock"
                @toggle-file-tree="toggleFileTree" />

            <div v-if="fileTreeError" class="editor-notice error" role="alert">
                <span>{{ fileTreeError }}</span>
                <button @click="loadFileTree" :disabled="fileTreeLoading">重新连接</button>
            </div>
            <div v-if="draft" class="editor-notice" role="status">
                <span>找到此文件的本地草稿（{{ new Date(draft.savedAt).toLocaleString() }}）。恢复前不会覆盖磁盘文件。</span>
                <button @click="session.restoreDraft">恢复草稿</button>
                <button @click="session.dismissDraft">使用磁盘版本</button>
            </div>
            <div v-if="issue" class="editor-notice" :class="{ error: issue.kind !== 'draft' }" role="alert">
                <span>{{ issue.message }}</span>
                <template v-if="issue.kind === 'conflict'">
                    <button @click="handleReloadFile" :disabled="isOpening || isSaving">读取磁盘版本</button>
                    <button @click="handleForceSave" :disabled="isSaving">覆盖保存</button>
                </template>
                <button v-else-if="issue.kind === 'save' || issue.kind === 'draft'" @click="handleSave" :disabled="isSaving">{{ issue.kind === 'save' ? '重试保存' : '保存到文件' }}</button>
                <button v-if="currentFile" @click="downloadDraft">下载当前副本</button>
                <button v-if="issue.kind === 'load'" @click="issue = null" aria-label="关闭提示">关闭</button>
            </div>
            <div v-if="draftWarning" class="editor-notice error" role="status">{{ draftWarning }}</div>
            <div v-if="notification" class="editor-notice" role="status">{{ notification }}</div>

            <div v-if="!currentFile" class="editor-empty">
                <span class="empty-mark" aria-hidden="true">✎</span>
                <h1>选择文章，开始写作</h1>
                <p>从左侧打开 Markdown 文件。修改会自动保存，也会在当前浏览器保留未保存草稿。</p>
                <button @click="fileTreeVisible = true">打开文件浏览器</button>
                <span v-if="fileTreeLoading" role="status">正在加载文件列表…</span>
            </div>

            <div v-if="currentFile" class="workspace-bar">
                <button @click="searchFiles" title="查找文章 · Ctrl / ⌘ + P" class="path-button">⌕ <span>{{ currentFile.path.replace('/Posts/', '') }}</span></button>
                <div class="view-switch" role="group" aria-label="编辑器布局">
                    <button @click="setLayout('edit')" :aria-pressed="effectiveLayout === 'edit'">编辑</button>
                    <button v-if="!isNarrow" @click="setLayout('split')" :aria-pressed="effectiveLayout === 'split'">双栏</button>
                    <button @click="setLayout('preview')" :aria-pressed="effectiveLayout === 'preview'">预览</button>
                </div>
                <label v-if="effectiveLayout === 'split'" class="sync-toggle"><input v-model="syncScroll" type="checkbox" />同步滚动</label>
                <button @click="focusMode = !focusMode" :aria-pressed="focusMode" title="专注写作 · Esc 退出">{{ focusMode ? '退出专注' : '专注' }}</button>
            </div>

            <!-- Editor and Preview Panels -->
            <div v-if="currentFile" class="editor-panels" ref="panelsRef" :aria-busy="isOpening" :class="`layout-${effectiveLayout}`" :style="{ '--editor-width': splitRatio + '%' }">
                <!-- Edit Panel -->
                <div class="edit-panel" v-show="effectiveLayout !== 'preview'">
                    <MonacoEditor v-model="content" language="markdown" :theme="editorTheme"
                        :document-key="currentFile.path" :options="{ readOnly: isOpening || !!draft }"
                        :current-file-name="currentFileName" :api-base="API_BASE" :scroll-sync="previewScrollTop"
                        @save="handleSave" @search-files="searchFiles" @notice="notify" @cursor="cursor = $event" @scroll="handleEditorScroll" @format-request="handleInsertFormat"
                        ref="monacoEditorRef" />
                </div>

                <div v-show="effectiveLayout === 'split'" class="panel-splitter" role="separator" tabindex="0"
                    aria-label="调整编辑区宽度" aria-orientation="vertical" :aria-valuenow="splitRatio" :aria-valuemin="35" :aria-valuemax="70"
                    @pointerdown="startPanelResize" @pointermove="resizePanels" @pointerup="resizingPanels = false" @lostpointercapture="resizingPanels = false"
                    @keydown="resizePanelsByKey" @dblclick="splitRatio = 50"></div>
                <!-- Preview Panel -->
                <div class="preview-panel" v-show="effectiveLayout !== 'edit'" ref="previewPanelRef">
                    <!-- WaterfallGraph 图片预览 - 使用 Graph 组件 -->
                    <div v-if="isWaterfallGraphFile && graphData" class="graph-preview-section">
                        <div class="preview-header">
                            <div class="preview-label">图片卡片预览</div>
                            <button @click="toggleGraphPreview" class="collapse-btn"
                                :class="{ 'collapsed': !showGraphPreview }">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </button>
                        </div>
                        <div v-show="showGraphPreview" class="graph-preview-content">
                            <div class="graph-preview-wrapper">
                                <Graph :image="graphData" :index="0" :column="0" />
                            </div>
                        </div>
                    </div>

                    <details v-else-if="currentMetadata && Object.keys(currentMetadata).length" class="metadata-preview">
                        <summary>文章信息预览 <span>来自当前草稿</span></summary>
                        <div class="metadata-card">
                            <img v-if="currentMetadata.img" :src="coverUrl" alt="文章封面" loading="lazy" />
                            <h2>{{ currentMetadata.title || currentFileName.replace(/\.md$/i, '') }}</h2>
                            <p v-if="currentMetadata.description || currentMetadata.summary">{{ currentMetadata.description || currentMetadata.summary }}</p>
                            <small v-if="currentMetadata.date">{{ currentMetadata.date }}</small>
                            <p v-if="currentMetadata.tags" class="metadata-tags">{{ Array.isArray(currentMetadata.tags) ? currentMetadata.tags.join(' · ') : currentMetadata.tags }}</p>
                        </div>
                    </details>

                    <!-- Markdown内容预览 -->
                    <div class="markdown-preview-section">
                        <div v-if="currentMetadata || isWaterfallGraphFile" class="preview-label">Markdown渲染预览</div>
                        <MarkdownPreview :content="content" :active="effectiveLayout !== 'edit'" :scroll-sync="editorScrollTop"
                            @scroll="handlePreviewScroll" />
                    </div>
                </div>
            </div>
            <footer v-if="currentFile" class="editor-statusbar">
                <span>{{ documentStats.words.toLocaleString() }} 字 / 词 · 约 {{ documentStats.minutes }} 分钟阅读</span>
                <span class="cursor-position">行 {{ cursor.lineNumber }}，列 {{ cursor.column }}</span>
                <span>{{ isOpening ? '正在打开…' : isSaving ? '正在保存…' : isDirty ? '有未保存修改' : '已与磁盘同步' }}</span>
            </footer>
        </div>
        <EditorLeaveDialog v-if="leavePrompt" :file-name="currentFileName" @answer="session.answerLeave" />
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { onBeforeRouteLeave } from 'vue-router';
import { useEditorDocument } from '@/composables/useEditorDocument';
import EditorLeaveDialog from '@/components/Editor/EditorLeaveDialog.vue';
import axios from 'axios';
import fm from 'front-matter';
import MonacoEditor from '@/components/Editor/MonacoEditor.vue';
import MarkdownPreview from '@/components/Editor/MarkdownPreview.vue';
import FileTreeSidebar from '@/components/Editor/FileTreeSidebar.vue';
import EditorToolbar from '@/components/Editor/EditorToolbar.vue';
import Graph from '@/components/WaterfallPanelComps/Graph.vue';
import { useTheme } from '@/composables/useTheme';

// Error handling utility
const handleApiError = (error, context = '') => {
    // Log detailed error for debugging
    console.error(`[EditorPage] ${context} Error:`, error);

    if (axios.isCancel(error)) {
        // Silently ignore cancellation errors
        return null;
    }

    let userMessage = '';

    if (error.response) {
        // Server returned error status code
        const status = error.response.status;
        const detail = error.response.data?.detail || error.response.data?.message || '';

        console.error(`[EditorPage] ${context} HTTP ${status}:`, detail);

        switch (status) {
            case 400:
                userMessage = `请求无效: ${detail || '请检查输入'}`;
                break;
            case 401:
                userMessage = '认证失败: 请重新启动编辑器';
                break;
            case 404:
                userMessage = `文件不存在: ${detail || '请刷新文件树'}`;
                break;
            case 409:
                // Version conflict - handled separately
                return error;
            case 500:
                userMessage = `服务器错误: ${detail || '请稍后重试'}`;
                break;
            default:
                userMessage = `操作失败 (${status}): ${detail || '未知错误'}`;
        }
    } else if (error.request) {
        // Request sent but no response received
        console.error(`[EditorPage] ${context} No response from server`);
        userMessage = '无法连接到服务器\n请确保编辑器服务正在运行';
    } else {
        // Error setting up request
        console.error(`[EditorPage] ${context} Request setup error:`, error.message);
        userMessage = `发生错误: ${error.message || '未知错误'}`;
    }

    return userMessage;
};

// Get token and port from URL parameters
// Note: Using hash router, so params are in window.location.hash
const getHashParams = () => {
    const hash = window.location.hash;
    const queryString = hash.split('?')[1];
    if (!queryString) return new URLSearchParams();
    return new URLSearchParams(queryString);
};

const urlParams = getHashParams();
const authToken = urlParams.get('token');
const apiPort = urlParams.get('api_port');


// Use current hostname instead of hardcoded 127.0.0.1
// This allows LAN access to work properly
const currentHost = window.location.hostname;
const API_BASE = apiPort ? `http://${currentHost}:${apiPort}/api` : `http://${currentHost}:8000/api`;


// Create authenticated axios instance for backend API calls only
const apiClient = axios.create({
    baseURL: API_BASE,
    timeout: 15000,
    headers: authToken ? { 'X-Auth-Token': authToken } : {}
});

// Helper function to normalize path for API
// Backend expects paths relative to public/Posts (e.g., "Markdowns/file.md")
// Frontend uses paths like "/Posts/Markdowns/file.md"
const normalizePathForAPI = (path) => {
    if (!path) return '';

    // Remove leading slash and /Posts/ prefix
    let normalized = path.replace(/^\/+/, ''); // Remove leading slashes
    if (normalized.startsWith('Posts/')) {
        normalized = normalized.substring(6); // Remove 'Posts/' prefix
    }

    return normalized;
};

// State
const fileTree = ref([]);
const fileTreeVisible = ref(true);
const fileTreeWidth = ref(250);
const session = useEditorDocument({
    api: apiClient,
    normalizePath: normalizePathForAPI,
    // The API chooses a new free port on every launch. Drafts must survive it;
    // localStorage already scopes this namespace to the frontend origin.
    storageKey: 'kmblog-editor-draft:v1',
    describeError: error => handleApiError(error, 'Document')
});
const { currentFile, content, saveStatus, lastSaveTime, isDirty, isSaving, isOpening,
    issue, draft, draftWarning, leavePrompt } = session;
const currentFileName = computed(() => currentFile.value?.name || '');
const handleSave = () => session.save();
const handleForceSave = () => {
    if (confirm('覆盖磁盘上的最新版本？当前草稿将替换其他程序的更改。')) return session.save({ force: true });
};
const handleReloadFile = () => session.open(currentFile.value, { reload: true });
const fileTreeLoading = ref(false);
const fileTreeError = ref('');
const notification = ref('');
let notificationTimer;
const notify = message => {
    notification.value = message;
    clearTimeout(notificationTimer);
    notificationTimer = setTimeout(() => { notification.value = ''; }, 4000);
};
const editorScrollTop = ref(0);
const previewScrollTop = ref(0);
const isScrollingFromPreview = ref(false);
const monacoEditorRef = ref(null);
const previewPanelRef = ref(null);
const fileTreeRef = ref(null);
const panelsRef = ref(null);
const cursor = ref({ lineNumber: 1, column: 1 });
const layout = ref('split');
const focusMode = ref(false);
const isNarrow = ref(window.innerWidth <= 900);
const syncScroll = ref(true);
const splitRatio = ref(50);
const resizingPanels = ref(false);
const effectiveLayout = computed(() => focusMode.value ? 'edit' : isNarrow.value && layout.value === 'split' ? 'edit' : layout.value);
try {
    const preferences = JSON.parse(localStorage.getItem('kmblog-editor-layout') || '{}');
    if (['edit', 'split', 'preview'].includes(preferences.layout)) layout.value = preferences.layout;
    if (Number.isFinite(preferences.ratio)) splitRatio.value = Math.max(35, Math.min(70, preferences.ratio));
} catch { /* Layout preferences are optional. */ }
watch([layout, splitRatio], () => {
    try { localStorage.setItem('kmblog-editor-layout', JSON.stringify({ layout: layout.value, ratio: splitRatio.value })); } catch { /* Optional. */ }
});
const setLayout = value => { focusMode.value = false; layout.value = value; };
const toggleFileTree = () => { fileTreeVisible.value = focusMode.value || !fileTreeVisible.value; focusMode.value = false; };
const searchFiles = async () => { focusMode.value = false; fileTreeVisible.value = true; await nextTick(); fileTreeRef.value?.focusSearch(); };
const updateViewport = () => { isNarrow.value = window.innerWidth <= 900; };
const startPanelResize = event => { resizingPanels.value = true; event.currentTarget.setPointerCapture(event.pointerId); event.preventDefault(); };
const resizePanels = event => {
    if (!resizingPanels.value || !panelsRef.value) return;
    const bounds = panelsRef.value.getBoundingClientRect();
    splitRatio.value = Math.round(Math.max(35, Math.min(70, (event.clientX - bounds.left) / bounds.width * 100)));
};
const resizePanelsByKey = event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home'].includes(event.key)) return;
    event.preventDefault();
    splitRatio.value = event.key === 'Home' ? 50 : Math.max(35, Math.min(70, splitRatio.value + (event.key === 'ArrowLeft' ? -5 : 5)));
};
const previewContent = ref('');
let metadataTimer;
watch(content, value => {
    clearTimeout(metadataTimer);
    metadataTimer = setTimeout(() => { previewContent.value = value; }, 180);
});
const documentStats = computed(() => {
    const words = (previewContent.value.match(/[\u3400-\u9fff]|[a-zA-Z0-9]+/g) || []).length;
    return { words, minutes: Math.max(1, Math.ceil(words / 350)) };
});
const coverUrl = computed(() => {
    const image = currentMetadata.value?.img || '';
    return /^(https?:\/\/|\/)/i.test(image) ? image : `/Posts/Images/${image}`;
});
const showGraphPreview = ref(true); // 控制图片卡片预览的显示/隐藏

// Theme management
const { isDarkMode } = useTheme();

// Computed Monaco theme based on global theme
const editorTheme = computed(() => {
    return isDarkMode.value ? 'vs-dark' : 'vs';
});

// 解析当前文件的metadata用于Post组件显示
const currentMetadata = computed(() => {
    if (!previewContent.value) return null;

    try {
        const parsed = fm(previewContent.value);
        return parsed.attributes || null;
    } catch (error) {
        console.error('[EditorPage] Failed to parse front-matter:', error);
        return null;
    }
});

// 检查当前文件是否在 WaterfallGraph 文件夹内
const isWaterfallGraphFile = computed(() => {
    if (!currentFile.value) return false;
    return currentFile.value.path.includes('WaterfallGraph');
});

// 为 Graph 组件准备数据
const graphData = computed(() => {

    if (!isWaterfallGraphFile.value || !currentMetadata.value) {
        return null;
    }

    // 从 metadata 中提取图片路径
    const imgPath = currentMetadata.value.img;

    if (!imgPath) {
        return null;
    }

    // 构建完整的图片 URL
    // imgPath 可能是: "WaterfallGraph/image.jpg" 或 "/Posts/WaterfallGraph/image.jpg"
    let imageUrl;
    if (imgPath.startsWith('/')) {
        imageUrl = imgPath; // 已经是完整路径
    } else if (imgPath.startsWith('Posts/')) {
        imageUrl = '/' + imgPath; // 添加前导斜杠
    } else {
        imageUrl = '/Posts/' + imgPath; // 添加 /Posts/ 前缀
    }

    // 构建 Graph 组件需要的 image 对象
    const data = {
        src: imageUrl,
        alt: currentMetadata.value.title || currentFileName.value,
        title: currentMetadata.value.title || (currentFileName.value ? currentFileName.value.replace('.md', '') : ''),
        date: currentMetadata.value.date || new Date().toLocaleDateString(),
        aspectRatio: currentMetadata.value.aspectRatio || 1,
        dominantColor: currentMetadata.value.dominantColor || 'var(--theme-index)'
    };

    return data;
});

// 切换图片卡片预览显示状态
const toggleGraphPreview = () => {
    showGraphPreview.value = !showGraphPreview.value;
};

// Fetch the current directory tree.
const loadFileTree = async () => {
    fileTreeLoading.value = true;
    fileTreeError.value = '';
    try {
        const response = await apiClient.get('/files/tree');
        fileTree.value = response.data.tree || [];
    } catch (error) {
        fileTreeError.value = handleApiError(error, 'Load File Tree') || '无法加载文件列表';
    } finally {
        fileTreeLoading.value = false;
    }
};

const handleFileSelect = async file => {
    if (file.type !== 'file') return;
    if (await session.open(file)) {
        editorScrollTop.value = previewScrollTop.value = 0;
        if (isNarrow.value) layout.value = 'edit';
        if (isNarrow.value) fileTreeVisible.value = false;
        await nextTick();
        monacoEditorRef.value?.focus();
    }
};

const handleImageFileSelect = async ({ imagePath, mdPath, imageNode }) => {
    const file = { path: mdPath, name: mdPath.split('/').pop(), type: 'file' };
    if (await session.open(file, { createContent: () => generateImageDescriptionTemplate(imagePath, imageNode) })) {
        editorScrollTop.value = previewScrollTop.value = 0;
        if (isNarrow.value) layout.value = 'edit';
        if (isNarrow.value) fileTreeVisible.value = false;
    }
};

// Generate image description template (Task 36)
const generateImageDescriptionTemplate = (imagePath, imageNode) => {
    const filename = imageNode.name;
    const filenameWithoutExt = filename.replace(/\.[^.]+$/, '');

    // 构建相对于 Posts 目录的图片路径
    // imagePath 格式: /Posts/WaterfallGraph/image.jpg
    // 我们需要: WaterfallGraph/image.jpg (相对于 Posts)
    let relativeImgPath = imagePath;
    if (relativeImgPath.startsWith('/Posts/')) {
        relativeImgPath = relativeImgPath.substring(7); // 移除 '/Posts/'
    } else if (relativeImgPath.startsWith('Posts/')) {
        relativeImgPath = relativeImgPath.substring(6); // 移除 'Posts/'
    }

    // 为 WaterfallGraph 图片生成带 metadata 的模板
    const template = `---
title: ${filenameWithoutExt}
date: ${new Date().toISOString().split('T')[0]}
img: ${relativeImgPath}
aspectRatio: 1
dominantColor: var(--theme-index)
---

# ${filenameWithoutExt}

在这里添加图片描述...
`;

    return template;
};

// Handle file create
const handleFileCreate = async ({ folder, fileName }) => {
    if (!fileName) return;

    // Ensure .md extension
    const fullFileName = fileName.endsWith('.md') ? fileName : `${fileName}.md`;
    const filePath = `${folder.path}/${fullFileName}`;
    const normalizedPath = normalizePathForAPI(filePath);


    try {
        await apiClient.post('/files/create', {
            path: normalizedPath,
            name: fileName,
            collection: folder.name
        });


        // Reload file tree
        await loadFileTree();

        // Optionally open the new file
        // Find and select the new file
        const findFile = (nodes, path) => {
            for (const node of nodes) {
                if (node.path === path) return node;
                if (node.children) {
                    const found = findFile(node.children, path);
                    if (found) return found;
                }
            }
            return null;
        };

        const newFile = findFile(fileTree.value, filePath);
        if (newFile) {
            await handleFileSelect(newFile);
        }
    } catch (error) {
        const errorMessage = handleApiError(error, 'Create File');
        if (errorMessage) {
            alert(`创建文件失败\n\n${errorMessage}\n\n文件名: ${fullFileName}`);
        }
    }
};

// Handle file delete
const handleFileDelete = async (file) => {
    if (currentFile.value?.path === file.path && !await session.canLeave()) return;
    try {
        const normalizedPath = normalizePathForAPI(file.path);

        await apiClient.delete('/files/delete', {
            params: { path: normalizedPath }
        });


        // If deleted file was current file, clear editor
        if (currentFile.value && currentFile.value.path === file.path) {
            session.reset();
        }

        // Reload file tree
        await loadFileTree();
    } catch (error) {
        const errorMessage = handleApiError(error, 'Delete File');
        if (errorMessage) {
            alert(`删除文件失败\n\n${errorMessage}\n\n文件: ${file.name}`);
        }
    }
};

// Handle file move
const handleFileMove = async ({ file, targetFolder }) => {
    if (currentFile.value?.path === file.path && !await session.canLeave()) return;

    // Construct new path
    const fileName = file.name;
    const targetFolderPath = normalizePathForAPI(targetFolder.path);
    const newPath = `${targetFolderPath}/${fileName}`;
    const oldPath = normalizePathForAPI(file.path);


    // Don't move if already in target folder
    if (oldPath === newPath) {
        return;
    }

    try {
        const response = await apiClient.post('/files/move', {
            from: oldPath,
            to: newPath
        });


        // Update current file path if it was moved
        if (currentFile.value && currentFile.value.path === file.path) {
            session.relocate(targetFolder.path + '/' + fileName);
        }

        // Reload file tree
        await loadFileTree();
    } catch (error) {
        const errorMessage = handleApiError(error, 'Move File');
        if (errorMessage) {
            alert(`移动文件失败\n\n${errorMessage}\n\n文件: ${file.name}\n目标: ${targetFolder.name}`);
        }
    }
};

// Handle file rename
const handleFileRename = async ({ node, newName }) => {
    if (currentFile.value && (currentFile.value.path === node.path || currentFile.value.path.startsWith(node.path + '/')) && !await session.canLeave()) return;

    const normalizedPath = normalizePathForAPI(node.path);

    try {
        const response = await apiClient.post('/files/rename', {
            path: normalizedPath,
            new_name: newName
        });


        // Update current file path if it was renamed
        if (currentFile.value && (currentFile.value.path === node.path || currentFile.value.path.startsWith(node.path + '/'))) {
            const parentPath = node.path.substring(0, node.path.lastIndexOf('/'));
            const newFileName = node.type === 'folder' || newName.endsWith('.md') ? newName : `${newName}.md`;
            const suffix = currentFile.value.path.slice(node.path.length);
            session.relocate(`${parentPath}/${newFileName}${suffix}`, suffix ? currentFileName.value : newFileName);
        }

        // Reload file tree
        await loadFileTree();
    } catch (error) {
        const errorMessage = handleApiError(error, 'Rename');
        if (errorMessage) {
            alert(`重命名失败\n\n${errorMessage}\n\n原名称: ${node.name}\n新名称: ${newName}`);
        }
    }
};

// Handle folder create
const handleFolderCreate = async ({ parentFolder, folderName }) => {

    const normalizedPath = normalizePathForAPI(parentFolder.path);

    try {
        const response = await apiClient.post('/folders/create', {
            path: normalizedPath,
            name: folderName
        });


        // Reload file tree
        await loadFileTree();
    } catch (error) {
        const errorMessage = handleApiError(error, 'Create Folder');
        if (errorMessage) {
            alert(`创建文件夹失败\n\n${errorMessage}\n\n文件夹名: ${folderName}`);
        }
    }
};

// Handle folder delete
const handleFolderDelete = async (folder) => {
    if (currentFile.value?.path.startsWith(folder.path + '/') && !await session.canLeave()) return;

    const normalizedPath = normalizePathForAPI(folder.path);

    try {
        await apiClient.delete('/folders/delete', {
            params: { path: normalizedPath }
        });


        // If current file was in deleted folder, clear editor
        if (currentFile.value && currentFile.value.path.startsWith(folder.path + '/')) {
            session.reset();
        }

        // Reload file tree
        await loadFileTree();
    } catch (error) {
        const errorMessage = handleApiError(error, 'Delete Folder');
        if (errorMessage) {
            alert(`删除文件夹失败\n\n${errorMessage}\n\n文件夹: ${folder.name}`);
        }
    }
};

// Handle external file drop (for WaterfallGraph folder)
const handleExternalFileDrop = async ({ files, targetFolder }) => {

    if (!files || files.length === 0) {
        console.warn('[EditorPage] No files to upload');
        return;
    }

    // 确认上传
    const confirmMessage = `📤 上传图片到 ${targetFolder.name}\n\n` +
        `将上传 ${files.length} 个文件:\n` +
        files.map(f => `• ${f.name}`).join('\n') +
        `\n\n确认上传?`;

    if (!confirm(confirmMessage)) {
        return;
    }

    const normalizedPath = normalizePathForAPI(targetFolder.path);
    let successCount = 0;
    let failCount = 0;
    const errors = [];

    // 显示上传进度

    for (const file of files) {
        try {

            const formData = new FormData();
            formData.append('file', file);
            formData.append('path', normalizedPath);

            await apiClient.post('/files/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            successCount++;
        } catch (error) {
            failCount++;
            const errorMessage = handleApiError(error, `Upload ${file.name}`);
            errors.push(`${file.name}: ${errorMessage || '未知错误'}`);
            console.error(`[EditorPage] ✗ Failed: ${file.name}`, error);
        }
    }

    // 显示结果
    let resultMessage = `📊 上传完成\n\n`;
    resultMessage += `✓ 成功: ${successCount} 个文件\n`;
    if (failCount > 0) {
        resultMessage += `✗ 失败: ${failCount} 个文件\n\n`;
        resultMessage += `失败详情:\n${errors.join('\n')}`;
    }

    alert(resultMessage);

    // 重新加载文件树
    if (successCount > 0) {
        await loadFileTree();
    }
};

// Handle editor scroll
const handleEditorScroll = (scrollPercentage) => {
    if (!syncScroll.value || effectiveLayout.value !== 'split' || isScrollingFromPreview.value) return; // 如果是预览触发的滚动，忽略
    editorScrollTop.value = scrollPercentage;
};

// Handle preview scroll
let previewScrollTimer;
const handlePreviewScroll = (scrollPercentage) => {
    if (!syncScroll.value || effectiveLayout.value !== 'split') return;
    isScrollingFromPreview.value = true;
    previewScrollTop.value = scrollPercentage;

    // 重置标记
    clearTimeout(previewScrollTimer);
    previewScrollTimer = setTimeout(() => {
        isScrollingFromPreview.value = false;
    }, 100);
};

// Handle format insertion
const handleInsertFormat = (format) => {
    if (isOpening.value || draft.value) return;
    if (!monacoEditorRef.value) return;

    const editor = monacoEditorRef.value.getEditor();
    if (!editor) return;

    const selection = editor.getSelection();
    const selectedText = editor.getModel().getValueInRange(selection);
    const position = editor.getPosition();

    let insertText = '';
    let cursorOffset = 0;

    // 处理多级标题
    if (format.startsWith('heading-')) {
        const level = parseInt(format.split('-')[1]);
        const hashes = '#'.repeat(level);
        insertText = `${hashes} ${selectedText || '标题'}`;
        cursorOffset = selectedText ? 0 : 0;
    }
    // 处理颜色
    else if (format.startsWith('color:')) {
        const color = format.split(':')[1];
        insertText = `<span style="color: ${color}">${selectedText || '彩色文本'}</span>`;
        cursorOffset = selectedText ? 0 : -7;
    }
    // 处理背景颜色
    else if (format.startsWith('bgcolor:')) {
        const color = format.split(':')[1];
        insertText = `<span style="background-color: ${color}">${selectedText || '高亮文本'}</span>`;
        cursorOffset = selectedText ? 0 : -7;
    }
    // 处理字体大小
    else if (format.startsWith('fontsize:')) {
        const size = format.split(':')[1];
        insertText = `<span style="font-size: ${size}">${selectedText || '文本'}</span>`;
        cursorOffset = selectedText ? 0 : -7;
    }
    // 处理符号插入
    else if (format.startsWith('symbol:')) {
        const symbol = format.split(':')[1];
        insertText = symbol;
        cursorOffset = 0;
    }
    else {
        switch (format) {
            case 'bold':
                insertText = `**${selectedText || '粗体文本'}**`;
                cursorOffset = selectedText ? 0 : -2;
                break;
            case 'italic':
                insertText = `*${selectedText || '斜体文本'}*`;
                cursorOffset = selectedText ? 0 : -1;
                break;
            case 'strikethrough':
                insertText = `~~${selectedText || '删除线文本'}~~`;
                cursorOffset = selectedText ? 0 : -2;
                break;
            case 'underline':
                insertText = `<u>${selectedText || '下划线文本'}</u>`;
                cursorOffset = selectedText ? 0 : -4;
                break;
            case 'quote':
                insertText = `> ${selectedText || '引用文本'}`;
                cursorOffset = selectedText ? 0 : 0;
                break;
            case 'link':
                insertText = `[${selectedText || '链接文本'}](url)`;
                cursorOffset = selectedText ? -4 : -9;
                break;
            case 'image':
                insertText = `![${selectedText || '图片描述'}](url)`;
                cursorOffset = selectedText ? -4 : -10;
                break;
            case 'code':
                insertText = '```\n' + (selectedText || '代码') + '\n```';
                cursorOffset = selectedText ? 0 : -4;
                break;
            case 'inline-code':
                insertText = `\`${selectedText || '代码'}\``;
                cursorOffset = selectedText ? 0 : -1;
                break;
            case 'ul':
                insertText = `- ${selectedText || '列表项'}`;
                cursorOffset = selectedText ? 0 : 0;
                break;
            case 'ol':
                insertText = `1. ${selectedText || '列表项'}`;
                cursorOffset = selectedText ? 0 : 0;
                break;
            case 'task':
                insertText = `- [ ] ${selectedText || '任务项'}`;
                cursorOffset = selectedText ? 0 : 0;
                break;
            case 'table':
                insertText = '| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n| 内容 | 内容 | 内容 |';
                cursorOffset = 0;
                break;
            case 'hr':
                insertText = '\n---\n';
                cursorOffset = 0;
                break;
            case 'align-left':
                insertText = `<div style="text-align: left">\n\n${selectedText || '左对齐文本'}\n\n</div>`;
                cursorOffset = selectedText ? 0 : -7;
                break;
            case 'align-center':
                insertText = `<center>\n\n${selectedText || '居中文本'}\n\n</center>`;
                cursorOffset = selectedText ? 0 : -10;
                break;
            case 'align-right':
                insertText = `<div style="text-align: right">\n\n${selectedText || '右对齐文本'}\n\n</div>`;
                cursorOffset = selectedText ? 0 : -7;
                break;
            case 'align-justify':
                insertText = `<div style="text-align: justify">\n\n${selectedText || '两端对齐文本'}\n\n</div>`;
                cursorOffset = selectedText ? 0 : -7;
                break;
            case 'superscript':
                insertText = `<sup>${selectedText || '上标'}</sup>`;
                cursorOffset = selectedText ? 0 : -6;
                break;
            case 'subscript':
                insertText = `<sub>${selectedText || '下标'}</sub>`;
                cursorOffset = selectedText ? 0 : -6;
                break;
            case 'mark':
                insertText = `<mark>${selectedText || '高亮文本'}</mark>`;
                cursorOffset = selectedText ? 0 : -7;
                break;
            default:
                return;
        }
    }

    // Insert text
    editor.executeEdits('', [{
        range: selection,
        text: insertText
    }]);

    // Adjust cursor position
    if (cursorOffset !== 0) {
        const newPosition = editor.getPosition();
        editor.setPosition({
            lineNumber: newPosition.lineNumber,
            column: newPosition.column + cursorOffset
        });
    }

    editor.focus();
};

// Handle block insertion
const handleInsertBlock = (blockType) => {
    if (isOpening.value || draft.value) return;
    if (!monacoEditorRef.value) return;

    const editor = monacoEditorRef.value.getEditor();
    if (!editor) return;

    const blockTemplates = {
        'bilibili-video': '```bilibili-video\nhttps://www.bilibili.com/video/BV...\n```',
        'steam-game': '```steam-game\nhttps://store.steampowered.com/app/...\n```',
        'bangumi-card': '```bangumi-card\nhttps://bgm.tv/subject/...\n```',
        'github-repo': '```github-repo\nhttps://github.com/user/repo\n```',
        'xiaohongshu-note': '```xiaohongshu-note\nhttps://www.xiaohongshu.com/explore/...\n```',
        'mermaid': '```mermaid\ngraph TD\n  A[开始] --> B[结束]\n```'
    };

    const template = blockTemplates[blockType];
    if (!template) return;

    const position = editor.getPosition();
    const lineContent = editor.getModel().getLineContent(position.lineNumber);

    // Insert on new line if current line is not empty
    const insertText = lineContent.trim() ? '\n\n' + template + '\n\n' : template + '\n\n';

    editor.executeEdits('', [{
        range: {
            startLineNumber: position.lineNumber,
            startColumn: position.column,
            endLineNumber: position.lineNumber,
            endColumn: position.column
        },
        text: insertText
    }]);

    editor.focus();
};

const downloadDraft = () => {
    const blob = new Blob([content.value], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = currentFileName.value || 'draft.md';
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
};
const handleFocusEscape = event => { if (event.key === 'Escape') focusMode.value = false; };
const handleEditorShortcut = event => {
    if (event.defaultPrevented) return;
    if (event.key === 'Escape' && focusMode.value) { focusMode.value = false; return; }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'p') { event.preventDefault(); void searchFiles(); return; }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
        event.preventDefault();
        if (!isOpening.value) void handleSave();
    }
};
onBeforeRouteLeave(() => session.canLeave());

// Before unload handler - warn about unsaved changes
const handleBeforeUnload = (e) => {
    session.persistDraft();
    if (isDirty.value || isSaving.value) {
        e.preventDefault();
        e.returnValue = '您有未保存的更改,确定要离开吗?';
        return e.returnValue;
    }
};

// Lifecycle hooks
onMounted(async () => {
    // Add beforeunload listener
    window.addEventListener('beforeunload', handleBeforeUnload);
    window.addEventListener('keydown', handleEditorShortcut);
    window.addEventListener('keydown', handleFocusEscape, true);
    window.addEventListener('resize', updateViewport);

    // Load file tree
    await loadFileTree();
});

onBeforeUnmount(() => {
    clearTimeout(metadataTimer);
    clearTimeout(previewScrollTimer);
    window.removeEventListener('resize', updateViewport);
    // Clean up
    window.removeEventListener('beforeunload', handleBeforeUnload);
    clearTimeout(notificationTimer);
    window.removeEventListener('keydown', handleEditorShortcut);
    window.removeEventListener('keydown', handleFocusEscape, true);

});
</script>

<style scoped>
.editor-notice { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; padding: 10px 18px; background: var(--theme-surface-default); border-bottom: 1px solid var(--theme-panel-border); font-size: 13px; line-height: 1.6; flex-shrink: 0; }
.editor-notice > span:first-child { flex: 1; min-width: 180px; }
.editor-notice.error { border-left: 3px solid #c24b36; }
.editor-notice button, .editor-empty button { border: 1px solid var(--theme-panel-border); background: var(--theme-panel-bg); color: var(--theme-body-text); border-radius: 6px; padding: 6px 12px; cursor: pointer; }
.editor-notice button:focus-visible, .editor-empty button:focus-visible { outline: 2px solid var(--theme-primary); outline-offset: 2px; }
.editor-empty { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; padding: 28px; text-align: center; }
.editor-empty h1 { font-size: 24px; margin: 0; }
.editor-empty p { max-width: 420px; line-height: 1.8; color: var(--theme-meta-text); margin: 0 0 10px; }
.empty-mark { font-size: 52px; color: var(--theme-primary); }

.editor-container { display: flex; height: 100vh; height: 100dvh; width: 100%; overflow: hidden; background: var(--theme-body-bg); color: var(--theme-body-text); }
.main-editor { flex: 1; min-width: 0; display: flex; flex-direction: column; overflow: hidden; }
.workspace-bar { display: flex; gap: 12px; align-items: center; min-height: 46px; padding: 6px 16px; border-bottom: 1px solid var(--theme-panel-border); background: var(--theme-panel-bg); flex-shrink: 0; }
.workspace-bar button { border: 1px solid var(--theme-panel-border); border-radius: 5px; background: transparent; color: inherit; padding: 6px 10px; cursor: pointer; font-size: 12px; white-space: nowrap; }
.workspace-bar button:focus-visible, .panel-splitter:focus-visible { outline: 2px solid var(--theme-primary); outline-offset: -2px; }
.workspace-bar .path-button { flex: 1; display: flex; gap: 6px; min-width: 0; border: 0; text-align: left; color: var(--theme-meta-text); }
.path-button span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.view-switch { display: flex; gap: 2px; }
.view-switch button[aria-pressed="true"], .workspace-bar > button[aria-pressed="true"] { color: var(--theme-primary); background: var(--theme-surface-hover); border-color: var(--theme-primary); }
.sync-toggle { display: flex; align-items: center; gap: 4px; font-size: 12px; white-space: nowrap; }
.editor-panels { flex: 1; min-height: 0; display: flex; overflow: hidden; }
.edit-panel, .preview-panel { flex: 1; min-width: 0; min-height: 0; overflow: hidden; }
.layout-split .edit-panel { flex: 0 0 var(--editor-width, 50%); }
.preview-panel { overflow-y: auto; background: var(--theme-panel-bg); }
.panel-splitter { flex: 0 0 6px; cursor: col-resize; touch-action: none; background: var(--theme-panel-border); }
.panel-splitter:hover, .panel-splitter:focus-visible { background: var(--theme-primary); }
.metadata-preview, .graph-preview-section { margin: 16px 20px 0; border: 1px solid var(--theme-panel-border); border-radius: 8px; }
.metadata-preview summary { cursor: pointer; padding: 12px; font-size: 12px; }
.metadata-preview summary span { float: right; color: var(--theme-meta-text); }
.metadata-card { padding: 12px 20px; }
.metadata-card img { width: 100%; max-height: 180px; object-fit: cover; border-radius: 6px; }
.metadata-card h2 { margin: 12px 0; font-size: 23px; }
.metadata-card p { font-size: 14px; line-height: 1.7; }
.metadata-card small, .metadata-tags { color: var(--theme-meta-text); }
.preview-header { display: flex; justify-content: space-between; align-items: center; padding: 10px; }
.preview-label { color: var(--theme-meta-text); font-size: 12px; padding: 12px 20px 0; }
.collapse-btn { width: 28px; height: 28px; border: 0; border-radius: 5px; color: inherit; background: var(--theme-surface-hover); cursor: pointer; }
.collapse-btn svg { width: 16px; }
.collapse-btn.collapsed svg { transform: rotate(-90deg); }
.graph-preview-wrapper { max-width: 400px; margin: 16px auto; }
.editor-statusbar { display: flex; justify-content: space-between; gap: 12px; padding: 7px 16px; border-top: 1px solid var(--theme-panel-border); color: var(--theme-meta-text); font-size: 11px; flex-shrink: 0; font-variant-numeric: tabular-nums; }
.focus-mode :deep(.toolbar-tools > .tool-group), .focus-mode :deep(.toolbar-tools > .dropdown), .focus-mode :deep(.toolbar-tools > .divider), .focus-mode :deep(.toolbar-tools > .format-btn), .focus-mode :deep(.mobile-tools-toggle) { display: none; }
.focus-mode .edit-panel { max-width: 1000px; margin: 0 auto; }
.sidebar-backdrop { display: none; }
@media (max-width: 900px) {
    .workspace-bar { padding: 6px 8px; gap: 5px; }
    .sync-toggle { display: none; }
    .editor-container > :deep(.ethereal-sidebar) { position: fixed; top: 0; bottom: 0; left: 0; z-index: 1501; max-width: 85vw; }
    .sidebar-backdrop { display: block; position: fixed; inset: 0; z-index: 1500; border: 0; background: #0006; }
    .editor-statusbar { padding: 7px 8px; font-size: 10px; }
    .cursor-position { display: none; }
}
@media (prefers-reduced-motion: reduce) { .editor-container :deep(*) { animation: none !important; transition: none !important; } }
</style>
