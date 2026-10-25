<script setup lang="ts">
import { computed } from 'vue';
import { tagHue } from '@/utils/tagColor';

const props = withDefaults(defineProps<{
    tagname: string;
    count?: number;
}>(), { count: 1 });

// 标签名决定身份色；主题只调整明度，同一标签在文章、列表和标签云中始终一致。
const tagStyle = computed(() => ({
    '--tag-hue': tagHue(props.tagname),
    fontSize: `${0.85 * (1 + Math.min(Math.max(props.count - 1, 0), 10) * 0.05)}rem`,
}));
</script>

<template>
    <router-link :to="{ name: 'ArchivePageByTag', params: { tagName: props.tagname } }"
        :style="tagStyle" :title="props.tagname" class="tag">
        <span class="hash" aria-hidden="true">#</span>
        <span class="text">{{ props.tagname }}</span>
    </router-link>
</template>

<style scoped>
.tag {
    --tag-ink: hsl(var(--tag-hue), var(--theme-tag-saturation), var(--theme-tag-ink-lightness));
    --tag-fill: hsl(var(--tag-hue), var(--theme-tag-saturation), var(--theme-tag-fill-lightness));
    display: inline-flex;
    align-items: center;
    gap: 0.25em;
    max-width: 100%;
    min-height: 1.8em;
    padding: 0.4rem 0.8rem;
    border: 1px solid color-mix(in srgb, var(--tag-ink) 28%, var(--tag-fill));
    border-radius: 8px;
    background: var(--tag-fill);
    color: var(--tag-ink);
    font-weight: 600;
    line-height: 1.3;
    text-decoration: none;
    transition: var(--theme-transition-colors);
}

.text { overflow-wrap: anywhere; min-width: 0; }
.hash { opacity: 0.75; font-weight: 400; }
.tag:hover { border-color: var(--tag-ink); text-decoration: underline; }
.tag:focus-visible { outline: 2px solid var(--tag-ink); outline-offset: 3px; }
</style>
