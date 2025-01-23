<script setup>
import { defineProps, defineAsyncComponent } from 'vue';

// 使用 Vite 的代码分割功能进行动态导入
const BaseLayout = defineAsyncComponent(() => import('@/views/BaseLayout.vue'));
const CategoryPanel = defineAsyncComponent(() => import('@/components/CategoryPanel.vue'));

const props = defineProps({
    categoryPath: {
        type: Array,
        default: () => [],
    }
});
</script>

<template>
    <BaseLayout :showTipList="false">
        <template #main>
            <CategoryPanel :categoryPath="categoryPath" />
        </template>
    </BaseLayout>
</template>
