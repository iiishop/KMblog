<template>
    <div class="toc-panel" :class="{ 'toc-collapsed': collapsed }">
        <div class="toc-header">
            <h3 class="toc-title">目录</h3>
            <button class="toc-toggle" @click="collapsed = !collapsed" :aria-label="collapsed ? '展开目录' : '收起目录'">
                <svg v-if="collapsed" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 9l-7 7-7-7" />
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 15l-7-7-7 7" />
                </svg>
            </button>
        </div>
        <nav class="toc-nav" v-show="!collapsed">
            <ul class="toc-list" v-if="tocItems.length > 0">
                <li v-for="item in tocItems" :key="item.id"
                    :class="['toc-item', `toc-level-${item.level}`, { 'toc-active': activeHeadingId === item.id }]">
                    <a :href="`#${item.id}`" @click.prevent="scrollToHeading(item.id)" class="toc-link">
                        <span class="toc-indicator"></span>
                        <span class="toc-text">{{ item.text }}</span>
                    </a>
                </li>
            </ul>
            <div v-else class="toc-empty">
                <p>暂无目录</p>
            </div>
        </nav>
    </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
    contentSelector: {
        type: String,
        default: '.post-content.markdown'
    }
});

const tocItems = ref([]);
const activeHeadingId = ref('');
const collapsed = ref(false);
const headingObserver = ref(null);
const contentObserver = ref(null);

// 提取目录
const extractTOC = () => {
    const container = document.querySelector(props.contentSelector);
    if (!container) return;

    const headings = container.querySelectorAll('h2, h3, h4');
    const items = [];

    headings.forEach((heading, index) => {
        const level = parseInt(heading.tagName.substring(1));
        const text = heading.textContent.trim();
        const id = heading.id || `heading-${index}`;

        // 如果标题没有 id，添加一个
        if (!heading.id) {
            heading.id = id;
        }

        items.push({ id, text, level, element: heading });
    });

    tocItems.value = items;

    // 设置 Intersection Observer 来追踪当前标题
    setupHeadingObserver();
};

// 设置标题观察器
const setupHeadingObserver = () => {
    // 清理旧的观察器
    if (headingObserver.value) {
        headingObserver.value.disconnect();
    }

    if (tocItems.value.length === 0) return;

    const options = {
        rootMargin: '-80px 0px -80% 0px',
        threshold: 0
    };

    headingObserver.value = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                activeHeadingId.value = entry.target.id;
            }
        });
    }, options);

    // 观察所有标题
    tocItems.value.forEach((item) => {
        if (item.element) {
            headingObserver.value.observe(item.element);
        }
    });
};

// 滚动到指定标题
const scrollToHeading = (id) => {
    const element = document.getElementById(id);
    if (element) {
        const offset = 80; // 顶部偏移量
        const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });

        // 更新活动标题
        activeHeadingId.value = id;
    }
};

// 监听内容变化，重新提取目录
const observeContentChanges = () => {
    const container = document.querySelector(props.contentSelector);
    if (!container) {
        // 如果容器还不存在，延迟重试
        setTimeout(observeContentChanges, 500);
        return;
    }

    // 使用 MutationObserver 监听内容变化
    contentObserver.value = new MutationObserver(() => {
        extractTOC();
    });

    contentObserver.value.observe(container, {
        childList: true,
        subtree: true
    });

    // 初始提取
    extractTOC();
};

onMounted(() => {
    observeContentChanges();
});

onUnmounted(() => {
    if (headingObserver.value) {
        headingObserver.value.disconnect();
    }
    if (contentObserver.value) {
        contentObserver.value.disconnect();
    }
});

// 暴露方法供外部调用
defineExpose({
    extractTOC,
    scrollToHeading
});
</script>

<style scoped>
.toc-panel {
    width: 100%;
    background: var(--theme-panel-bg);
    border-radius: 1rem;
    padding: 1.5rem;
    box-shadow: 0 4px 20px var(--theme-shadow-sm);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toc-panel:hover {
    box-shadow: 0 8px 30px var(--theme-shadow-md);
}

.toc-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--theme-content-border);
}

.toc-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--theme-content-text);
    margin: 0;
    letter-spacing: 0.5px;
}

.toc-toggle {
    width: 32px;
    height: 32px;
    border: none;
    background: var(--theme-gradient);
    color: var(--theme-button-text);
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.toc-toggle:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px var(--theme-primary);
}

.toc-toggle svg {
    width: 18px;
    height: 18px;
}

.toc-nav {
    overflow-y: auto;
    overflow-x: hidden;
    max-height: 60vh;
    padding-right: 0.5rem;
    scrollbar-width: thin;
    scrollbar-color: var(--theme-primary) transparent;
}

.toc-nav::-webkit-scrollbar {
    width: 4px;
}

.toc-nav::-webkit-scrollbar-track {
    background: transparent;
}

.toc-nav::-webkit-scrollbar-thumb {
    background: var(--theme-primary);
    border-radius: 2px;
}

.toc-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.toc-item {
    margin: 0.3rem 0;
    transition: all 0.2s ease;
}

.toc-link {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.5rem 0.8rem;
    text-decoration: none;
    color: var(--theme-meta-text);
    border-radius: 0.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.toc-link::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: var(--theme-gradient);
    transform: scaleY(0);
    transition: transform 0.3s ease;
}

.toc-link:hover {
    background: var(--theme-hover-bg);
    color: var(--theme-primary);
    transform: translateX(4px);
}

.toc-link:hover::before {
    transform: scaleY(1);
}

.toc-indicator {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--theme-meta-text);
    flex-shrink: 0;
    margin-top: 0.5rem;
    transition: all 0.3s ease;
}

.toc-text {
    flex: 1;
    font-size: 0.9rem;
    line-height: 1.5;
    word-break: break-word;
}

/* 目录层级缩进 */
.toc-level-2 {
    padding-left: 0;
}

.toc-level-3 {
    padding-left: 1rem;
}

.toc-level-3 .toc-text {
    font-size: 0.85rem;
}

.toc-level-4 {
    padding-left: 2rem;
}

.toc-level-4 .toc-text {
    font-size: 0.8rem;
    opacity: 0.9;
}

/* 活动状态 */
.toc-active .toc-link {
    background: linear-gradient(90deg,
            var(--theme-hover-bg) 0%,
            transparent 100%);
    color: var(--theme-primary);
    font-weight: 600;
}

.toc-active .toc-link::before {
    transform: scaleY(1);
}

.toc-active .toc-indicator {
    background: var(--theme-primary);
    transform: scale(1.3);
    box-shadow: 0 0 8px var(--theme-primary);
}

/* 空状态 */
.toc-empty {
    text-align: center;
    padding: 2rem 1rem;
    color: var(--theme-meta-text);
    font-size: 0.9rem;
}

.toc-empty p {
    margin: 0;
}

/* 折叠状态 */
.toc-collapsed .toc-header {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}
</style>
