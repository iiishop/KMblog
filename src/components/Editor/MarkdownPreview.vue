<template>
    <div class="markdown-preview-container">
        <p v-if="renderError" class="render-error" role="status">{{ renderError }}</p>
        <article class="post-content markdown" ref="contentRef">
            <div v-html="htmlContent"></div>
        </article>
    </div>
</template>

<script setup>
import { ref, watch, nextTick, defineAsyncComponent, onMounted, onBeforeUnmount } from 'vue';
import fm from 'front-matter';

// 复用MarkdownPanel.vue的渲染模块
import md from '@/components/MarkdownPanelComps/MarkdownRenender.js';
import '@/components/MarkdownPanelComps/MarkdownStyle.css';
import { renderDynamicComponents, unmountDynamicComponents } from '@/components/MarkdownPanelComps/DynamicComponentRenderer.js';
import mermaid from 'mermaid';

// 复用MarkdownPanel.vue的Block组件
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
const CarouselBlock = defineAsyncComponent(() =>
    import('@/components/MarkdownPanelComps/CarouselBlock.vue')
);

const props = defineProps({
    active: { type: Boolean, default: true },
    content: {
        type: String,
        required: true
    },
    scrollSync: {
        type: Number,
        default: 0
    }
});

const emit = defineEmits(['scroll']);

const htmlContent = ref('');
const contentRef = ref(null);
const renderError = ref('');
let isScrollingFromEditor = false;
let renderTimer;
let scrollTimer;
let disposed = false;
let revision = 0;
let rendering = false;
let pending = false;

// Coalesce typing bursts, and serialize asynchronous chart rendering. Never
// let an older render mount apps into a newer document's DOM.
async function renderMarkdown() {
    if (rendering || disposed || !props.active) return;
    rendering = true;
    pending = false;
    const currentRevision = revision;
    try {
        const { body } = fm(props.content);
        const processed = body.replace(/!\[([^\]]*)\]\(([^)<>]+\s+[^)<>]+)\)/g, '![$1](<$2>)');
        const html = md.render(processed);
        unmountDynamicComponents(contentRef.value);
        htmlContent.value = html;
        renderError.value = '';
        await nextTick();
        const container = contentRef.value;
        if (disposed || currentRevision !== revision || !container || !props.active) return;
        renderDynamicComponents(container, {
            steamgameblock: SteamGameBlock, bangumiblock: BangumiBlock,
            bilibilivideoblock: BilibiliVideoBlock, githubrepoblock: GithubRepoBlock,
            xiaohongshunoteblock: XiaohongshuNoteBlock, carouselblock: CarouselBlock
        });
        const nodes = container.querySelectorAll('.mermaid');
        if (nodes.length) {
            try {
                await mermaid.run({ nodes, suppressErrors: true });
            } catch {
                if (!disposed && currentRevision === revision) renderError.value = '图表语法暂时不完整，请继续编辑。';
            }
        }
    } catch (error) {
        if (!disposed && currentRevision === revision) renderError.value = `预览暂未更新，请检查文章头部格式：${error.message}`;
    } finally {
        rendering = false;
        if (pending && !disposed && props.active) {
            clearTimeout(renderTimer);
            renderTimer = setTimeout(renderMarkdown, 180);
        }
    }
}
watch(() => [props.content, props.active], () => {
    revision++;
    pending = true;
    clearTimeout(renderTimer);
    if (props.active) renderTimer = setTimeout(renderMarkdown, 180);
}, { immediate: true });

// 滚动同步 - 从编辑器到预览
watch(() => props.scrollSync, (scrollPercentage) => {
    if (previewContainer && props.active) {
        isScrollingFromEditor = true;
        const container = previewContainer;
        const maxScroll = container.scrollHeight - container.clientHeight;
        container.scrollTop = maxScroll * scrollPercentage;

        // 重置标记
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(() => {
            isScrollingFromEditor = false;
        }, 100);
    }
});

// 监听预览面板的滚动 - 从预览到编辑器
const handlePreviewScroll = (event) => {
    if (isScrollingFromEditor) return; // 如果是编辑器触发的滚动，忽略

    const container = event.target;
    const maxScroll = container.scrollHeight - container.clientHeight;

    // 防止除以0
    if (maxScroll <= 0) return;

    const scrollPercentage = container.scrollTop / maxScroll;
    emit('scroll', scrollPercentage);
};

// 在组件挂载后添加滚动监听
let previewContainer = null;

onMounted(() => {
    if (contentRef.value) {
        previewContainer = contentRef.value.closest('.preview-panel') || contentRef.value.parentElement;
        if (previewContainer) {
            previewContainer.addEventListener('scroll', handlePreviewScroll, { passive: true });
        }
    }
});

onBeforeUnmount(() => {
    disposed = true;
    revision++;
    clearTimeout(renderTimer);
    clearTimeout(scrollTimer);
    unmountDynamicComponents(contentRef.value);
    if (previewContainer) {
        previewContainer.removeEventListener('scroll', handlePreviewScroll);
    }
});
</script>

<style scoped>
.render-error { padding: 10px; border-left: 3px solid #c24b36; font-size: 13px; line-height: 1.6; }
.markdown-preview-container {
    overflow-wrap: anywhere;
    padding: 2rem;
    background-color: var(--theme-content-bg);
    transition: var(--theme-transition-colors);
}

/* 复用MarkdownStyle.css中的样式 */
.post-content {
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
    line-height: 1.8;
    color: var(--theme-content-text);
    font-size: 1.05rem;
    transition: var(--theme-transition-colors);
}

/* 响应式设计 */
@media (max-width: 968px) {
    .markdown-preview-container {
        padding: 1.5rem;
    }

    .post-content {
        font-size: 1rem;
    }
}

@media (max-width: 640px) {
    .markdown-preview-container {
        padding: 1rem;
    }

    .post-content {
        font-size: 0.95rem;
    }
}
</style>
