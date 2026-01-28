<script setup>
import globalVar from '@/globalVar';
import { ref, onMounted, computed, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { gsap } from 'gsap';
import axios from 'axios';
import { parseMarkdownMetadata } from "@/utils";

const props = defineProps({
    markdownUrls: {
        type: Array,
        default: () => []
    }
});

const posts = ref({});
const allFilteredPosts = ref([]); // 所有过滤后的文章
const displayedPosts = ref([]); // 当前显示的文章
const router = useRouter();

// 分页配置
const POSTS_PER_PAGE = 20;
const currentPage = ref(1);
const isLoading = ref(false);
const hasMore = ref(true);
const loadMoreTrigger = ref(null);

// 过滤掉带'公告'标签和 title 为 'About' 的文章
async function filterPosts() {
    const allPosts = globalVar.markdowns;
    const result = [];

    for (const [key, post] of Object.entries(allPosts)) {
        // 如果有 markdownUrls 限制，先检查是否在列表中
        if (props.markdownUrls.length > 0 && !props.markdownUrls.includes(key)) {
            continue;
        }

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
                result.push({ url: key, ...post });
            }
        } catch (error) {
            console.error(`Failed to check tags for ${key}:`, error);
            // 如果解析失败，还是保留这篇文章
            result.push({ url: key, ...post });
        }
    }

    // 按日期排序：从新到旧
    result.sort((a, b) => {
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);
        return dateB - dateA; // 降序排列
    });

    return result;
}

// 加载更多文章
function loadMorePosts() {
    if (isLoading.value || !hasMore.value) return;

    isLoading.value = true;

    // 模拟异步加载（实际上数据已经在内存中）
    setTimeout(() => {
        const start = (currentPage.value - 1) * POSTS_PER_PAGE;
        const end = start + POSTS_PER_PAGE;
        const newPosts = allFilteredPosts.value.slice(start, end);

        if (newPosts.length > 0) {
            displayedPosts.value.push(...newPosts);
            currentPage.value++;

            // 检查是否还有更多
            if (end >= allFilteredPosts.value.length) {
                hasMore.value = false;
            }
        } else {
            hasMore.value = false;
        }

        isLoading.value = false;
    }, 300);
}

// 设置 Intersection Observer
function setupIntersectionObserver() {
    if (!loadMoreTrigger.value) return;

    const observer = new IntersectionObserver(
        (entries) => {
            if (entries[0].isIntersecting && hasMore.value && !isLoading.value) {
                loadMorePosts();
            }
        },
        {
            root: null,
            rootMargin: '100px', // 提前 100px 开始加载
            threshold: 0.1
        }
    );

    observer.observe(loadMoreTrigger.value);

    // 组件卸载时清理
    return () => observer.disconnect();
}

onMounted(async () => {
    posts.value = globalVar.markdowns;
    allFilteredPosts.value = await filterPosts();

    // 初始加载第一页
    loadMorePosts();

    // Panel Entry Animation
    gsap.from('.ArchivePanel', {
        opacity: 0,
        y: 40,
        duration: 0.8,
        ease: 'power3.out'
    });

    // 设置滚动加载
    await nextTick();
    setupIntersectionObserver();
});

// 定义导航到 PostPage 的函数
function navigateToPost(markdownUrl) {
    // 移除空字符串部分，兼容 /posts/... 和 posts/...
    const urlParts = markdownUrl.split('/').filter(part => part !== '');
    const fileName = urlParts.pop();
    const mdName = fileName.replace('.md', '');

    let collection = null;
    // 检查剩余路径的最后一部分
    // 如果是 posts/MyCollection/file.md -> 剩余 [posts, MyCollection] -> lastPart 是 MyCollection
    // 如果是 posts/file.md -> 剩余 [posts] -> lastPart 是 posts
    if (urlParts.length > 0) {
        const lastPart = urlParts[urlParts.length - 1];
        // 只要不是 posts 目录本身，就认为是 collection
        if (lastPart.toLowerCase() !== 'posts') {
            collection = lastPart;
        }
    }

    router.push({
        name: 'PostPage',
        params: { collection, mdName }
    });
}

