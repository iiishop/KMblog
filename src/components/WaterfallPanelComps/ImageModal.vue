<template>
    <teleport to="body">
        <div v-if="isOpen" class="image-modal" @click.self="handleClose" @keydown.esc="handleClose" tabindex="0"
            ref="modalRef">
            <!-- 背景模糊层 -->
            <div class="modal-backdrop"></div>

            <!-- 主内容区 -->
            <div class="modal-content" :class="{ 'no-description': !hasDescription, 'fullscreen-mode': isFullscreen }">
                <!-- 左侧：图片 -->
                <div class="modal-image-section">
                    <div class="image-container" @wheel="handleWheel">
                        <img :src="image.src" :alt="image.alt" class="modal-image" :style="imageTransform"
                            @mousedown="handleImageMouseDown" @mousemove="handleImageMouseMove"
                            @mouseup="handleImageMouseUp" @mouseleave="handleImageMouseUp"
                            @dblclick="handleImageDoubleClick" />

                        <!-- 图片信息浮层 -->
                        <div class="image-info-float">
                            <span class="image-dimensions">{{ imageDimensions }}</span>
                            <span class="image-format">{{ imageFormat }}</span>
                            <span class="image-zoom">{{ Math.round(scale * 100) }}%</span>
                        </div>
                    </div>

                    <!-- 工具栏 -->
                    <div class="image-toolbar">
                        <!-- 缩放控制 -->
                        <div class="toolbar-group">
                            <button class="toolbar-btn" @click="zoomOut" title="缩小 (-)">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="11" cy="11" r="8" />
                                    <path d="M8 11h6" />
                                    <path d="M21 21l-4.35-4.35" />
                                </svg>
                            </button>
                            <button class="toolbar-btn" @click="resetZoom" title="重置 (0)">
                                <span class="zoom-text">{{ Math.round(scale * 100) }}%</span>
                            </button>
                            <button class="toolbar-btn" @click="zoomIn" title="放大 (+)">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="11" cy="11" r="8" />
                                    <path d="M11 8v6M8 11h6" />
                                    <path d="M21 21l-4.35-4.35" />
                                </svg>
                            </button>
                        </div>

                        <!-- 旋转控制 -->
                        <div class="toolbar-group">
                            <button class="toolbar-btn" @click="rotateLeft" title="逆时针旋转">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                                    <path d="M3 3v5h5" />
                                </svg>
                            </button>
                            <button class="toolbar-btn" @click="rotateRight" title="顺时针旋转">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8" />
                                    <path d="M21 3v5h-5" />
                                </svg>
                            </button>
                        </div>

                        <!-- 功能按钮 -->
                        <div class="toolbar-group">
                            <button class="toolbar-btn" @click="downloadImage" title="下载图片 (D)">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                                    <polyline points="7 10 12 15 17 10" />
                                    <line x1="12" y1="15" x2="12" y2="3" />
                                </svg>
                            </button>
                            <button class="toolbar-btn" @click="copyImageLink" title="复制链接">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                                </svg>
                            </button>
                            <button class="toolbar-btn" @click="toggleImageInfo" title="图片信息 (I)"
                                :class="{ 'active': showImageInfo }">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="10" />
                                    <line x1="12" y1="16" x2="12" y2="12" />
                                    <line x1="12" y1="8" x2="12.01" y2="8" />
                                </svg>
                            </button>
                            <button class="toolbar-btn" @click="toggleFullscreen" title="图片全屏 (F)"
                                :class="{ 'active': isFullscreen }">
                                <svg v-if="!isFullscreen" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <path
                                        d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
                                </svg>
                                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path
                                        d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- 图片信息面板 -->
                    <transition name="info-panel-fade">
                        <div v-if="showImageInfo" class="image-info-panel">
                            <h3>图片信息</h3>
                            <div class="info-item">
                                <span class="info-label">标题:</span>
                                <span class="info-value">{{ image.title || '无' }}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">编辑日期:</span>
                                <span class="info-value">{{ image.date || '无' }}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">尺寸:</span>
                                <span class="info-value">{{ imageDimensions || '未知' }}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">格式:</span>
                                <span class="info-value">{{ imageFormat }}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">缩放:</span>
                                <span class="info-value">{{ Math.round(scale * 100) }}%</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">旋转:</span>
                                <span class="info-value">{{ rotation }}°</span>
                            </div>
                        </div>
                    </transition>

                    <!-- 导航按钮 -->
                    <button v-if="canGoPrev" class="nav-btn nav-prev" @click="goToPrev" title="上一张 (←)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="15 18 9 12 15 6" />
                        </svg>
                    </button>
                    <button v-if="canGoNext" class="nav-btn nav-next" @click="goToNext" title="下一张 (→)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="9 18 15 12 9 6" />
                        </svg>
                    </button>

                    <!-- 关闭按钮 -->
                    <button class="close-btn" @click="handleClose" aria-label="Close modal">
                        <svg viewBox="0 0 24 24">
                            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2"
                                stroke-linecap="round" />
                        </svg>
                    </button>
                </div>

                <!-- 右侧：描述（只在有描述且非全屏模式时显示） -->
                <div v-if="hasDescription && !isFullscreen" class="modal-description-section">
                    <div class="description-header">
                        <h2 class="description-title">图片描述</h2>
                    </div>
                    <div class="description-content" ref="contentRef">
                        <!-- Markdown 渲染 - 使用完整的渲染系统 -->
                        <div v-html="renderedDescription" class="markdown-body"></div>
                    </div>

                    <!-- 评论区 - 小红书风格 -->
                    <div v-if="showComments" class="image-comments-section">
                        <div class="comments-divider">
                            <span class="divider-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                                </svg>
                            </span>
                            <span class="divider-text">评论与互动</span>
                            <span class="divider-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path
                                        d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z">
                                    </path>
                                </svg>
                            </span>
                        </div>
                        <GiscusComments component-type="image" :term="commentTerm" :compact="true"
                            :emphasize-reactions="true" />
                    </div>
                </div>
            </div>
        </div>
    </teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, defineAsyncComponent } from 'vue';

