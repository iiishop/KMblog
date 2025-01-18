<script setup>
import BaseLayout from '@/views/BaseLayout.vue';
import ArchivePanel from '@/components/ArchivePanel.vue';

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
