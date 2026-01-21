<script setup>
import { defineAsyncComponent } from 'vue';

// 使用 Vite 的代码分割功能进行动态导入
const BaseLayout = defineAsyncComponent(() => import('@/views/BaseLayout.vue'));
const ArchivePanel = defineAsyncComponent(() => import('@/components/ArchivePanel.vue'));

const props = defineProps({
    markdownUrls: {
        type: Array,
        default: () => []
    }
});
</script>

<template>
    <BaseLayout :showTipList="false">
        <template #main>
            <ArchivePanel :markdown-urls="props.markdownUrls" />
        </template>
    </BaseLayout>
</template>
