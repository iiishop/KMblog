<script setup>
import BaseLayout from '@/views/BaseLayout.vue';
import CategoryPanel from '@/components/CategoryPanel.vue';

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