// 使用完整的 Markdown 渲染系统
import md from '@/components/MarkdownPanelComps/MarkdownRenender.js';
import '@/components/MarkdownPanelComps/MarkdownStyle.css';
import { renderDynamicComponents } from '@/components/MarkdownPanelComps/DynamicComponentRenderer.js';
import mermaid from 'mermaid';
import config from '@/config';
import GiscusComments from '@/components/GiscusComments.vue';

// 导入所有嵌入式组件
const SteamGameBlock = defineAsyncComponent(() =>
    import('@/components/MarkdownPanelComps/SteamGameBlock.vue')
);
const BangumiBlock = defineAsyncComponent(() =>
    import('@/components/MarkdownPanelComps/BangumiBlock.vue')
);
const BilibiliVideoBlock = defineAsyncComponent(() =>
    import('@/components/MarkdownPanelComps/BilibiliVideoBlock.vue')
);
const GithubRepoBlock = defineAsyncComponent(() =>
    import('@/components/MarkdownPanelComps/GithubRepoBlock.vue')
);
const XiaohongshuNoteBlock = defineAsyncComponent(() =>
    import('@/components/MarkdownPanelComps/XiaohongshuNoteBlock.vue')
);

const props = defineProps({
    image: {
        type: Object,
        required: true
    },
    description: {
        type: String,
        default: ''
    },
    triggerCardRect: {
        type: Object,
        default: null
    },
    images: {
        type: Array,
        default: () => []
    },
    currentIndex: {
        type: Number,
        default: 0
    }
});

const emit = defineEmits(['close', 'next', 'prev']);

// Refs
const modalRef = ref(null);
const contentRef = ref(null);

// 状态
const isOpen = ref(false);
const mdDescription = ref('');
const scale = ref(1); // 缩放比例
const rotation = ref(0); // 旋转角度
const translateX = ref(0); // X轴偏移
const translateY = ref(0); // Y轴偏移
const isDragging = ref(false); // 是否正在拖拽
const dragStartX = ref(0);
const dragStartY = ref(0);
const isFullscreen = ref(false); // 是否图片全屏（隐藏描述区域）
const showImageInfo = ref(false); // 是否显示图片信息面板

// 评论相关
const showComments = computed(() => {
    return config.Giscus?.enabled && config.Giscus?.imageModal?.enabled;
});

const commentTerm = computed(() => {
    // Use image path or title as unique identifier
    return props.image.src || props.image.title || 'image-' + props.currentIndex;
});

// 计算属性
const imageDimensions = computed(() => {
    if (props.image.width && props.image.height) {
        return `${props.image.width} × ${props.image.height}`;
    }
    return '';
});

const imageFormat = computed(() => {
    if (props.image.src) {
        const ext = props.image.src.split('.').pop().toUpperCase();
        return ext;
    }
    return '';
});

// 图片变换样式
const imageTransform = computed(() => {
    return {
        transform: `scale(${scale.value}) rotate(${rotation.value}deg) translate(${translateX.value}px, ${translateY.value}px)`,
        cursor: scale.value > 1 ? (isDragging.value ? 'grabbing' : 'grab') : 'default',
        transition: isDragging.value ? 'none' : 'transform 0.3s ease'
    };
});

// 是否可以切换到上一张
const canGoPrev = computed(() => {
    return props.images && props.images.length > 1 && props.currentIndex > 0;
});

// 是否可以切换到下一张
const canGoNext = computed(() => {
    return props.images && props.images.length > 1 && props.currentIndex < props.images.length - 1;
});

const renderedDescription = computed(() => {
    const desc = mdDescription.value || props.description;
    if (!desc) return '';

    // 最后一道防线：检查是否是 HTML 页面
    const trimmed = desc.trim().toLowerCase();
    if (trimmed.startsWith('<!doctype') ||
        trimmed.startsWith('<html') ||
        trimmed.includes('<!doctype html>')) {
        console.warn('[ImageModal] Blocked HTML content from rendering');
        return '';
    }

    // 移除 front-matter metadata（YAML 格式）
    let content = desc;
    if (content.startsWith('---')) {
        const endIndex = content.indexOf('---', 3);
        if (endIndex !== -1) {
            // 跳过 metadata 部分
            content = content.substring(endIndex + 3).trim();
        }
    }

    // 使用完整的 markdown-it 渲染器（支持代码高亮、LaTeX、Mermaid等）
    return md.render(content);
});

// 检查是否有描述内容
const hasDescription = computed(() => {
    const desc = mdDescription.value || props.description;
    if (!desc) return false;

    // 检查是否是 HTML 错误页面
    const trimmed = desc.trim().toLowerCase();
    if (trimmed.startsWith('<!doctype') ||
        trimmed.startsWith('<html') ||
        trimmed.includes('<!doctype html>')) {
        return false;
    }

    return true;
});