// 计算统计信息
const totalCount = computed(() => allFilteredPosts.value.length);
const displayedCount = computed(() => displayedPosts.value.length);
</script>

<template>
    <div class="ArchivePanel">
        <!-- Modern Header -->
        <div class="panel-header">
            <div class="icon-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="header-icon">
                    <path
                        d="M12.75 12.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM7.5 15.75a.75.75 0 1 0 0-1.5 .75.75 0 0 0 0 1.5ZM8.25 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM9.75 15.75a.75.75 0 1 0 0-1.5 .75.75 0 0 0 0 1.5ZM10.5 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM12 15.75a.75.75 0 1 0 0-1.5 .75.75 0 0 0 0 1.5ZM12.75 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM14.25 15.75a.75.75 0 1 0 0-1.5 .75.75 0 0 0 0 1.5ZM15 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM16.5 15.75a.75.75 0 1 0 0-1.5 .75.75 0 0 0 0 1.5ZM15 12.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM16.5 13.5a.75.75 0 1 0 0-1.5 .75.75 0 0 0 0 1.5Z" />
                    <path fill-rule="evenodd"
                        d="M6.75 2.25A.75.75 0 0 1 7.5 3v1.5h9V3A.75.75 0 0 1 18 3v1.5h.75a3 3 0 0 1 3 3v11.25a3 3 0 0 1-3 3H5.25a3 3 0 0 1-3-3V7.5a3 3 0 0 1 3-3H6V3a.75.75 0 0 1 .75-.75Zm13.5 9a1.5 1.5 0 0 0-1.5-1.5H5.25a1.5 1.5 0 0 0-1.5 1.5v7.5a1.5 1.5 0 0 0 1.5 1.5h13.5a1.5 1.5 0 0 0 1.5-1.5v-7.5Z"
                        clip-rule="evenodd" />
                </svg>
            </div>
            <div class="header-text">
                <h1>Archive</h1>
                <span class="subtitle">历史文章归档 · {{ displayedCount }} / {{ totalCount }}</span>
            </div>
        </div>

        <div class="timeline-container">
            <div v-for="(post, index) in displayedPosts" :key="post.url" class="post-item-wrapper">
                <!-- Timeline Marker logic remains same but styled differently -->
                <div v-if="index === 0 || new Date(post.date).getFullYear() !== new Date(displayedPosts[index - 1].date).getFullYear()"
                    class="timeline-marker year-marker">
                    <span class="year-text">{{ new Date(post.date).getFullYear() }}</span>
                </div>

                <div v-if="index === 0 || new Date(post.date).getMonth() !== new Date(displayedPosts[index - 1].date).getMonth()"
                    class="timeline-marker month-marker">
                    <span class="month-text">{{ new Date(post.date).toLocaleString('default', { month: 'long' })
                    }}</span>
                </div>

                <div @click="navigateToPost(post.url)" class="post-content post-entry">
                    <div class="post-dot"></div>
                    <div class="post-info">
                        <h3>{{ post.title }}</h3>
                        <p class="post-date">
                            <svg class="date-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            {{ post.date }}
                        </p>
                    </div>
                </div>
            </div>

            <!-- 加载触发器 -->
            <div ref="loadMoreTrigger" class="load-more-trigger">
                <div v-if="isLoading" class="loading-indicator">
                    <div class="spinner"></div>
                    <span>加载中...</span>
                </div>
                <div v-else-if="!hasMore" class="end-message">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>已加载全部 {{ totalCount }} 篇文章</span>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.ArchivePanel {
    display: flex;
    flex-direction: column;
    color: var(--theme-panel-text);
    width: 100%;
    background: var(--theme-panel-bg);
    border-radius: 20px;
    box-shadow: 0 10px 30px -10px var(--theme-shadow-md);
    padding: 1.5rem;
    box-sizing: border-box;
    backdrop-filter: blur(10px);
    border: 1px solid var(--theme-panel-border);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.ArchivePanel:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 40px -12px var(--theme-shadow-lg);
}

