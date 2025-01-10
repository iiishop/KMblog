<script setup>
import { onMounted, ref } from 'vue';
import globalVar from '@/globalVar';
import Post from '@/components/Post.vue';
const posts = ref([]);


onMounted(() => {
    posts.value = globalVar.markdowns;

});
</script>
<template>
    <div class="PostPanel">
        <Post v-for="(post, index) in posts" :key="post.id" :imageUrl="post.imageUrl" :markdownUrl="post.markdownUrl" />
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