<script setup>
import { ref, onMounted } from 'vue';
import Tag from './PostPanelComps/Tag.vue';
import globalVar from '@/globalVar';

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
    width: 100%;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
}
.TagPanel h1 {
    color: black;
}
.TagList {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
    width: 100%;
    padding: 10px;
}
</style>
