<script setup>
import globalVar from '@/globalVar';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { gsap } from 'gsap';

const props = defineProps({
    markdownUrls: {
        type: Array,
        default: () => []
    }
});

const posts = ref({});
const filteredPosts = ref({});
const router = useRouter();

onMounted(() => {
    posts.value = globalVar.markdowns;
    if (props.markdownUrls.length === 0) {
        filteredPosts.value = posts.value;
    } else {
        filteredPosts.value = Object.keys(posts.value)
            .filter(url => props.markdownUrls.includes(url))
            .reduce((acc, url) => {
                acc[url] = posts.value[url];
                return acc;
            }, {});
    }
    gsap.from('.ArchivePanel', { opacity: 0, y: 50, duration: 1 });
});

// 定义导航到 PostPage 的函数
function navigateToPost(markdownUrl) {
    const urlParts = markdownUrl.split('/');
    const mdName = urlParts.pop().replace('.md', '');
    const collection = urlParts.length > 3 ? urlParts[3] : null;

    router.push({
        name: 'PostPage',
        params: { collection, mdName }
    });
}
</script>

<template>
    <div class="ArchivePanel">
        <div v-for="(post, url, index) in filteredPosts" :key="url" class="post-item">
            <template v-if="index === 0 || new Date(post.date).getFullYear() !== new Date(Object.values(filteredPosts)[index - 1].date).getFullYear()">
                <h1 class="year">{{ new Date(post.date).getFullYear() }}</h1>
            </template>
            <template v-if="index === 0 || new Date(post.date).getMonth() !== new Date(Object.values(filteredPosts)[index - 1].date).getMonth()">
                <h2 class="month">{{ new Date(post.date).toLocaleString('default', { month: 'long' }) }}</h2>
            </template>
            <div @click="navigateToPost(url)" class="post-content">
                <h3>{{ post.title }}</h3>
                <p>{{ post.date }}</p>
            </div>
        </div>
    </div>
</template>

<style scoped>
.ArchivePanel {
    display: flex;
    flex-direction: column;
    color: rgb(10, 10, 10);
    width: 100%;
    background-color: #f8f8f8;
    border-radius: 1rem;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
    padding: 1rem;
    box-sizing: border-box;
}

.year {
    margin-top: 2rem;
    font-size: 2rem;
    color: #333;
    border-bottom: 2px solid #ddd;
    padding-bottom: 0.5rem;
}

.month {
    margin-top: 1.5rem;
    font-size: 1.5rem;
    color: #666;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.5rem;
}

.post-item {
    margin-top: 1rem;
}

.post-content {
    cursor: pointer;
    padding: 0.5rem;
    transition: background-color 0.3s, transform 0.3s;
    border-radius: 0.5rem;
}

.post-content:hover {
    background-color: #e0e0e0;
    transform: translateX(5px);
}

.post-content h3 {
    margin: 0;
    font-size: 1.2rem;
    color: #007BFF;
}

.post-content p {
    margin: 0.2rem 0 0;
    font-size: 0.9rem;
    color: #999;
}
</style>