// 加载关联的 .md 文件
async function loadMarkdownDescription() {
    if (!props.image.mdPath) {
        mdDescription.value = '';
        return;
    }

    try {
        const response = await fetch(props.image.mdPath);

        // 只处理成功的响应
        if (!response.ok) {
            console.log('[ImageModal] .md file not found (status:', response.status, ')');
            mdDescription.value = '';
            return;
        }

        // 检查 Content-Type
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('text/html')) {
            console.log('[ImageModal] .md file not found (got HTML content-type)');
            mdDescription.value = '';
            return;
        }

        const text = await response.text();

        // 检查内容是否为空或只有空白字符
        if (!text || !text.trim()) {
            console.log('[ImageModal] .md file is empty');
            mdDescription.value = '';
            return;
        }

        const trimmed = text.trim().toLowerCase();

        // 检查是否是 HTML 页面
        if (trimmed.startsWith('<!doctype') ||
            trimmed.startsWith('<html') ||
            trimmed.includes('<!doctype html>') ||
            trimmed.includes('<html>')) {
            console.log('[ImageModal] .md file not found (got HTML page)');
            mdDescription.value = '';
            return;
        }

        // 只有确认不是 HTML 才设置内容
        mdDescription.value = text;
        console.log('[ImageModal] Successfully loaded .md file');

    } catch (error) {
        console.log('[ImageModal] Failed to load markdown description:', error);
        mdDescription.value = '';
    }
}

// 事件处理
function handleClose() {
    isOpen.value = false;
    resetImageState();
    emit('close');
}

// 重置图片状态
function resetImageState() {
    scale.value = 1;
    rotation.value = 0;
    translateX.value = 0;
    translateY.value = 0;
    isDragging.value = false;
    // 注意：不重置 isFullscreen，让用户的全屏偏好保持
}

// 缩放功能
function zoomIn() {
    scale.value = Math.min(scale.value + 0.25, 5);
}

function zoomOut() {
    scale.value = Math.max(scale.value - 0.25, 0.5);
}

function resetZoom() {
    scale.value = 1;
    translateX.value = 0;
    translateY.value = 0;
}

// 旋转功能
function rotateLeft() {
    rotation.value -= 90;
}

function rotateRight() {
    rotation.value += 90;
}

// 下载图片
async function downloadImage() {
    try {
        const response = await fetch(props.image.src);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = props.image.title || 'image';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('[ImageModal] Failed to download image:', error);
        alert('下载失败，请稍后重试');
    }
}

// 复制图片链接
async function copyImageLink() {
    try {
        const fullUrl = window.location.origin + props.image.src;
        await navigator.clipboard.writeText(fullUrl);
        alert('✓ 图片链接已复制到剪贴板');
    } catch (error) {
        console.error('[ImageModal] Failed to copy link:', error);
        alert('复制失败，请手动复制');
    }
}

// 全屏切换（图片全屏，隐藏描述区域）
function toggleFullscreen() {
    isFullscreen.value = !isFullscreen.value;
}

// 切换图片信息面板
function toggleImageInfo() {
    showImageInfo.value = !showImageInfo.value;
}

// 图片拖拽
function handleImageMouseDown(e) {
    if (scale.value <= 1) return;

    isDragging.value = true;
    dragStartX.value = e.clientX - translateX.value;
    dragStartY.value = e.clientY - translateY.value;
    e.preventDefault();
}

function handleImageMouseMove(e) {
    if (!isDragging.value) return;

    translateX.value = e.clientX - dragStartX.value;
    translateY.value = e.clientY - dragStartY.value;
}

function handleImageMouseUp() {
    isDragging.value = false;
}

// 双击重置/放大
function handleImageDoubleClick() {
    if (scale.value === 1) {
        scale.value = 2;
    } else {
        resetZoom();
    }
}

// 滚轮缩放
function handleWheel(e) {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    scale.value = Math.max(0.5, Math.min(5, scale.value + delta));
}

// 切换到上一张
function goToPrev() {
    if (canGoPrev.value) {
        resetImageState();
        emit('prev');
    }
}

// 切换到下一张
function goToNext() {
    if (canGoNext.value) {
        resetImageState();
        emit('next');
    }
}

// 键盘事件处理
function handleKeydown(e) {
    if (!isOpen.value) return;

    switch (e.key) {
        case 'Escape':
            handleClose();
            break;
        case 'ArrowLeft':
            goToPrev();
            break;
        case 'ArrowRight':
            goToNext();
            break;
        case '+':
        case '=':
            zoomIn();
            break;
        case '-':
        case '_':
            zoomOut();
            break;
        case '0':
            resetZoom();
            break;
        case 'f':
        case 'F':
            toggleFullscreen();
            break;
        case 'i':
        case 'I':
            toggleImageInfo();
            break;
        case 'd':
        case 'D':
            downloadImage();
            break;
    }
}

// 监听图片变化
watch(() => props.image, (newVal) => {
    if (newVal) {
        isOpen.value = true;
        resetImageState();
        loadMarkdownDescription();
    }
}, { immediate: true });

// 监听 isOpen 变化
watch(isOpen, (newVal) => {
    if (newVal) {
        // 聚焦模态框以支持键盘事件
        nextTick(() => {
            if (modalRef.value) {
                modalRef.value.focus();
            }
        });
    }
});

// 监听描述内容变化，渲染动态组件和 Mermaid
watch(renderedDescription, async () => {
    await nextTick();
    const container = contentRef.value;
    if (container) {
        // 渲染动态组件（Bilibili, Steam, Bangumi, GitHub, Xiaohongshu）
        renderDynamicComponents(container, {
            'bilibilivideoblock': BilibiliVideoBlock,
            'steamgameblock': SteamGameBlock,
            'bangumiblock': BangumiBlock,
            'githubrepoblock': GithubRepoBlock,
            'xiaohongshunoteblock': XiaohongshuNoteBlock
        });

        // 渲染 Mermaid 图表
        await nextTick();
        if (typeof mermaid !== 'undefined') {
            try {
                await mermaid.run({
                    nodes: container.querySelectorAll('.mermaid'),
                });

                // 修复 SVG 尺寸
                await nextTick();
                const mermaidSvgs = container.querySelectorAll('.mermaid svg');
                mermaidSvgs.forEach(svg => {
                    svg.removeAttribute('width');
                    svg.removeAttribute('height');
                    svg.style.width = '100%';
                    svg.style.height = '400px';
                    svg.style.maxWidth = '100%';
                    svg.style.maxHeight = '400px';
                    svg.style.display = 'block';
                    svg.style.margin = '0 auto';
                });
            } catch (error) {
                console.warn('[ImageModal] Mermaid rendering failed:', error);
            }
        }
    }
});