.panel-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--theme-border-light);
    margin-bottom: 1.5rem;
}

.icon-wrapper {
    background: linear-gradient(135deg, var(--theme-success) 0%, var(--theme-success-hover) 100%);
    padding: 10px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px var(--theme-shadow-md);
}

.header-icon {
    width: 24px;
    height: 24px;
    color: var(--theme-button-text);
}

.header-text {
    display: flex;
    flex-direction: column;
}

h1 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
    background: linear-gradient(to right, var(--theme-panel-text), var(--theme-meta-text));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.subtitle {
    font-size: 0.85rem;
    opacity: 0.7;
    font-weight: 500;
}

.timeline-container {
    position: relative;
    padding-left: 1rem;
    border-left: 2px solid var(--theme-border-light);
    margin-left: 0.5rem;
}

.post-item-wrapper {
    position: relative;
}

.timeline-marker {
    position: relative;
    margin-left: -1rem;
    /* stick out to left */
    padding-left: 1.5rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
}

.year-marker {
    margin-top: 1.5rem;
}

.year-marker::before {
    content: '';
    position: absolute;
    left: -5px;
    /* adjust to center on border line */
    width: 12px;
    height: 12px;
    background: var(--theme-success);
    border-radius: 50%;
    border: 3px solid var(--theme-panel-bg);
    box-shadow: 0 0 0 1px var(--theme-success);
}

.year-text {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--theme-heading-text);
    opacity: 0.8;
}

.month-marker {
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

.month-marker::before {
    content: '';
    position: absolute;
    left: -3px;
    width: 8px;
    height: 8px;
    background: var(--theme-success-hover);
    border-radius: 50%;
    border: 2px solid var(--theme-panel-bg);
}

.month-text {
    font-size: 1rem;
    font-weight: 600;
    color: var(--theme-meta-text);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.post-content {
    cursor: pointer;
    padding: 0.8rem 1rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 12px;
    margin-bottom: 0.5rem;
    background: var(--theme-surface-hover);
    border: 1px solid transparent;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.post-dot {
    width: 6px;
    height: 6px;
    background-color: var(--theme-divider);
    border-radius: 50%;
    flex-shrink: 0;
    transition: background-color 0.3s;
}

.post-info {
    width: 100%;
}

.post-content:hover {
    background: var(--theme-surface-default);
    transform: translateX(5px);
    box-shadow: 0 4px 20px -5px var(--theme-shadow-md);
    border-color: var(--theme-border-medium);
}

.post-content:hover .post-dot {
    background-color: var(--theme-success);
    box-shadow: 0 0 8px var(--theme-success);
}

.post-content h3 {
    margin: 0;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--theme-content-text);
    transition: color 0.2s;
}

.post-content:hover h3 {
    color: var(--theme-success);
}

.post-date {
    margin: 0.3rem 0 0;
    font-size: 0.75rem;
    color: var(--theme-meta-text);
    display: flex;
    align-items: center;
    gap: 4px;
}

.date-icon {
    width: 12px;
    height: 12px;
}

/* === 加载更多样式 === */
.load-more-trigger {
    margin-top: 2rem;
    padding: 1.5rem;
    display: flex;
    justify-content: center;
    align-items: center;
}

.loading-indicator {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: var(--theme-meta-text);
    font-size: 0.95rem;
    font-weight: 500;
}

.spinner {
    width: 20px;
    height: 20px;
    border: 3px solid var(--theme-border-light);
    border-top-color: var(--theme-success);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.end-message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--theme-meta-text);
    font-size: 0.9rem;
    font-weight: 500;
    padding: 1rem;
    background: var(--theme-surface-hover);
    border-radius: 12px;
    border: 1px dashed var(--theme-border-light);
}

.end-message svg {
    color: var(--theme-success);
    flex-shrink: 0;
}
</style>