<template>
    <teleport to="body">
        <div v-if="isOpen" class="image-modal" @click.self="handleClose" @keydown.esc="handleClose" tabindex="0"
            ref="modalRef">
            <!-- 背景模糊层 -->
            <div class="modal-backdrop"></div>

            <!-- 主内容区 -->
            <div class="modal-content" :class="{ 'no-description': !hasDescription }">
                <!-- 左侧：图片 -->
                <div class="modal-image-section">
                    <div class="image-container">
                        <img :src="image.src" :alt="image.alt" class="modal-image" />

                        <!-- 图片信息浮层 -->
                        <div class="image-info-float">
                            <span class="image-dimensions">{{ imageDimensions }}</span>
                            <span class="image-format">{{ imageFormat }}</span>
                        </div>
                    </div>

                    <!-- 关闭按钮 -->
                    <button class="close-btn" @click="handleClose" aria-label="Close modal">
                        <svg viewBox="0 0 24 24">
                            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2"
                                stroke-linecap="round" />
                        </svg>
                    </button>
                </div>

                <!-- 右侧：描述（只在有描述时显示） -->
                <div v-if="hasDescription" class="modal-description-section">
                    <div class="description-header">
                        <h2 class="description-title">图片描述</h2>
                    </div>
                    <div class="description-content">
                        <!-- Markdown 渲染 -->
                        <div v-html="renderedDescription" class="markdown-body"></div>
                    </div>

                    <!-- 评论区域 -->
                    <div class="comments-section">
                        <UtterancesComments :issueTitle="`图片: ${image.alt || image.src}`" />
                    </div>
                </div>
            </div>
        </div>
    </teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import MarkdownIt from 'markdown-it';
import UtterancesComments from '@/components/UtterancesComments.vue';

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
    }
});

const emit = defineEmits(['close', 'next', 'prev']);

// Refs
const modalRef = ref(null);

// 状态
const isOpen = ref(false);
const mdDescription = ref('');

// Markdown 渲染器 - 禁用 HTML 标签以避免注入问题
const md = new MarkdownIt({
    html: false, // 禁用 HTML 标签
    linkify: true,
    typographer: true
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

    return md.render(desc);
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
    emit('close');
}

// 键盘事件处理
function handleKeydown(e) {
    if (!isOpen.value) return;

    switch (e.key) {
        case 'Escape':
            handleClose();
            break;
        case 'ArrowLeft':
            emit('prev');
            break;
        case 'ArrowRight':
            emit('next');
            break;
    }
}

// 监听图片变化
watch(() => props.image, (newVal) => {
    if (newVal) {
        isOpen.value = true;
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
.modal-content.no-description .modal-image-section {
    flex: 1;
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
    transition: transform 0.3s ease;
}

.modal-image:hover {
    transform: scale(1.02);
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

/* 评论区域 */
.comments-section {
    padding: 0 2.5rem 2rem;
    border-top: 1px solid #e8e8e8;
    margin-top: 1rem;
}

.comments-section :deep(.utterances-comments) {
    margin: 1rem 0 0 0;
    padding: 1.5rem;
    background: #fff;
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

/* 响应式 */
@media (max-width: 968px) {
    .modal-content {
        flex-direction: column;
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
}
</style>
