<template>
    <div ref="rootRef" class="markdown-preview-container">
        <ImageDescription v-if="source !== null && image" :image="image" :content="source" />
        <MarkdownPanel v-else-if="source !== null" :markdown-url="markdownUrl" :content="source" :scroll-container="scrollContainer" />
    </div>
</template>

<script setup>
import { ref, shallowRef, watch, onMounted, onBeforeUnmount } from 'vue';
import MarkdownPanel from '@/components/MarkdownPanel.vue';
import ImageDescription from '@/components/WaterfallPanelComps/ImageDescription.vue';

const props = defineProps({
    content: { type: String, required: true },
    markdownUrl: { type: String, default: '' },
    image: { type: Object, default: null },
    active: { type: Boolean, default: true },
    scrollSync: { type: Number, default: 0 }
});
const emit = defineEmits(['scroll']);
const rootRef = ref(null);
const source = ref(null);
const scrollContainer = shallowRef(null);
let renderTimer;
let scrollTimer;
let isScrollingFromEditor = false;
watch(() => [props.content, props.active], () => {
    clearTimeout(renderTimer);
    if (props.active) renderTimer = setTimeout(() => { source.value = props.content; }, 180);
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
    if (rootRef.value) {
        previewContainer = rootRef.value.closest('.preview-panel') || rootRef.value.parentElement;
        if (previewContainer) {
            previewContainer.addEventListener('scroll', handlePreviewScroll, { passive: true });
        }
    }
});

onMounted(() => { scrollContainer.value = previewContainer; });
onBeforeUnmount(() => {
    clearTimeout(renderTimer);
    clearTimeout(scrollTimer);
    previewContainer?.removeEventListener('scroll', handlePreviewScroll);
});
</script>
