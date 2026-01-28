<script setup>
import { onMounted, ref, computed, defineAsyncComponent } from 'vue';
import globalVar from '@/globalVar';
import gsap from 'gsap';
import config from '@/config';
import axios from 'axios';
import { parseMarkdownMetadata } from "@/utils";

// 使用 Vite 的代码分割功能进行动态导入
const Post = defineAsyncComponent(() => import('@/components/PostPanelComps/Post.vue'));

const posts = ref({});
const currentPage = ref(1);

// 过滤掉带'公告'标签和 title 为 'About' 的文章
async function filterAnnouncements() {
    const allPosts = globalVar.markdowns;
    const filteredPosts = {};

    for (const [key, post] of Object.entries(allPosts)) {
        try {
            // 获取文章内容
            const response = await axios.get(key.startsWith('http') ? key : new URL(key, import.meta.url).href);
            const content = response.data;

            // 解析元数据
            const { meta } = await parseMarkdownMetadata(content);

            // 检查是否有'公告'标签或 title 为 'About'
            const hasAnnouncementTag = meta.tags && (Array.isArray(meta.tags) ? meta.tags.includes('公告') : meta.tags === '公告');
            const isAboutPage = meta.title && meta.title.toLowerCase() === 'about';

            // 如果既没有'公告'标签也不是 About 页面，则加入列表
            if (!hasAnnouncementTag && !isAboutPage) {
                filteredPosts[key] = post;
            }
        } catch (error) {
            console.error(`Failed to check tags for ${key}:`, error);
            // 如果解析失败，还是保留这篇文章
            filteredPosts[key] = post;
        }
    }

    posts.value = filteredPosts;
}

onMounted(() => {
    filterAnnouncements();
});

const totalPages = computed(() => {
    return Math.ceil(Object.keys(posts.value).length / config.PostsPerPage);
});

const paginatedPosts = computed(() => {
    // 先将所有文章转换为数组并按日期降序排序
    const sortedPosts = Object.keys(posts.value)
        .map(key => ({ key, ...posts.value[key] }))
        .sort((a, b) => new Date(b.date) - new Date(a.date));

    // 然后进行分页
    const start = (currentPage.value - 1) * config.PostsPerPage;
    const end = start + config.PostsPerPage;
    const paginatedResult = sortedPosts.slice(start, end);

    console.log(`Current Page: ${currentPage.value}, Start: ${start}, End: ${end}`);
    return paginatedResult;
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

// Vue TransitionGroup hooks for staggered animation
function onBeforeEnter(el) {
    el.style.opacity = 0;
    el.style.transform = 'translateY(30px)';
}

function onEnter(el, done) {
    const delay = el.dataset.index * 100; // 100ms delay per item
    setTimeout(() => {
        gsap.to(el, {
            opacity: 1,
            y: 0,
            duration: 0.6,
            ease: 'power2.out',
            onComplete: done
        });
    }, delay);
}

function onLeave(el, done) {
    gsap.to(el, {
        opacity: 0,
        y: -20,
        scale: 0.98,
        duration: 0.4,
        ease: 'power2.in',
        onComplete: done
    });
}

</script>

<template>
    <div class="PostPanel">
        <transition-group name="list" tag="div" class="posts" @before-enter="onBeforeEnter" @enter="onEnter"
            @leave="onLeave" appear>
            <Post v-for="(post, index) in paginatedPosts" :key="post.key" :imageUrl="post.imageUrl"
                :markdownUrl="post.key" :data-index="index" />
        </transition-group>
        <div class="pagination">
            <button @click="goToFirstPage" :disabled="currentPage === 1">最前页</button>
            <button @click="goToPreviousPage" :disabled="currentPage === 1">前一页</button>
            <button v-for="page in totalPages" :key="page" @click="goToPage(page)" :disabled="currentPage === page">{{
                page }}</button>
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

/* List transition styles */
.list-move {
    transition: transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.list-leave-active {
    position: absolute;
    width: 100%;
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
    background: var(--theme-panel-bg);
    color: var(--theme-panel-text);
    box-shadow: 1px 1px 5px var(--theme-shadow-sm);
    cursor: pointer;
    transition: all 0.3s ease;
}

.pagination button:hover {
    box-shadow: 2px 2px 10px var(--theme-shadow-md);
    background-color: var(--theme-nav-hover-bg);
    color: var(--theme-link-color);
}

.pagination button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}
</style>