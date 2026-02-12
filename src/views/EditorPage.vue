<template>
    <div class="editor-container">
        <!-- File Tree Sidebar -->
        <FileTreeSidebar v-model:visible="fileTreeVisible" v-model:width="fileTreeWidth" :files="fileTree"
            :current-file="currentFile" @file-select="handleFileSelect" @file-create="handleFileCreate"
            @file-delete="handleFileDelete" @file-move="handleFileMove" @file-rename="handleFileRename"
            @folder-create="handleFolderCreate" @folder-delete="handleFolderDelete"
            @image-file-select="handleImageFileSelect" @external-file-drop="handleExternalFileDrop" />

        <!-- Main Editor Area -->
        <div class="main-editor">
            <!-- Toolbar -->
            <EditorToolbar :save-status="saveStatus" :file-name="currentFileName" :last-save-time="lastSaveTime"
                @save="handleSave" @insert-format="handleInsertFormat" @insert-block="handleInsertBlock"
                @toggle-file-tree="fileTreeVisible = !fileTreeVisible" />

            <!-- Mobile View Toggle -->
            <div class="mobile-view-toggle">
                <button @click="mobileView = 'edit'" :class="{ active: mobileView === 'edit' }" class="view-toggle-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                    </svg>
                    <span>编辑</span>
                </button>
                <button @click="mobileView = 'preview'" :class="{ active: mobileView === 'preview' }"
                    class="view-toggle-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                        <circle cx="12" cy="12" r="3" />
                    </svg>
                    <span>预览</span>
                </button>
            </div>

            <!-- Editor and Preview Panels -->
            <div class="editor-panels">
                <!-- Edit Panel -->
                <div class="edit-panel" :class="{ 'mobile-hidden': mobileView === 'preview' }">
                    <MonacoEditor v-model="content" language="markdown" :theme="editorTheme"
                        :current-file-name="currentFileName" :api-base="API_BASE" :scroll-sync="previewScrollTop"
                        @change="handleContentChange" @scroll="handleEditorScroll" @format-request="handleInsertFormat"
                        ref="monacoEditorRef" />
                </div>

                <!-- Preview Panel -->
                <div class="preview-panel" :class="{ 'mobile-hidden': mobileView === 'edit' }" ref="previewPanelRef">
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

                    <!-- 普通文章预览 - 使用 Post 组件 -->
                    <div v-else-if="currentMetadata && currentFile && !isWaterfallGraphFile"
                        class="post-preview-section">
                        <div class="preview-header">
                            <div class="preview-label">文章卡片预览</div>
                            <button @click="togglePostPreview" class="collapse-btn"
                                :class="{ 'collapsed': !showPostPreview }">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </button>
                        </div>
                        <div v-show="showPostPreview" class="post-preview-content">
                            <Post :key="postPreviewKey"
                                :imageUrl="currentMetadata.img ? `/Posts/Images/${currentMetadata.img}` : ''"
                                :markdownUrl="virtualMarkdownUrl" />
                        </div>
                    </div>

                    <!-- Markdown内容预览 -->
                    <div class="markdown-preview-section">
                        <div v-if="currentMetadata || isWaterfallGraphFile" class="preview-label">Markdown渲染预览</div>
                        <MarkdownPreview :content="content" :scroll-sync="editorScrollTop"
                            @scroll="handlePreviewScroll" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import axios from 'axios';
import fm from 'front-matter';
import MonacoEditor from '@/components/Editor/MonacoEditor.vue';
import MarkdownPreview from '@/components/Editor/MarkdownPreview.vue';
import FileTreeSidebar from '@/components/Editor/FileTreeSidebar.vue';
import EditorToolbar from '@/components/Editor/EditorToolbar.vue';
import Post from '@/components/PostPanelComps/Post.vue';
import Graph from '@/components/WaterfallPanelComps/Graph.vue';
import { useTheme } from '@/composables/useTheme';

