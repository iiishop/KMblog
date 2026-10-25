<script setup>
import { onMounted, ref, computed, defineAsyncComponent, watch, nextTick } from 'vue';
import globalVar from '@/globalVar';
import gsap from 'gsap';
import config from '@/config';
import { selectPosts } from '@/utils/postIndex';

// 使用 Vite 的代码分割功能进行动态导入
const Post = defineAsyncComponent(() => import('@/components/PostPanelComps/Post.vue'));

const posts = selectPosts(globalVar.markdowns);
const currentPage = ref(1);
const dynamicPostsPerPage = ref(config.PostsPerPage); // 动态每页文章数
const sidebarHeight = ref(0);

// 计算侧边栏高度并动态调整每页文章数
function calculateDynamicPostsPerPage() {
    // 如果未启用动态调整，直接使用配置值
    if (!config.EnableDynamicPostsPerPage) {
        dynamicPostsPerPage.value = config.PostsPerPage;
        return;
    }

    // 获取侧边栏高度（取左右两侧的最大值）
    // 注意：BaseLayout 中的类名是 LeftList 和 RightList（大写）
    const leftSidebar = document.querySelector('.LeftList .context');
    const rightSidebar = document.querySelector('.RightList .context');

    const leftHeight = leftSidebar ? leftSidebar.offsetHeight : 0;
    const rightHeight = rightSidebar ? rightSidebar.offsetHeight : 0;
    sidebarHeight.value = Math.max(leftHeight, rightHeight);

    console.log('[PostPanel] Sidebar heights:', { leftHeight, rightHeight, max: sidebarHeight.value });

    // 如果侧边栏高度为 0，说明还没渲染完成，使用默认值
    if (sidebarHeight.value === 0) {
        dynamicPostsPerPage.value = config.PostsPerPage;
        return;
    }

    // 获取单个 Post 的平均高度（估算）
    const postElements = document.querySelectorAll('.posts > *');
    let avgPostHeight = 450; // 默认估算值（包含 gap）

    if (postElements.length > 0) {
        const totalHeight = Array.from(postElements).reduce((sum, el) => sum + el.offsetHeight, 0);
        const gaps = (postElements.length - 1) * 16; // 1rem gap = 16px
        avgPostHeight = (totalHeight + gaps) / postElements.length;
    }

    // 计算需要多少篇文章才能填满侧边栏高度
    // 公式：Math.max(配置的最小值, Math.ceil(侧边栏高度 / 单篇文章高度))
    const calculatedPosts = Math.ceil(sidebarHeight.value / avgPostHeight);
    const newPostsPerPage = Math.max(config.PostsPerPage, calculatedPosts);

    console.log('[PostPanel] Dynamic calculation:', {
        sidebarHeight: sidebarHeight.value,
        avgPostHeight,
        calculatedPosts,
        configMin: config.PostsPerPage,
        finalPostsPerPage: newPostsPerPage
    });

    // 只有当变化超过 1 篇时才更新（避免频繁变化）
    if (Math.abs(dynamicPostsPerPage.value - newPostsPerPage) >= 1) {
        dynamicPostsPerPage.value = newPostsPerPage;
        console.log('[PostPanel] Updated posts per page to:', newPostsPerPage);
    }
}

// 使用 ResizeObserver 监听侧边栏高度变化
let resizeObserver = null;
let resizeTimeout = null;
const layoutTimeouts = [];
let disposed = false;

function setupResizeObserver() {
    if (typeof ResizeObserver === 'undefined') return;

    resizeObserver = new ResizeObserver(() => {
        // 使用 debounce 避免频繁计算
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            calculateDynamicPostsPerPage();
        }, 300);
    });

    // 监听侧边栏
    const leftSidebar = document.querySelector('.LeftList .context');
    const rightSidebar = document.querySelector('.RightList .context');

    if (leftSidebar) resizeObserver.observe(leftSidebar);
    if (rightSidebar) resizeObserver.observe(rightSidebar);
}

onMounted(async () => {
    // 等待 DOM 渲染完成后计算
    await nextTick();
    if (disposed) return;

    // 多次尝试计算，确保侧边栏已经渲染完成
    layoutTimeouts.push(setTimeout(() => {
        calculateDynamicPostsPerPage();
    }, 500));

    layoutTimeouts.push(setTimeout(() => {
        calculateDynamicPostsPerPage();
    }, 1000));

    layoutTimeouts.push(setTimeout(() => {
        calculateDynamicPostsPerPage();
        setupResizeObserver();
    }, 1500));
});

// 组件卸载时清理
import { onUnmounted } from 'vue';
onUnmounted(() => {
    disposed = true;
    if (resizeObserver) {
        resizeObserver.disconnect();
    }
    clearTimeout(resizeTimeout);
    layoutTimeouts.forEach(clearTimeout);
});

const totalPages = computed(() => {
    return Math.max(1, Math.ceil(posts.length / dynamicPostsPerPage.value));
});

const paginatedPosts = computed(() => {
    // 摘要已排序，只挂载当前页的卡片。
    const start = (currentPage.value - 1) * dynamicPostsPerPage.value;
    const end = start + dynamicPostsPerPage.value;
    const paginatedResult = posts.slice(start, end);

    console.log(`Current Page: ${currentPage.value}, Posts per page: ${dynamicPostsPerPage.value}, Start: ${start}, End: ${end}`);
    return paginatedResult;
});

