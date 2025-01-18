<script setup>
import { onMounted, ref, computed } from 'vue';
import globalVar from '@/globalVar';
import Post from '@/components/PostPanelComps/Post.vue';
import gsap from 'gsap';

const posts = ref({});
const currentPage = ref(1);
const postsPerPage = 3; // 每页显示3个帖子

onMounted(() => {
    posts.value = globalVar.markdowns;
});

const totalPages = computed(() => {
    return Math.ceil(Object.keys(posts.value).length / postsPerPage);
});

const paginatedPosts = computed(() => {
    const start = (currentPage.value - 1) * postsPerPage;
    const end = start + postsPerPage;
    const keys = Object.keys(posts.value).slice(start, end);
    console.log(`Current Page: ${currentPage.value}, Start: ${start}, End: ${end}, Keys: ${keys}`);
    return keys.map(key => ({ key, ...posts.value[key] }));
});

const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page;
    }
};

const goToFirstPage = () => {
    currentPage.value = 1;
};

const goToLastPage = () => {
    currentPage.value = totalPages.value;
};

const goToNextPage = () => {
    if (currentPage.value < totalPages.value) {
        currentPage.value += 1;
    }
};

const goToPreviousPage = () => {
    if (currentPage.value > 1) {
        currentPage.value -= 1;
    }
};
function onLeave(el, done) {
    gsap.to(el, {
        height: 0.1,
        width: 0.1,
        onComplete: done
    })
}

</script>

<template>
    <div class="PostPanel">
        <transition-group name="fade" tag="div" class="posts" @leave="onLeave">
            <Post v-for="post in paginatedPosts" :key="post.key" :imageUrl="post.imageUrl" :markdownUrl="post.key" />
        </transition-group>
        <div class="pagination">
            <button @click="goToFirstPage" :disabled="currentPage === 1">最前页</button>
            <button @click="goToPreviousPage" :disabled="currentPage === 1">前一页</button>
            <button v-for="page in totalPages" :key="page" @click="goToPage(page)" :disabled="currentPage === page">{{ page }}</button>
            <button @click="goToNextPage" :disabled="currentPage === totalPages">后一页</button>
            <button @click="goToLastPage" :disabled="currentPage === totalPages">最后页</button>
        </div>
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

.posts {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.pagination {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 1rem;
}

.pagination button {
    padding: 0.5rem 1rem;
    border-radius: 1rem;
    border: none;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: all 0.3s ease;
}
.pagination button:hover {
    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
    background-color: #aaaaaa;
    color: #f0f0f0;
}

.pagination button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}
.fade-move,
.fade-enter-active,
.fade-leave-active {
    opacity: 1;
    transition: all 0.5s ease;
}

.fade-enter,
.fade-leave-to {
    opacity: 0;
    transform: translateX(-150rem) scale(0);
}

.fade-leave-active {
    position: absolute;
}
</style>