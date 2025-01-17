<script setup>
import { onMounted, ref } from 'vue';
import globalVar from '@/globalVar';
import Post from '@/components/PostPanelComps/Post.vue';

const posts = ref({});

onMounted(() => {
    posts.value = globalVar.markdowns;
});
</script>

<template>
    <div class="PostPanel">
        <Post v-for="(key, index) in Object.keys(posts)" :key="index" :imageUrl="posts[key].imageUrl" :markdownUrl="key" />
    </div>
</template>

<style scoped>
.PostPanel {
    display: flex;
    gap: 2rem;
    flex-direction: column;
    color: var(--posts-text-color);
    width: 100%;
}
</style>