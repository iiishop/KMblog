<template>
    <div class="markdown-preview-container">
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
import { renderDynamicComponents } from '@/components/MarkdownPanelComps/DynamicComponentRenderer.js';
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

const props = defineProps({
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
let isScrollingFromEditor = false; // 标记是否来自编辑器的滚动

// 渲染Markdown - 完全复用MarkdownPanel.vue的逻辑
const renderMarkdown = async (markdown) => {
    try {
        // 解析front-matter
        const { body } = fm(markdown);

        // 使用相同的markdown-it实例渲染
        htmlContent.value = md.render(body);

        // 在nextTick中渲染动态组件
        await nextTick();
        const container = contentRef.value;
        if (container) {
            // 使用相同的动态组件渲染器
            renderDynamicComponents(container, {
                'steamgameblock': SteamGameBlock,
                'bangumiblock': BangumiBlock,
                'bilibilivideoblock': BilibiliVideoBlock,
                'githubrepoblock': GithubRepoBlock,
                'xiaohongshunoteblock': XiaohongshuNoteBlock
            });

            // 渲染Mermaid图表
            await nextTick();
            if (typeof mermaid !== 'undefined') {
                try {
                    mermaid.mermaidAPI.reset();
                    await mermaid.run({
                        nodes: container.querySelectorAll('.mermaid'),
                    });

                    // 修复SVG尺寸
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
                    console.warn('Mermaid rendering failed:', error);
                }
            }
        }
    } catch (error) {
        console.error('Markdown rendering failed:', error);
    }
};

// 监听内容变化
watch(() => props.content, (newContent) => {
    renderMarkdown(newContent);
}, { immediate: true });

// 滚动同步 - 从编辑器到预览
watch(() => props.scrollSync, (scrollPercentage) => {
    if (contentRef.value) {
        isScrollingFromEditor = true;
        const container = contentRef.value.parentElement;
        const maxScroll = container.scrollHeight - container.clientHeight;
        container.scrollTop = maxScroll * scrollPercentage;

        // 重置标记
        setTimeout(() => {
            isScrollingFromEditor = false;
        }, 100);
    }
});

// 监听预览面板的滚动 - 从预览到编辑器
const handlePreviewScroll = (event) => {
    if (isScrollingFromEditor) return; // 如果是编辑器触发的滚动，忽略

    const container = event.target;
    const scrollPercentage = container.scrollTop / (container.scrollHeight - container.clientHeight);
    emit('scroll', scrollPercentage);
};

// 在组件挂载后添加滚动监听
let previewContainer = null;

onMounted(() => {
    if (contentRef.value) {
        previewContainer = contentRef.value.parentElement;
        if (previewContainer) {
            previewContainer.addEventListener('scroll', handlePreviewScroll);
        }
    }
});

onBeforeUnmount(() => {
    if (previewContainer) {
        previewContainer.removeEventListener('scroll', handlePreviewScroll);
    }
});
</script>

<style scoped>
.markdown-preview-container {
    overflow-y: auto;
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