// Error handling utility
const handleApiError = (error, context = '') => {
    // Log detailed error for debugging
    console.error(`[EditorPage] ${context} Error:`, error);

    if (axios.isCancel(error)) {
        // Silently ignore cancellation errors
        console.log(`[EditorPage] ${context} Request cancelled`);
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

console.log('URL Hash:', window.location.hash);
console.log('Auth Token:', authToken ? 'Present' : 'Missing');
console.log('API Port:', apiPort);

// Use current hostname instead of hardcoded 127.0.0.1
// This allows LAN access to work properly
const currentHost = window.location.hostname;
const API_BASE = apiPort ? `http://${currentHost}:${apiPort}/api` : `http://${currentHost}:8000/api`;

console.log('API Base URL:', API_BASE);

// Create authenticated axios instance for backend API calls only
const apiClient = axios.create({
    baseURL: API_BASE,
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
const currentFile = ref(null);
const currentFileName = ref(null);
const content = ref('');
const saveStatus = ref('saved'); // 'saved', 'saving', 'unsaved'
const lastSaveTime = ref(null); // 上次保存时间戳
const editorScrollTop = ref(0);
const previewScrollTop = ref(0);
const isScrollingFromPreview = ref(false);
const monacoEditorRef = ref(null);
const currentFileVersion = ref(null); // Store file version for conflict detection
const previewPanelRef = ref(null);
const mobileView = ref('edit'); // 'edit' or 'preview' - for mobile view toggle
const showPostPreview = ref(true); // 控制文章卡片预览的显示/隐藏
const showGraphPreview = ref(true); // 控制图片卡片预览的显示/隐藏
const postPreviewKey = ref(0); // 用于强制刷新 Post 组件

// Theme management
const { currentMode, isDarkMode } = useTheme();

// Computed Monaco theme based on global theme
const editorTheme = computed(() => {
    return isDarkMode.value ? 'vs-dark' : 'vs';
});

// 解析当前文件的metadata用于Post组件显示
const currentMetadata = computed(() => {
    if (!content.value) return null;

    try {
        const parsed = fm(content.value);
        return parsed.attributes || null;
    } catch (error) {
        console.error('[EditorPage] Failed to parse front-matter:', error);
        return null;
    }
});

// 为Post组件生成虚拟的markdownUrl
const virtualMarkdownUrl = computed(() => {
    if (!currentFile.value) return '';
    return currentFile.value.path;
});

// 检查当前文件是否在 WaterfallGraph 文件夹内
const isWaterfallGraphFile = computed(() => {
    if (!currentFile.value) return false;
    return currentFile.value.path.includes('WaterfallGraph');
});

// 为 Graph 组件准备数据
const graphData = computed(() => {
    console.log('[EditorPage] Computing graphData...');
    console.log('[EditorPage] isWaterfallGraphFile:', isWaterfallGraphFile.value);
    console.log('[EditorPage] currentMetadata:', currentMetadata.value);

    if (!isWaterfallGraphFile.value || !currentMetadata.value) {
        console.log('[EditorPage] graphData is null - conditions not met');
        return null;
    }

    // 从 metadata 中提取图片路径
    const imgPath = currentMetadata.value.img;
    console.log('[EditorPage] imgPath from metadata:', imgPath);

    if (!imgPath) {
        console.log('[EditorPage] graphData is null - no img in metadata');
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
    console.log('[EditorPage] Constructed imageUrl:', imageUrl);

    // 构建 Graph 组件需要的 image 对象
    const data = {
        src: imageUrl,
        alt: currentMetadata.value.title || currentFileName.value,
        title: currentMetadata.value.title || (currentFileName.value ? currentFileName.value.replace('.md', '') : ''),
        date: currentMetadata.value.date || new Date().toLocaleDateString(),
        aspectRatio: currentMetadata.value.aspectRatio || 1,
        dominantColor: currentMetadata.value.dominantColor || 'hsl(250, 60%, 65%)'
    };

    console.log('[EditorPage] graphData computed:', data);
    return data;
});

// Request cancellation and queue management
let currentLoadRequest = null; // Track current file load request
const pendingRequests = new Set(); // Track all pending requests

// Create axios instance with request tracking (uses apiClient for authenticated requests)
const createTrackedRequest = (config) => {
    const source = axios.CancelToken.source();
    const request = apiClient({
        ...config,
        cancelToken: source.token
    });

    // Track this request
    pendingRequests.add(source);

    // Remove from tracking when done (suppress cancellation errors in console)
    request
        .catch(error => {
            // Silently ignore cancellation errors
            if (!axios.isCancel(error)) {
                throw error; // Re-throw non-cancellation errors
            }
        })
        .finally(() => {
            pendingRequests.delete(source);
        });

    return { request, cancel: source.cancel };
};

// Auto-save timer
let autoSaveTimer = null;

// 切换文章卡片预览显示状态
const togglePostPreview = () => {
    showPostPreview.value = !showPostPreview.value;
};

// 切换图片卡片预览显示状态
const toggleGraphPreview = () => {
    showGraphPreview.value = !showGraphPreview.value;
};

// 强制刷新 Post 组件
const refreshPostPreview = () => {
    postPreviewKey.value++;
    console.log('[EditorPage] Post preview refreshed, key:', postPreviewKey.value);
};

// Handle content change
const handleContentChange = () => {
    saveStatus.value = 'unsaved';

    // Clear previous timer
    if (autoSaveTimer) {
        clearTimeout(autoSaveTimer);
    }

    // Auto-save after 3 seconds
    autoSaveTimer = setTimeout(() => {
        handleSave();
    }, 3000);
};

// Handle save
const handleSave = async () => {
    if (!currentFile.value) {
        console.warn('[EditorPage] No file selected');
        return;
    }

    saveStatus.value = 'saving';

    try {
        const normalizedPath = normalizePathForAPI(currentFile.value.path);
        console.log('[EditorPage] Saving file:', currentFile.value.path, '-> API path:', normalizedPath);

        const response = await apiClient.post('/files/save', {
            path: normalizedPath,
            content: content.value,
            expectedVersion: currentFileVersion.value
        });

        saveStatus.value = 'saved';
        currentFileVersion.value = response.data.version;
        lastSaveTime.value = Date.now(); // 记录保存时间

        // 保存成功后刷新 Post 预览组件
        refreshPostPreview();

        console.log('[EditorPage] File saved successfully');
    } catch (error) {
        const errorMessage = handleApiError(error, 'Save');

        // If it's a version conflict (409), handle separately
        if (error.response && error.response.status === 409) {
            saveStatus.value = 'unsaved';
            await handleVersionConflict(error.response.data);
        } else if (errorMessage) {
            // Show user-friendly error message
            alert(`保存失败\n\n${errorMessage}`);
            saveStatus.value = 'unsaved';
        }
    }
};

// Handle version conflict
const handleVersionConflict = async (conflictData) => {
    console.log('[EditorPage] Version conflict detected:', conflictData);

    const message =
        '⚠️ 文件版本冲突\n\n' +
        '文件已被其他进程修改。这可能是因为:\n' +
        '• 在另一个编辑器中修改了文件\n' +
        '• 文件系统直接修改了文件\n' +
        '• 另一个用户修改了文件\n\n' +
        '请选择如何处理:\n\n' +
        '【确定】强制保存当前内容(覆盖其他更改)\n' +
        '【取消】重新加载文件(丢弃当前更改)';

    const userChoice = confirm(message);

    if (userChoice) {
        // Force save without version check
        await handleForceSave();
    } else {
        // Reload file from server
        await handleReloadFile();
    }
};

// Force save without version check
const handleForceSave = async () => {
    if (!currentFile.value) return;

    console.log('[EditorPage] Force saving file...');
    saveStatus.value = 'saving';

    try {
        const normalizedPath = normalizePathForAPI(currentFile.value.path);
        const response = await apiClient.post('/files/save', {
            path: normalizedPath,
            content: content.value
            // No expectedVersion - force save
        });

        saveStatus.value = 'saved';
        currentFileVersion.value = response.data.version;

        // 强制保存成功后也刷新 Post 预览组件
        refreshPostPreview();

        console.log('[EditorPage] Force save successful');

        // Show success message
        alert('✓ 强制保存成功\n\n文件已更新为当前内容');
    } catch (error) {
        const errorMessage = handleApiError(error, 'Force Save');
        if (errorMessage) {
            alert(`强制保存失败\n\n${errorMessage}\n\n请检查文件权限或稍后重试`);
        }
        saveStatus.value = 'unsaved';
    }
};

// Reload file from server
const handleReloadFile = async () => {
    if (!currentFile.value) return;

    console.log('[EditorPage] Reloading file from server...');

    const shouldProceed = confirm(
        '⚠️ 确认重新加载\n\n' +
        '这将丢弃所有未保存的更改。\n\n' +
        '是否继续?'
    );

    if (!shouldProceed) {
        saveStatus.value = 'unsaved';
        return;
    }

    try {
        const normalizedPath = normalizePathForAPI(currentFile.value.path);
        console.log('[EditorPage] Reloading file:', normalizedPath);

        const response = await apiClient.get('/files/read', {
            params: { path: normalizedPath }
        });

        content.value = response.data.content;
        currentFileVersion.value = response.data.version;
        saveStatus.value = 'saved';

        console.log('[EditorPage] File reloaded successfully');
        alert('✓ 文件已重新加载\n\n已从服务器获取最新版本');
    } catch (error) {
        const errorMessage = handleApiError(error, 'Reload File');
        if (errorMessage) {
            alert(`重新加载失败\n\n${errorMessage}\n\n请手动刷新页面`);
        }
    }
};

// Load file tree
const loadFileTree = async () => {
    try {
        const response = await apiClient.get('/files/tree');
        fileTree.value = response.data.tree || [];
        console.log('[EditorPage] File tree loaded:', fileTree.value.length, 'items');
    } catch (error) {
        const errorMessage = handleApiError(error, 'Load File Tree');
        if (errorMessage) {
            alert(`加载文件树失败\n\n${errorMessage}`);
        }
    }
};

// Handle file select
const handleFileSelect = async (file) => {
    if (file.type !== 'file') return;

    // Cancel previous file load request if still pending
    if (currentLoadRequest) {
        console.log('[EditorPage] Cancelling previous file load request');
        currentLoadRequest.cancel('New file selected');
        currentLoadRequest = null;
    }

    // Check for unsaved changes
    if (saveStatus.value === 'unsaved') {
        const shouldSave = confirm('当前文件有未保存的更改,是否保存?');
        if (shouldSave) {
            await handleSave();
        }
    }

    try {
        const normalizedPath = normalizePathForAPI(file.path);
        console.log('[EditorPage] Loading file:', file.path, '-> API path:', normalizedPath);

        // Create tracked request
        const { request, cancel } = createTrackedRequest({
            method: 'get',
            url: '/files/read',
            params: { path: normalizedPath }
        });

        // Store cancel function
        currentLoadRequest = { cancel };

        const response = await request;

        currentFile.value = file;
        currentFileName.value = file.name;
        content.value = response.data.content;
        currentFileVersion.value = response.data.version;
        saveStatus.value = 'saved';
        currentLoadRequest = null;

        console.log('[EditorPage] File loaded successfully');
    } catch (error) {
        currentLoadRequest = null;

        const errorMessage = handleApiError(error, 'Load File');
        if (errorMessage) {
            alert(`加载文件失败\n\n${errorMessage}\n\n文件: ${file.name}`);
        }
    }
};

// Handle image file select (Task 35)
const handleImageFileSelect = async ({ imagePath, mdPath, exists, imageNode }) => {
    console.log('[EditorPage] Image file selected:', imagePath);
    console.log('[EditorPage] Associated .md path:', mdPath);

    // Cancel previous file load request if still pending
    if (currentLoadRequest) {
        console.log('[EditorPage] Cancelling previous file load request');
        currentLoadRequest.cancel('New image file selected');
        currentLoadRequest = null;
    }

    // Check for unsaved changes
    if (saveStatus.value === 'unsaved') {
        const shouldSave = confirm('当前文件有未保存的更改,是否保存?');
        if (shouldSave) {
            await handleSave();
        }
    }

    // Task 35.2: 通过后端 API 检查 .md 文件是否存在
    const normalizedPath = normalizePathForAPI(mdPath);
    console.log('[EditorPage] Checking if .md file exists:', mdPath, '-> API path:', normalizedPath);

    try {
        // 尝试读取 .md 文件
        const { request, cancel } = createTrackedRequest({
            method: 'get',
            url: '/files/read',
            params: { path: normalizedPath }
        });

        currentLoadRequest = { cancel };
        const response = await request;

        // Task 35.3: 如果存在则加载 .md 文件
        console.log('[EditorPage] .md file exists, loading...');

        // Create a virtual file node for the .md file
        const mdFile = {
            path: mdPath,
            name: mdPath.split('/').pop(),
            type: 'file'
        };

        currentFile.value = mdFile;
        currentFileName.value = mdFile.name;
        content.value = response.data.content;
        currentFileVersion.value = response.data.version;
        saveStatus.value = 'saved';
        currentLoadRequest = null;

        console.log('[EditorPage] .md file loaded successfully');
    } catch (error) {
        currentLoadRequest = null;

        // 如果是 404 错误，说明文件不存在，创建模板
        if (error.response && error.response.status === 404) {
            // Task 35.4: 如果不存在则创建模板
            console.log('[EditorPage] .md file does not exist (404), creating template');

            // Generate template
            const template = generateImageDescriptionTemplate(imagePath, imageNode);

            // Create a virtual file node for the new .md file
            const mdFile = {
                path: mdPath,
                name: mdPath.split('/').pop(),
                type: 'file'
            };

            currentFile.value = mdFile;
            currentFileName.value = mdFile.name;
            content.value = template;
            currentFileVersion.value = null; // New file, no version yet
            saveStatus.value = 'unsaved'; // Mark as unsaved since it's a new file

            console.log('[EditorPage] Template created for image description');

            // Show notification
            alert(`✨ 已为图片创建描述模板\n\n图片: ${imageNode.name}\n描述文件: ${mdFile.name}\n\n请编辑并保存以创建描述文件。`);
        } else {
            // 其他错误
            const errorMessage = handleApiError(error, 'Load Image Description');
            if (errorMessage) {
                alert(`加载图片描述文件失败\n\n${errorMessage}\n\n文件: ${mdPath}`);
            }
        }
    }

    // Task 35.5: 在预览区显示图片
    // Note: This would require adding image preview functionality to the preview panel
    // For now, the markdown preview will show the image when the template is rendered
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
dominantColor: hsl(250, 60%, 65%)
---

# ${filenameWithoutExt}

在这里添加图片描述...
`;

    console.log('[EditorPage] Generated template for image:', filename);
    console.log('[EditorPage] Image path in metadata:', relativeImgPath);
    return template;
};

// Handle file create
const handleFileCreate = async ({ folder, fileName }) => {
    if (!fileName) return;

    // Ensure .md extension
    const fullFileName = fileName.endsWith('.md') ? fileName : `${fileName}.md`;
    const filePath = `${folder.path}/${fullFileName}`;
    const normalizedPath = normalizePathForAPI(filePath);

    console.log('[EditorPage] Creating file:', filePath, '-> API path:', normalizedPath);

    try {
        await apiClient.post('/files/create', {
            path: normalizedPath,
            name: fileName,
            collection: folder.name
        });

        console.log('[EditorPage] File created successfully');

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
    try {
        const normalizedPath = normalizePathForAPI(file.path);
        console.log('[EditorPage] Deleting file:', file.path, '-> API path:', normalizedPath);

        await apiClient.delete('/files/delete', {
            params: { path: normalizedPath }
        });

        console.log('[EditorPage] File deleted successfully');

        // If deleted file was current file, clear editor
        if (currentFile.value && currentFile.value.path === file.path) {
            currentFile.value = null;
            currentFileName.value = null;
            content.value = '';
            currentFileVersion.value = null;
            saveStatus.value = 'saved';
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
    console.log('[EditorPage] handleFileMove called');
    console.log('[EditorPage] File:', file);
    console.log('[EditorPage] Target folder:', targetFolder);

    // Construct new path
    const fileName = file.name;
    const targetFolderPath = normalizePathForAPI(targetFolder.path);
    const newPath = `${targetFolderPath}/${fileName}`;
    const oldPath = normalizePathForAPI(file.path);

    console.log('[EditorPage] API paths - from:', oldPath, 'to:', newPath);

    // Don't move if already in target folder
    if (oldPath === newPath) {
        console.log('[EditorPage] Same path, skipping move');
        return;
    }

    try {
        console.log('[EditorPage] Sending move request to API...');
        const response = await apiClient.post('/files/move', {
            from: oldPath,
            to: newPath
        });

        console.log('[EditorPage] Move response:', response.data);
        console.log('[EditorPage] File moved successfully');

        // Update current file path if it was moved
        if (currentFile.value && currentFile.value.path === file.path) {
            currentFile.value.path = targetFolder.path + '/' + fileName;
            console.log('[EditorPage] Updated current file path');
        }

        // Reload file tree
        console.log('[EditorPage] Reloading file tree...');
        await loadFileTree();
        console.log('[EditorPage] File tree reloaded');
    } catch (error) {
        const errorMessage = handleApiError(error, 'Move File');
        if (errorMessage) {
            alert(`移动文件失败\n\n${errorMessage}\n\n文件: ${file.name}\n目标: ${targetFolder.name}`);
        }
    }
};

// Handle file rename
const handleFileRename = async ({ node, newName }) => {
    console.log('[EditorPage] handleFileRename called');
    console.log('[EditorPage] Node:', node);
    console.log('[EditorPage] New name:', newName);

    const normalizedPath = normalizePathForAPI(node.path);

    try {
        console.log('[EditorPage] Sending rename request to API...');
        const response = await apiClient.post('/files/rename', {
            path: normalizedPath,
            new_name: newName
        });

        console.log('[EditorPage] Rename response:', response.data);
        console.log('[EditorPage] File/folder renamed successfully');

        // Update current file path if it was renamed
        if (currentFile.value && currentFile.value.path === node.path) {
            const parentPath = node.path.substring(0, node.path.lastIndexOf('/'));
            const newFileName = newName.endsWith('.md') ? newName : `${newName}.md`;
            currentFile.value.path = `${parentPath}/${newFileName}`;
            currentFileName.value = newFileName;
            console.log('[EditorPage] Updated current file path');
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
    console.log('[EditorPage] handleFolderCreate called');
    console.log('[EditorPage] Parent folder:', parentFolder);
    console.log('[EditorPage] Folder name:', folderName);

    const normalizedPath = normalizePathForAPI(parentFolder.path);

    try {
        console.log('[EditorPage] Sending create folder request to API...');
        const response = await apiClient.post('/folders/create', {
            path: normalizedPath,
            name: folderName
        });

        console.log('[EditorPage] Create folder response:', response.data);
        console.log('[EditorPage] Folder created successfully');

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
    console.log('[EditorPage] handleFolderDelete called');
    console.log('[EditorPage] Folder:', folder);

    const normalizedPath = normalizePathForAPI(folder.path);

    try {
        console.log('[EditorPage] Sending delete folder request to API...');
        await apiClient.delete('/folders/delete', {
            params: { path: normalizedPath }
        });

        console.log('[EditorPage] Folder deleted successfully');

        // If current file was in deleted folder, clear editor
        if (currentFile.value && currentFile.value.path.startsWith(folder.path)) {
            currentFile.value = null;
            currentFileName.value = null;
            content.value = '';
            currentFileVersion.value = null;
            saveStatus.value = 'saved';
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
    console.log('[EditorPage] handleExternalFileDrop called');
    console.log('[EditorPage] Files:', files.length);
    console.log('[EditorPage] Target folder:', targetFolder);

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
        console.log('[EditorPage] Upload cancelled by user');
        return;
    }

    const normalizedPath = normalizePathForAPI(targetFolder.path);
    let successCount = 0;
    let failCount = 0;
    const errors = [];

    // 显示上传进度
    console.log('[EditorPage] Starting upload...');

    for (const file of files) {
        try {
            console.log(`[EditorPage] Uploading: ${file.name}`);

            const formData = new FormData();
            formData.append('file', file);
            formData.append('path', normalizedPath);

            await apiClient.post('/files/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            successCount++;
            console.log(`[EditorPage] ✓ Uploaded: ${file.name}`);
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
        console.log('[EditorPage] Reloading file tree...');
        await loadFileTree();
    }
};

// Handle editor scroll
const handleEditorScroll = (scrollPercentage) => {
    if (isScrollingFromPreview.value) return; // 如果是预览触发的滚动，忽略
    editorScrollTop.value = scrollPercentage;
};

// Handle preview scroll
const handlePreviewScroll = (scrollPercentage) => {
    isScrollingFromPreview.value = true;
    previewScrollTop.value = scrollPercentage;

    // 重置标记
    setTimeout(() => {
        isScrollingFromPreview.value = false;
    }, 100);
};

// Handle format insertion
const handleInsertFormat = (format) => {
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

// Before unload handler - warn about unsaved changes
const handleBeforeUnload = (e) => {
    if (saveStatus.value === 'unsaved') {
        e.preventDefault();
        e.returnValue = '您有未保存的更改,确定要离开吗?';
        return e.returnValue;
    }
};

// 监听内容变化，当 metadata 更新时刷新预览
watch(() => currentMetadata.value, (newMetadata, oldMetadata) => {
    // 只有当 metadata 真正发生变化时才刷新
    if (newMetadata && oldMetadata && JSON.stringify(newMetadata) !== JSON.stringify(oldMetadata)) {
        console.log('[EditorPage] Metadata changed, refreshing preview');
        refreshPostPreview();
    }
}, { deep: true });

// Lifecycle hooks
onMounted(async () => {
    // Add beforeunload listener
    window.addEventListener('beforeunload', handleBeforeUnload);

    // Suppress axios cancellation errors in console
    window.addEventListener('unhandledrejection', (event) => {
        if (event.reason && event.reason.name === 'CanceledError') {
            event.preventDefault(); // Prevent console error
        }
    });

    // Log configuration
    console.log('Editor initialized');
    console.log('API Base:', API_BASE);
    console.log('Auth Token:', authToken ? 'Present' : 'Missing');

    // Load file tree
    await loadFileTree();
});

onBeforeUnmount(() => {
    // Clean up
    window.removeEventListener('beforeunload', handleBeforeUnload);
    if (autoSaveTimer) {
        clearTimeout(autoSaveTimer);
    }

    // Cancel all pending requests
    console.log('[EditorPage] Cancelling all pending requests');
    pendingRequests.forEach(source => {
        try {
            source.cancel('Component unmounting');
        } catch (e) {
            // Ignore errors
        }
    });
    pendingRequests.clear();
});
</script>

<style scoped>
.editor-container {
    display: flex;
    height: 100vh;
    width: 100vw;
    background-color: var(--theme-body-bg);
    color: var(--theme-body-text);
    overflow: hidden;
    transition: var(--theme-transition-colors);
}

/* Main Editor */
.main-editor {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Mobile View Toggle */
.mobile-view-toggle {
    display: none;
    gap: 8px;
    padding: 8px 16px;
    background: var(--theme-surface-default);
    border-bottom: 1px solid var(--theme-panel-border);
    transition: var(--theme-transition-colors);
}

.view-toggle-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 10px 16px;
    border: 1px solid var(--theme-border-light);
    background: var(--theme-panel-bg);
    color: var(--theme-panel-text);
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
}

.view-toggle-btn svg {
    width: 18px;
    height: 18px;
}

.view-toggle-btn:hover {
    background: var(--theme-surface-hover);
    border-color: var(--theme-primary);
}

.view-toggle-btn.active {
    background: var(--theme-gradient);
    color: white;
    border-color: transparent;
}

/* Editor Panels */
.editor-panels {
    flex: 1;
    display: flex;
    overflow: hidden;
}

.edit-panel,
.preview-panel {
    flex: 1;
    overflow: hidden;
}

.edit-panel {
    border-right: 1px solid var(--theme-panel-border);
    transition: var(--theme-transition-colors);
}

.preview-panel {
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    background: var(--theme-panel-bg);
    transition: var(--theme-transition-colors);
}

/* Post预览区域 */
.post-preview-section,
.graph-preview-section {
    padding: 0;
    background: var(--theme-surface-default);
    border-bottom: 2px solid var(--theme-panel-border);
    flex-shrink: 0;
    transition: var(--theme-transition-colors);
}

/* 预览区域头部 */
.preview-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    background: linear-gradient(135deg,
            var(--theme-panel-bg) 0%,
            var(--theme-surface-default) 100%);
    border-bottom: 1px solid var(--theme-panel-border);
    transition: var(--theme-transition-colors);
    position: relative;
}

/* 头部装饰线 */
.preview-header::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 1.5rem;
    right: 1.5rem;
    height: 2px;
    background: linear-gradient(90deg,
            transparent 0%,
            var(--theme-primary) 20%,
            var(--theme-secondary, #667eea) 80%,
            transparent 100%);
    opacity: 0.6;
}

/* 折叠按钮 - 更显眼的设计 */
.collapse-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border: 2px solid var(--theme-primary);
    background: linear-gradient(135deg,
            var(--theme-primary) 0%,
            var(--theme-secondary, #667eea) 100%);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    color: white;
    box-shadow:
        0 4px 12px rgba(99, 102, 241, 0.25),
        0 2px 4px rgba(0, 0, 0, 0.1);
    position: relative;
    overflow: hidden;
}

/* 按钮光晕效果 */
.collapse-btn::before {
    content: '';
    position: absolute;
    inset: -2px;
    background: linear-gradient(135deg,
            var(--theme-primary),
            var(--theme-secondary, #667eea));
    border-radius: 14px;
    opacity: 0;
    filter: blur(8px);
    transition: opacity 0.3s ease;
    z-index: -1;
}

.collapse-btn:hover {
    transform: scale(1.1) translateY(-2px);
    box-shadow:
        0 8px 24px rgba(99, 102, 241, 0.4),
        0 4px 8px rgba(0, 0, 0, 0.15);
    border-color: transparent;
}

.collapse-btn:hover::before {
    opacity: 0.6;
}

.collapse-btn:active {
    transform: scale(0.95) translateY(0);
}

.collapse-btn svg {
    width: 20px;
    height: 20px;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.collapse-btn.collapsed {
    background: var(--theme-surface-hover);
    color: var(--theme-content-text);
    border-color: var(--theme-border-light);
    box-shadow:
        0 2px 8px rgba(0, 0, 0, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.collapse-btn.collapsed::before {
    opacity: 0;
}

.collapse-btn.collapsed:hover {
    background: linear-gradient(135deg,
            var(--theme-primary) 0%,
            var(--theme-secondary, #667eea) 100%);
    color: white;
    border-color: var(--theme-primary);
}

.collapse-btn.collapsed svg {
    transform: rotate(-90deg);
}

/* 脉冲动画 - 吸引注意力 */
@keyframes buttonPulse {

    0%,
    100% {
        box-shadow:
            0 4px 12px rgba(99, 102, 241, 0.25),
            0 2px 4px rgba(0, 0, 0, 0.1);
    }

    50% {
        box-shadow:
            0 6px 20px rgba(99, 102, 241, 0.4),
            0 4px 8px rgba(0, 0, 0, 0.15);
    }
}

.collapse-btn:not(.collapsed) {
    animation: buttonPulse 2s ease-in-out infinite;
}

/* 预览内容区域 */
.post-preview-content,
.graph-preview-content {
    padding: 1.5rem;
    transition: all 0.3s ease;
}

/* Graph 预览包装器 - 固定尺寸以适配预览 */
.graph-preview-wrapper {
    position: relative;
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
}

.graph-preview-wrapper .graph-card {
    position: relative !important;
    width: 100% !important;
    height: auto !important;
    aspect-ratio: var(--card-aspect-ratio, 1);
}

.preview-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--theme-primary);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    transition: var(--theme-transition-colors);
    position: relative;
    padding-left: 1rem;
}

/* 标签前的装饰图标 */
.preview-label::before {
    content: '●';
    position: absolute;
    left: 0;
    color: var(--theme-primary);
    animation: labelPulse 2s ease-in-out infinite;
}

@keyframes labelPulse {

    0%,
    100% {
        opacity: 0.6;
        transform: scale(1);
    }

    50% {
        opacity: 1;
        transform: scale(1.2);
    }
}

/* Markdown预览区域 */
.markdown-preview-section {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem 0;
}

/* Responsive */
@media (max-width: 1024px) {
    .editor-panels {
        flex-direction: column;
    }

    .edit-panel {
        border-right: none;
        border-bottom: 1px solid var(--theme-panel-border);
    }
}

/* Mobile Optimizations */
@media (max-width: 768px) {

    /* Show mobile view toggle */
    .mobile-view-toggle {
        display: flex;
    }

    /* Single view mode on mobile */
    .editor-panels {
        flex-direction: row;
    }

    .edit-panel,
    .preview-panel {
        flex: 0 0 100%;
        border: none;
        transition: transform 0.3s ease, opacity 0.3s ease;
    }

    /* Hide inactive view */
    .mobile-hidden {
        display: none;
    }

    /* Optimize preview sections for mobile */
    .post-preview-section,
    .graph-preview-section {
        padding: 0;
    }

    .preview-header {
        padding: 0.75rem 1rem;
    }

    .preview-header::after {
        left: 1rem;
        right: 1rem;
    }

    .post-preview-content,
    .graph-preview-content {
        padding: 1rem;
    }

    .collapse-btn {
        width: 32px;
        height: 32px;
        border-radius: 10px;
    }

    .collapse-btn svg {
        width: 18px;
        height: 18px;
    }

    .graph-preview-wrapper {
        max-width: 100%;
    }

    .markdown-preview-section {
        padding: 1rem;
    }

    .preview-label {
        font-size: 0.7rem;
    }

    /* Adjust editor container for mobile */
    .editor-container {
        height: 100dvh;
        /* Use dynamic viewport height for mobile browsers */
    }

    /* Make file tree overlay on mobile */
    .editor-container :deep(.file-tree-sidebar) {
        position: fixed;
        z-index: 1000;
        height: 100dvh;
    }

    /* Optimize toolbar for mobile */
    .main-editor :deep(.ethereal-toolbar) {
        position: sticky;
        top: 0;
        z-index: 100;
    }
}

/* Extra small devices */
@media (max-width: 480px) {
    .mobile-view-toggle {
        padding: 6px 12px;
    }

    .view-toggle-btn {
        padding: 8px 12px;
        font-size: 13px;
    }

    .view-toggle-btn svg {
        width: 16px;
        height: 16px;
    }

    .view-toggle-btn span {
        display: none;
    }

    /* Show only icons on very small screens */
    .view-toggle-btn {
        min-width: 44px;
        /* Touch target size */
    }
}

/* Landscape mobile optimization */
@media (max-width: 768px) and (orientation: landscape) {
    .mobile-view-toggle {
        padding: 4px 12px;
    }

    .view-toggle-btn {
        padding: 6px 12px;
    }
}

/* Touch device optimizations */
@media (hover: none) and (pointer: coarse) {

    /* Increase touch targets */
    .view-toggle-btn {
        min-height: 44px;
    }

    /* Improve scrolling performance */
    .preview-panel {
        -webkit-overflow-scrolling: touch;
    }

    /* Prevent text selection during touch interactions */
    .mobile-view-toggle {
        -webkit-user-select: none;
        user-select: none;
        -webkit-tap-highlight-color: transparent;
    }
}
</style>