onMounted(() => {
    document.addEventListener('keydown', handleKeydown);
    loadMarkdownDescription();
});

onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.image-modal {
    position: fixed;
    inset: 0;
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    isolation: isolate;
}

/* 背景模糊层 */
.modal-backdrop {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.75);
    backdrop-filter: blur(12px);
}

/* 主内容区 */
.modal-content {
    position: relative;
    width: 90%;
    height: 85%;
    display: flex;
    z-index: 2;
    max-width: 1400px;
    margin: 0 auto;
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.15),
        0 0 0 1px rgba(0, 0, 0, 0.05);
    animation: modalEnter 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalEnter {
    from {
        opacity: 0;
        transform: scale(0.9) translateY(20px);
    }

    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}

/* 图片区域 */
.modal-image-section {
    flex: 0 0 60%;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a1a1a 0%, #000 100%);
    padding: 0;
    transition: flex 0.3s ease;
}

/* 无描述时，图片区域占满 */
.modal-content.no-description .modal-image-section,
.modal-content.fullscreen-mode .modal-image-section {
    flex: 1;
}

/* 全屏模式时隐藏描述区域 */
.modal-content.fullscreen-mode .modal-description-section {
    display: none;
}

.image-container {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3rem;
}

.modal-image {
    display: block;
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
    object-fit: contain;
    border-radius: 12px;
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.5),
        0 0 0 1px rgba(255, 255, 255, 0.1);
    user-select: none;
}

/* 图片信息浮层 */
.image-info-float {
    position: absolute;
    bottom: 1.5rem;
    left: 1.5rem;
    display: flex;
    gap: 1rem;
    padding: 0.5rem 1rem;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.9);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    z-index: 5;
}

.image-zoom {
    color: #4ade80;
    font-weight: 600;
}

/* 工具栏 */
.image-toolbar {
    position: absolute;
    bottom: 1.5rem;
    right: 1.5rem;
    display: flex;
    gap: 0.75rem;
    z-index: 5;
}

.toolbar-group {
    display: flex;
    gap: 0.25rem;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    padding: 0.25rem;
}

.toolbar-btn {
    width: 36px;
    height: 36px;
    border: none;
    background: transparent;
    color: rgba(255, 255, 255, 0.9);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    transition: all 0.2s;
}

.toolbar-btn:hover {
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
}

.toolbar-btn.active {
    background: rgba(99, 102, 241, 0.3);
    color: #818cf8;
}

.toolbar-btn svg {
    width: 18px;
    height: 18px;
}

.zoom-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
}

