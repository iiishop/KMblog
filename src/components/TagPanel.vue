<script setup>
import { ref, onMounted, defineAsyncComponent } from 'vue';
import globalVar from '@/globalVar';

// 使用 Vite 的代码分割功能进行动态导入
const Tag = defineAsyncComponent(() => import('./PostPanelComps/Tag.vue'));

const tags = ref({});

onMounted(() => {
    tags.value = globalVar.tags
    console.log(tags.value)
})
</script>
<template>
    <div class="TagPanel">
        <h1>Tags</h1>
        <div class="TagList">
            <Tag v-for="( tag, tagname ) in tags" :tagname="tagname" :count="tag.length" />
        </div>
    </div>
</template>
<style scoped>
.TagPanel {
    padding: 1rem;
    gap: 1rem;
    width: 100%;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    text-align: center;
    align-items: center;
    justify-content: center;
    box-shadow: 1px 1px 5px var(--tag-panel-box-shadow);
    background-color: var(--tag-panel-background-color);

}

.TagPanel h1 {
    color: var(--tag-panel-text-color);
}

.TagList {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.8rem;
    width: 100%;
}
</style>