// 监听 dynamicPostsPerPage 变化，重置到第一页
watch(dynamicPostsPerPage, () => {
    if (currentPage.value > totalPages.value) {
        currentPage.value = 1;
    }
});

const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page;
    }
};

const goToFirst = () => { currentPage.value = 1; };
const goToLast = () => { currentPage.value = totalPages.value; };

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

// 分页数字显示逻辑：当前页 ±2，首尾必显示，其余省略号
const PAGE_WINDOW = 2;
const isPageVisible = (page) => {
    if (page === 1 || page === totalPages.value) return true;
    if (Math.abs(page - currentPage.value) <= PAGE_WINDOW) return true;
    return false;
};
const isPageEllipsisBefore = (page) => {
    return page === 2 && currentPage.value > PAGE_WINDOW + 2;
};
const isPageEllipsisAfter = (page) => {
    return page === totalPages.value - 1 && currentPage.value < totalPages.value - PAGE_WINDOW - 1;
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
            <Post v-for="(post, index) in paginatedPosts" :key="post.url" :imageUrl="post.imageUrl"
                :markdownUrl="post.url" :postMetadata="post" :data-index="index" />
        </transition-group>
        <div class="pagination" v-show="totalPages > 1">
            <button class="pg-nav pg-first" v-show="currentPage > 1" @click="goToFirst" aria-label="First page">«</button>
            <button class="pg-nav pg-prev" v-show="currentPage > 1" @click="goToPreviousPage" aria-label="Newer posts">‹<span class="pg-nav-label">Newer</span></button>

            <div class="pg-numbers">
                <template v-for="page in totalPages" :key="page">
                    <button
                        v-if="isPageVisible(page)"
                        class="pg-page"
                        :class="{ active: currentPage === page, adjacent: Math.abs(currentPage - page) === 1 }"
                        @click="goToPage(page)"
                    >{{ page }}</button>
                    <span v-else-if="isPageEllipsisBefore(page) || isPageEllipsisAfter(page)" class="pg-ellipsis">···</span>
                </template>
            </div>

            <button class="pg-nav pg-next" v-show="currentPage < totalPages" @click="goToNextPage" aria-label="Older posts"><span class="pg-nav-label">Older</span>›</button>
            <button class="pg-nav pg-last" v-show="currentPage < totalPages" @click="goToLast" aria-label="Last page">»</button>
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

/* === Pagination: unified underline metaphor — nav buttons match page numbers === */
.pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin-top: 2rem;
    padding: 0.25rem 0;
}

/* Nav arrows + labels — same transparent base and ::after underline as .pg-page */
.pg-nav {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.35rem 0.5rem;
    border: none;
    border-radius: 0;
    background: transparent;
    color: var(--theme-meta-text);
    font-family: inherit;
    font-size: 0.85rem;
    cursor: pointer;
    transition: color 0.2s ease;
    letter-spacing: 0.02em;
    position: relative;
}

.pg-nav::after {
    content: '';
    position: absolute;
    bottom: 2px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 2px;
    background: var(--theme-primary);
    transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.pg-nav:hover {
    color: var(--theme-heading-text);
}

.pg-nav:hover::after {
    width: 60%;
}

.pg-nav-label {
    font-size: 0.8rem;
    font-weight: 500;
}

.pg-numbers {
    display: flex;
    align-items: center;
    gap: 0.15rem;
    margin: 0 0.75rem;
}

.pg-page {
    min-width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    border-radius: 0;
    background: transparent;
    color: var(--theme-meta-text);
    font-family: 'SF Mono', 'Cascadia Code', 'Consolas', monospace;
    font-size: 0.9rem;
    cursor: pointer;
    padding: 0 0.3rem;
    position: relative;
    transition: color 0.2s ease;
    letter-spacing: 0.02em;
}

.pg-page::after {
    content: '';
    position: absolute;
    bottom: 2px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 2px;
    background: var(--theme-primary);
    transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.pg-page:hover { color: var(--theme-heading-text); }
.pg-page:hover::after { width: 60%; }

.pg-page.active {
    color: var(--theme-heading-text);
    font-weight: 700;
}

.pg-page.active::after {
    width: 80%;
    background: var(--theme-heading-text);
}

.pg-page.adjacent {
    color: var(--theme-body-text);
    font-weight: 500;
}

.pg-ellipsis {
    min-width: 1.5rem;
    text-align: center;
    color: var(--theme-meta-text);
    opacity: 0.5;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    user-select: none;
}

/* Mobile */
@media (max-width: 768px) {
    .pagination { margin-top: 1.5rem; gap: 0; }
    .pg-nav { padding: 0.35rem 0.5rem; }
    .pg-nav-label { display: none; }
    .pg-numbers { gap: 0; margin: 0 0.4rem; }
    .pg-page { min-width: 1.6rem; height: 1.6rem; font-size: 0.8rem; }
    .pg-first, .pg-last { display: none; }
}

@media (max-width: 480px) {
    .pg-nav { font-size: 0.75rem; }
    .pg-page { min-width: 1.4rem; height: 1.4rem; font-size: 0.75rem; }
    .pg-ellipsis { min-width: 1rem; }
}
</style>