/* 图片信息面板 */
.image-info-panel {
    position: absolute;
    top: 5rem;
    right: 1.5rem;
    width: 250px;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(20px);
    border-radius: 12px;
    padding: 1.25rem;
    z-index: 5;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.image-info-panel h3 {
    margin: 0 0 1rem 0;
    font-size: 0.9rem;
    font-weight: 600;
    color: #fff;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.info-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 0.8rem;
}

.info-item:last-child {
    border-bottom: none;
}

.info-label {
    color: rgba(255, 255, 255, 0.6);
    font-weight: 500;
}

.info-value {
    color: rgba(255, 255, 255, 0.9);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
}

.info-panel-fade-enter-active,
.info-panel-fade-leave-active {
    transition: all 0.3s;
}

.info-panel-fade-enter-from,
.info-panel-fade-leave-to {
    opacity: 0;
    transform: translateX(20px);
}

/* 导航按钮 */
.nav-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 50px;
    height: 50px;
    border: none;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(10px);
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
    z-index: 5;
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.nav-btn:hover {
    background: rgba(0, 0, 0, 0.7);
    transform: translateY(-50%) scale(1.1);
}

.nav-btn svg {
    width: 24px;
    height: 24px;
}

.nav-prev {
    left: 1.5rem;
}

.nav-next {
    right: 1.5rem;
}

/* 关闭按钮 */
.close-btn {
    position: absolute;
    top: 1.5rem;
    right: 1.5rem;
    width: 44px;
    height: 44px;
    border: none;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px);
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 10;
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.close-btn:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: scale(1.1) rotate(90deg);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.close-btn:active {
    transform: scale(0.95) rotate(90deg);
}

.close-btn svg {
    width: 22px;
    height: 22px;
}

/* 描述区域 - 小红书风格 */
.modal-description-section {
    flex: 0 0 40%;
    background: #fafafa;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    border-left: 1px solid #e8e8e8;
}

.description-header {
    padding: 2rem 2.5rem 1rem;
    background: linear-gradient(180deg, #fff 0%, #fafafa 100%);
    border-bottom: 1px solid #e8e8e8;
    flex-shrink: 0;
}

.description-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #222;
    letter-spacing: -0.02em;
}

.description-content {
    padding: 2rem 2.5rem;
    flex: 1;
}

/* === 图片评论区 - 小红书风格 === */
.image-comments-section {
    padding: 2rem 2.5rem 2.5rem;
    background: linear-gradient(180deg, #fff 0%, #fafafa 100%);
    border-top: 2px solid #ffebee;
}

.comments-divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
    position: relative;
}

.comments-divider::before,
.comments-divider::after {
    content: '';
    flex: 1;
    height: 2px;
    background: linear-gradient(to right, transparent, #ffcdd2, transparent);
}

.divider-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #ff2442 0%, #ff6b6b 100%);
    border-radius: 50%;
    color: #fff;
    box-shadow: 0 4px 12px rgba(255, 36, 66, 0.25);
}

.divider-icon svg {
    width: 18px;
    height: 18px;
}

.divider-text {
    padding: 0.5rem 1.5rem;
    font-size: 1rem;
    font-weight: 700;
    color: #d32f2f;
    white-space: nowrap;
    background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
    border: 2px solid #ffcdd2;
    border-radius: 20px;
    letter-spacing: 0.05em;
}

/* === Giscus 小红书风格定制 === */
.image-comments-section :deep(.gsc-main) {
    background: transparent !important;
    border: none !important;
}

.image-comments-section :deep(.gsc-comment-box) {
    background: #fff !important;
    border: 2px solid #ffcdd2 !important;
    border-radius: 20px !important;
    padding: 1.25rem !important;
    margin-bottom: 1.5rem !important;
    box-shadow: 0 4px 16px rgba(255, 36, 66, 0.08) !important;
    transition: all 0.3s ease !important;
}

.image-comments-section :deep(.gsc-comment-box:hover) {
    border-color: #ff2442 !important;
    box-shadow: 0 8px 24px rgba(255, 36, 66, 0.15) !important;
    transform: translateY(-2px) !important;
}

.image-comments-section :deep(.gsc-comment-box-tabs) {
    border-bottom: 2px solid #ffe8e8 !important;
    margin-bottom: 1rem !important;
}

.image-comments-section :deep(.gsc-comment-box-tab) {
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.2rem !important;
    color: #999 !important;
    border-radius: 12px 12px 0 0 !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.02em !important;
}

.image-comments-section :deep(.gsc-comment-box-tab[aria-selected="true"]) {
    color: #ff2442 !important;
    background: linear-gradient(180deg, #fff5f5 0%, #fff 100%) !important;
    border-bottom: 3px solid #ff2442 !important;
}

.image-comments-section :deep(.gsc-comment-box-textarea) {
    background: #fafafa !important;
    border: 2px solid #f0f0f0 !important;
    border-radius: 16px !important;
    padding: 1rem 1.25rem !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
    color: #333 !important;
    transition: all 0.3s ease !important;
    font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', sans-serif !important;
}

.image-comments-section :deep(.gsc-comment-box-textarea:focus) {
    background: #fff !important;
    border-color: #ff2442 !important;
    box-shadow: 0 0 0 4px rgba(255, 36, 66, 0.1) !important;
    outline: none !important;
}

.image-comments-section :deep(.gsc-comment-box-textarea::placeholder) {
    color: #bbb !important;
}

.image-comments-section :deep(.gsc-comment-box-bottom) {
    margin-top: 1rem !important;
    padding-top: 1rem !important;
    border-top: 1px solid #f5f5f5 !important;
}

.image-comments-section :deep(.gsc-comment-box-buttons) {
    gap: 0.75rem !important;
}

.image-comments-section :deep(.gsc-comment-box-button) {
    padding: 0.7rem 1.5rem !important;
    border-radius: 20px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    transition: all 0.3s ease !important;
    border: 2px solid transparent !important;
    letter-spacing: 0.02em !important;
}

.image-comments-section :deep(.gsc-comment-box-button-primary) {
    background: linear-gradient(135deg, #ff2442 0%, #ff6b6b 100%) !important;
    color: #fff !important;
    box-shadow: 0 4px 16px rgba(255, 36, 66, 0.3) !important;
}

.image-comments-section :deep(.gsc-comment-box-button-primary:hover) {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 24px rgba(255, 36, 66, 0.4) !important;
}

.image-comments-section :deep(.gsc-comment-box-button-secondary) {
    background: #f5f5f5 !important;
    color: #666 !important;
    border: 2px solid #e8e8e8 !important;
}

.image-comments-section :deep(.gsc-comment-box-button-secondary:hover) {
    background: #fff !important;
    border-color: #ffcdd2 !important;
    color: #ff2442 !important;
}

.image-comments-section :deep(.gsc-comment) {
    background: #fff !important;
    border: 2px solid #f5f5f5 !important;
    border-radius: 18px !important;
    padding: 1.25rem !important;
    margin-bottom: 1.25rem !important;
    transition: all 0.3s ease !important;
}

.image-comments-section :deep(.gsc-comment:hover) {
    border-color: #ffebee !important;
    box-shadow: 0 4px 16px rgba(255, 36, 66, 0.08) !important;
    transform: translateY(-1px) !important;
}

.image-comments-section :deep(.gsc-comment-author) {
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    color: #222 !important;
}

.image-comments-section :deep(.gsc-comment-author-avatar) {
    border-radius: 50% !important;
    border: 2px solid #ffebee !important;
    box-shadow: 0 2px 8px rgba(255, 36, 66, 0.1) !important;
}

.image-comments-section :deep(.gsc-comment-metadata) {
    color: #999 !important;
    font-size: 0.8rem !important;
}

.image-comments-section :deep(.gsc-comment-content) {
    color: #333 !important;
    font-size: 0.9rem !important;
    line-height: 1.7 !important;
    margin-top: 0.75rem !important;
}

.image-comments-section :deep(.gsc-comment-content p) {
    margin: 0.5rem 0 !important;
}

.image-comments-section :deep(.gsc-comment-reactions) {
    margin-top: 1rem !important;
    padding-top: 1rem !important;
    border-top: 1px solid #f5f5f5 !important;
    display: flex !important;
    gap: 0.5rem !important;
    flex-wrap: wrap !important;
}

.image-comments-section :deep(.gsc-reaction-button) {
    border-radius: 20px !important;
    padding: 0.4rem 0.8rem !important;
    background: #fafafa !important;
    border: 2px solid #f0f0f0 !important;
    transition: all 0.3s ease !important;
    font-size: 0.85rem !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.3rem !important;
}

.image-comments-section :deep(.gsc-reaction-button:hover) {
    background: #fff5f5 !important;
    border-color: #ffcdd2 !important;
    transform: scale(1.05) !important;
}

.image-comments-section :deep(.gsc-reaction-button[aria-pressed="true"]) {
    background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%) !important;
    border-color: #ff2442 !important;
}

.image-comments-section :deep(.gsc-reactions-count) {
    font-weight: 700 !important;
    color: #ff2442 !important;
    font-size: 0.85rem !important;
}

.image-comments-section :deep(.gsc-reply-button) {
    color: #ff2442 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 0.8rem !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}

.image-comments-section :deep(.gsc-reply-button:hover) {
    background: #fff5f5 !important;
}

.image-comments-section :deep(.gsc-timeline-header) {
    font-weight: 700 !important;
    color: #222 !important;
    font-size: 1.1rem !important;
    margin-bottom: 1.5rem !important;
    padding-bottom: 1rem !important;
    border-bottom: 2px solid #ffe8e8 !important;
}

/* Markdown 样式 - 小红书风格 */
.markdown-body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    font-size: 0.95rem;
    line-height: 1.8;
    color: #333;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3 {
    font-weight: 600;
    color: #222;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
}

.markdown-body h1 {
    font-size: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
}

.markdown-body h2 {
    font-size: 1.3rem;
}

.markdown-body h3 {
    font-size: 1.1rem;
}

.markdown-body p {
    margin-bottom: 1rem;
    color: #333;
}

.markdown-body code {
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    background: #f5f5f5;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-size: 0.9em;
    color: #e83e8c;
}

.markdown-body pre {
    background: #f8f8f8;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 1rem 0;
    border: 1px solid #eee;
}

.markdown-body pre code {
    background: none;
    padding: 0;
    color: #333;
}

.markdown-body a {
    color: #ff2442;
    text-decoration: none;
}

.markdown-body a:hover {
    text-decoration: underline;
}

.markdown-body img {
    max-width: 100%;
    border-radius: 8px;
    margin: 1rem 0;
}

.markdown-body blockquote {
    border-left: 3px solid #ff2442;
    padding-left: 1rem;
    margin: 1rem 0;
    color: #666;
    font-style: italic;
}

/* 滚动条样式 - 小红书风格 */
.modal-description-section::-webkit-scrollbar {
    width: 6px;
}

.modal-description-section::-webkit-scrollbar-track {
    background: #f5f5f5;
}

.modal-description-section::-webkit-scrollbar-thumb {
    background: #ddd;
    border-radius: 3px;
}

.modal-description-section::-webkit-scrollbar-thumb:hover {
    background: #ccc;
}

/* ========================================
   嵌入式 Block 组件强制移动端样式
   ======================================== */

/* 强制所有 Block 组件使用移动端布局 */
.modal-description-section :deep(.bili-embed-neo),
.modal-description-section :deep(.steam-card),
.modal-description-section :deep(.xhs-embed-container),
.modal-description-section :deep(.bangumi-card) {
    margin: 1.5rem 0 !important;
}

/* Bilibili Block - 强制垂直布局 */
.modal-description-section :deep(.bili-card-glass) {
    flex-direction: column !important;
    padding: 0.75rem !important;
    gap: 0.75rem !important;
}

.modal-description-section :deep(.bili-card-glass .media-column) {
    flex: none !important;
    width: 100% !important;
    max-width: 100% !important;
}

.modal-description-section :deep(.bili-card-glass .data-column) {
    width: 100% !important;
}

.modal-description-section :deep(.bili-card-glass .video-title) {
    font-size: 14px !important;
    margin-bottom: 8px !important;
}

.modal-description-section :deep(.bili-card-glass .video-description-deck) {
    padding: 6px 10px !important;
    margin-bottom: 10px !important;
}

.modal-description-section :deep(.bili-card-glass .deck-content) {
    font-size: 12px !important;
    -webkit-line-clamp: 2 !important;
}

.modal-description-section :deep(.bili-card-glass .stats-matrix) {
    grid-template-columns: 1fr 1fr !important;
    gap: 6px 10px !important;
    margin-bottom: 12px !important;
}

.modal-description-section :deep(.bili-card-glass .stat-info) {
    font-size: 9px !important;
}

.modal-description-section :deep(.bili-card-glass .data-footer) {
    padding-top: 10px !important;
    gap: 10px !important;
}

.modal-description-section :deep(.bili-card-glass .cyclotron-avatar) {
    width: 36px !important;
    height: 36px !important;
}

.modal-description-section :deep(.bili-card-glass .author-id) {
    font-size: 12px !important;
}

.modal-description-section :deep(.bili-card-glass .creator-bio) {
    font-size: 9px !important;
    max-width: 100% !important;
}

.modal-description-section :deep(.bili-card-glass .feedback-sector) {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 8px !important;
}

/* Steam Block - 强制垂直布局 */
.modal-description-section :deep(.steam-card .card-content) {
    flex-direction: column !important;
    padding: 10px !important;
    gap: 12px !important;
}

.modal-description-section :deep(.steam-card .left-col) {
    width: 100% !important;
    max-width: 100% !important;
}

.modal-description-section :deep(.steam-card .right-col) {
    width: 100% !important;
}

.modal-description-section :deep(.steam-card .game-title) {
    font-size: 1.1rem !important;
}

.modal-description-section :deep(.steam-card .meta-row) {
    font-size: 0.75rem !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
}

.modal-description-section :deep(.steam-card .tags-row) {
    gap: 4px !important;
}

.modal-description-section :deep(.steam-card .tag) {
    font-size: 0.65rem !important;
    padding: 1px 5px !important;
}

.modal-description-section :deep(.steam-card .game-desc) {
    font-size: 0.75rem !important;
    -webkit-line-clamp: 2 !important;
}

.modal-description-section :deep(.steam-card .action-row) {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 10px !important;
    padding: 6px 10px !important;
}

.modal-description-section :deep(.steam-card .price-block) {
    justify-content: center !important;
}

.modal-description-section :deep(.steam-card .store-btn) {
    width: 100% !important;
    justify-content: center !important;
    padding: 8px 14px !important;
    font-size: 0.85rem !important;
}

/* Xiaohongshu Block - 强制垂直布局 */
.modal-description-section :deep(.xhs-card) {
    flex-direction: column !important;
    padding: 0.75rem !important;
    gap: 0.75rem !important;
}

.modal-description-section :deep(.xhs-card .media-area) {
    flex: none !important;
    width: 100% !important;
    max-width: 100% !important;
    box-shadow: 8px 8px 0 var(--theme-red-deep) !important;
}

.modal-description-section :deep(.xhs-card .content-area) {
    width: 100% !important;
}

.modal-description-section :deep(.xhs-card .xhs-header) {
    gap: 8px !important;
    margin-bottom: 1rem !important;
}

.modal-description-section :deep(.xhs-card .brand-tag) {
    font-size: 9px !important;
    letter-spacing: 2px !important;
    padding: 2px 6px !important;
}

.modal-description-section :deep(.xhs-card .note-title) {
    font-size: 1.3rem !important;
    margin-bottom: 1rem !important;
}

.modal-description-section :deep(.xhs-card .note-abstract) {
    font-size: 0.8rem !important;
    max-height: 80px !important;
    margin-bottom: 1.5rem !important;
}

.modal-description-section :deep(.xhs-card .chips-left) {
    gap: 8px !important;
}

.modal-description-section :deep(.xhs-card .tag-chip) {
    font-size: 8px !important;
    padding: 2px 8px !important;
}

.modal-description-section :deep(.xhs-card .meta-footer) {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 12px !important;
    margin-top: 1rem !important;
}

.modal-description-section :deep(.xhs-card .user-avatar) {
    width: 24px !important;
    height: 24px !important;
}

.modal-description-section :deep(.xhs-card .user-name) {
    font-size: 0.75rem !important;
}

.modal-description-section :deep(.xhs-card .stats-row) {
    width: 100% !important;
    justify-content: flex-start !important;
    gap: 15px !important;
}

.modal-description-section :deep(.xhs-card .stat-pill) {
    font-size: 9px !important;
    gap: 4px !important;
}

/* Bangumi Block - 强制垂直布局 */
.modal-description-section :deep(.bangumi-card .card-content) {
    flex-direction: column !important;
    padding: 0.75rem !important;
    gap: 0.75rem !important;
}

.modal-description-section :deep(.bangumi-card .cover-column) {
    width: 100% !important;
    max-width: 160px !important;
    margin: 0 auto !important;
    gap: 0.75rem !important;
}

.modal-description-section :deep(.bangumi-card .cover-wrapper) {
    border-radius: 10px !important;
}

.modal-description-section :deep(.bangumi-card .cover-img) {
    min-height: 120px !important;
    border-radius: 10px !important;
}

.modal-description-section :deep(.bangumi-card .action-btn) {
    padding: 6px 8px !important;
    font-size: 0.75rem !important;
    gap: 4px !important;
}

.modal-description-section :deep(.bangumi-card .btn-icon svg) {
    width: 12px !important;
    height: 12px !important;
}

.modal-description-section :deep(.bangumi-card .info-column) {
    width: 100% !important;
}

.modal-description-section :deep(.bangumi-card .header-section) {
    flex-direction: column !important;
    align-items: center !important;
    text-align: center !important;
    gap: 0.75rem !important;
}

.modal-description-section :deep(.bangumi-card .title) {
    font-size: 1.1rem !important;
}

.modal-description-section :deep(.bangumi-card .rating-badge) {
    text-align: center !important;
    width: 100% !important;
}

.modal-description-section :deep(.bangumi-card .score-box) {
    justify-content: center !important;
}

.modal-description-section :deep(.bangumi-card .score-val) {
    font-size: 1.5rem !important;
}

.modal-description-section :deep(.bangumi-card .score-suffix) {
    font-size: 0.8rem !important;
}

.modal-description-section :deep(.bangumi-card .score-count) {
    font-size: 0.65rem !important;
}

.modal-description-section :deep(.bangumi-card .distribution-bar) {
    height: 4px !important;
}

.modal-description-section :deep(.bangumi-card .tags-container) {
    justify-content: center !important;
    gap: 5px !important;
}

.modal-description-section :deep(.bangumi-card .tag-pill) {
    font-size: 0.65rem !important;
    padding: 2px 6px !important;
}

.modal-description-section :deep(.bangumi-card .summary-text) {
    font-size: 0.8rem !important;
    text-align: left !important;
}

.modal-description-section :deep(.bangumi-card .summary-text.collapsed) {
    -webkit-line-clamp: 2 !important;
    line-clamp: 2 !important;
}

.modal-description-section :deep(.bangumi-card .infobox-grid) {
    grid-template-columns: 1fr !important;
    gap: 6px !important;
    padding-top: 0.75rem !important;
    text-align: left !important;
}

.modal-description-section :deep(.bangumi-card .info-item) {
    font-size: 0.7rem !important;
}

.modal-description-section :deep(.bangumi-card .info-key) {
    font-size: 0.65rem !important;
}

/* GitHub Block - 如果存在的话 */
.modal-description-section :deep(.github-repo-card) {
    padding: 0.75rem !important;
}

.modal-description-section :deep(.github-repo-card .repo-title) {
    font-size: 1rem !important;
}

.modal-description-section :deep(.github-repo-card .repo-description) {
    font-size: 0.8rem !important;
}

/* 响应式 */
@media (max-width: 968px) {
    .modal-content {
        flex-direction: column;
        width: 100%;
        height: 100%;
        border-radius: 0;
    }

    .modal-image-section {
        flex: 1;
    }

    .modal-description-section {
        width: 100%;
        max-width: none;
        height: 40%;
        border-left: none;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* 移动端工具栏 - 更紧凑 */
    .image-toolbar {
        bottom: 1rem;
        right: 1rem;
        left: 1rem;
        flex-direction: row;
        justify-content: center;
        gap: 0.5rem;
    }

    .toolbar-group {
        gap: 0.15rem;
        padding: 0.15rem;
    }

    .toolbar-btn {
        width: 32px;
        height: 32px;
    }

    .toolbar-btn svg {
        width: 16px;
        height: 16px;
    }

    .zoom-text {
        font-size: 0.65rem;
    }

    /* 移动端图片信息浮层 - 更小 */
    .image-info-float {
        bottom: 4.5rem;
        left: 50%;
        transform: translateX(-50%);
        padding: 0.4rem 0.8rem;
        font-size: 0.65rem;
        gap: 0.5rem;
    }

    /* 移动端图片信息面板 - 调整位置 */
    .image-info-panel {
        top: 4rem;
        right: 0.75rem;
        left: 0.75rem;
        width: auto;
        max-width: 300px;
        margin: 0 auto;
        padding: 1rem;
    }

    .image-info-panel h3 {
        font-size: 0.85rem;
        margin-bottom: 0.75rem;
    }

    .info-item {
        padding: 0.4rem 0;
        font-size: 0.75rem;
    }

    /* 移动端导航按钮 - 更大更易点击 */
    .nav-btn {
        width: 44px;
        height: 44px;
    }

    .nav-prev {
        left: 0.75rem;
    }

    .nav-next {
        right: 0.75rem;
    }

    /* 移动端关闭按钮 */
    .close-btn {
        top: 0.75rem;
        right: 0.75rem;
        width: 40px;
        height: 40px;
    }

    .close-btn svg {
        width: 20px;
        height: 20px;
    }

    /* 移动端图片容器 */
    .image-container {
        padding: 1.5rem 1rem;
    }

    /* 移动端评论区 */
    .image-comments-section {
        padding: 1rem 1.5rem;
    }

    .divider-text {
        font-size: 0.85rem;
        padding: 0.4rem 1rem;
    }

    .divider-icon {
        width: 28px;
        height: 28px;
    }

    .divider-icon svg {
        width: 16px;
        height: 16px;
    }

    /* 移动端描述区域 */
    .description-header {
        padding: 1.5rem 1.5rem 0.75rem;
    }

    .description-title {
        font-size: 1.1rem;
    }

    .description-content {
        padding: 1.5rem;
    }

    /* 在移动端模式下，Block 组件保持紧凑 */
    .modal-description-section :deep(.bili-embed-neo),
    .modal-description-section :deep(.steam-card),
    .modal-description-section :deep(.xhs-embed-container),
    .modal-description-section :deep(.bangumi-card) {
        margin: 1rem 0 !important;
    }
}

/* 小屏移动端 (≤ 480px) */
@media (max-width: 480px) {

    /* 工具栏进一步压缩 */
    .image-toolbar {
        gap: 0.25rem;
        bottom: 0.75rem;
        right: 0.5rem;
        left: 0.5rem;
    }

    .toolbar-group {
        gap: 0.1rem;
        padding: 0.1rem;
    }

    .toolbar-btn {
        width: 28px;
        height: 28px;
    }

    .toolbar-btn svg {
        width: 14px;
        height: 14px;
    }

    .zoom-text {
        font-size: 0.6rem;
    }

    /* 图片信息浮层 */
    .image-info-float {
        bottom: 4rem;
        padding: 0.3rem 0.6rem;
        font-size: 0.6rem;
        gap: 0.4rem;
    }

    /* 图片信息面板 */
    .image-info-panel {
        top: 3.5rem;
        right: 0.5rem;
        left: 0.5rem;
        padding: 0.75rem;
    }

    .image-info-panel h3 {
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }

    .info-item {
        padding: 0.3rem 0;
        font-size: 0.7rem;
    }

    /* 导航按钮 */
    .nav-btn {
        width: 40px;
        height: 40px;
    }

    .nav-btn svg {
        width: 20px;
        height: 20px;
    }

    .nav-prev {
        left: 0.5rem;
    }

    .nav-next {
        right: 0.5rem;
    }

    /* 关闭按钮 */
    .close-btn {
        top: 0.5rem;
        right: 0.5rem;
        width: 36px;
        height: 36px;
    }

    .close-btn svg {
        width: 18px;
        height: 18px;
    }

    /* 图片容器 */
    .image-container {
        padding: 1rem 0.5rem;
    }

    /* 评论区 */
    .image-comments-section {
        padding: 0.75rem 1rem;
    }

    .divider-text {
        font-size: 0.8rem;
        padding: 0.3rem 0.8rem;
    }

    .divider-icon {
        width: 24px;
        height: 24px;
    }

    .divider-icon svg {
        width: 14px;
        height: 14px;
    }

    /* 描述区域 */
    .description-header {
        padding: 1rem 1rem 0.5rem;
    }

    .description-title {
        font-size: 1rem;
    }

    .description-content {
        padding: 1rem;
    }

    /* Markdown 内容 */
    .markdown-body {
        font-size: 0.9rem;
    }

    .markdown-body h1 {
        font-size: 1.3rem;
    }

    .markdown-body h2 {
        font-size: 1.15rem;
    }

    .markdown-body h3 {
        font-size: 1rem;
    }
}
</style>
