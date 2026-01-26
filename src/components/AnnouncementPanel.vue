<template>
    <div class="announcement-panel" v-if="announcements.length > 0">
        <div class="panel-header">
            <div class="header-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M18 8A6 6 0 1 0 6 8c0 7-3 9-3 9h18s-3-2-3-9Z" stroke="currentColor" stroke-width="2"
                        stroke-linecap="round" stroke-linejoin="round" />
                    <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                        stroke-linejoin="round" />
                </svg>
            </div>
            <h2 class="panel-title">最新公告</h2>
            <div class="nav-indicators">
                <button v-for="(_, index) in announcements" :key="index" @click="goToAnnouncement(index)"
                    :class="['indicator', { active: currentIndex === index }]" :aria-label="`查看第${index + 1}条公告`">
                </button>
            </div>
        </div>

        <div class="announcements-container">
            <div class="cards-stack" :style="{ '--total': announcements.length }">
                <div v-for="(announcement, index) in announcements" :key="announcement.key" :class="[
                    'announcement-card',
                    {
                        'is-active': index === currentIndex,
                        'is-behind': index > currentIndex,
                        'is-past': index < currentIndex
                    }
                ]" :style="getCardStyle(index)" @click="handleCardClick(index, announcement)">
                    <!-- 图片背景（如果有） -->
                    <div v-if="announcement.imageUrl" class="card-image-bg"
                        :style="{ backgroundImage: `url(${announcement.imageUrl})` }">
                        <div class="image-overlay"></div>
                    </div>

                    <!-- 内容区域 -->
                    <div class="card-content">
                        <div class="card-badge">
                            <span class="badge-text">公告</span>
                            <span class="badge-number">#{{ announcements.length - index }}</span>
                        </div>

                        <h3 class="card-title" v-if="announcement.metadata.title">
                            {{ announcement.metadata.title }}
                        </h3>

                        <div class="card-meta">
                            <div class="meta-date" v-if="announcement.metadata.date">
                                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <rect x="3" y="6" width="18" height="15" rx="2" stroke="currentColor"
                                        stroke-width="2" />
                                    <path d="M3 10h18M7 3v4M17 3v4" stroke="currentColor" stroke-width="2"
                                        stroke-linecap="round" />
                                </svg>
                                <span>{{ formatDate(announcement.metadata.date) }}</span>
                            </div>
                            <div class="meta-category" v-if="announcement.metadata.categories">
                                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path
                                        d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"
                                        stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round" />
                                    <circle cx="7" cy="7" r="1" fill="currentColor" />
                                </svg>
                                <span>{{ announcement.metadata.categories[announcement.metadata.categories.length - 1]
                                    }}</span>
                            </div>
                        </div>

                        <p class="card-preview" v-if="announcement.metadata.pre">
                            {{ announcement.metadata.pre }}
                        </p>

                        <div class="card-actions">
                            <button class="action-btn primary" @click.stop="navigateToPost(announcement)">
                                查看详情
                                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2"
                                        stroke-linecap="round" stroke-linejoin="round" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- 卡片装饰 -->
                    <div class="card-corner"></div>
                </div>
            </div>

            <!-- 导航控制 -->
            <div class="nav-controls">
                <button class="nav-btn prev" @click="prevAnnouncement" :disabled="currentIndex === 0"
                    aria-label="上一条公告">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                            stroke-linejoin="round" />
                    </svg>
                </button>
                <button class="nav-btn next" @click="nextAnnouncement"
                    :disabled="currentIndex === announcements.length - 1" aria-label="下一条公告">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                            stroke-linejoin="round" />
                    </svg>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import globalVar from '@/globalVar';
import axios from 'axios';
import { parseMarkdownMetadata } from "@/utils";

const router = useRouter();
const currentIndex = ref(0);
const announcements = ref([]);

// 获取并解析带'公告'标签的文章
async function loadAnnouncements() {
    const allPosts = globalVar.markdowns;
    const announcementPosts = [];

    for (const [key, post] of Object.entries(allPosts)) {
        try {
            // 获取文章内容
            const response = await axios.get(key.startsWith('http') ? key : new URL(key, import.meta.url).href);
            const content = response.data;

            // 解析元数据
            const { meta } = await parseMarkdownMetadata(content);

            // 检查是否有'公告'标签
            if (meta.tags && (Array.isArray(meta.tags) ? meta.tags.includes('公告') : meta.tags === '公告')) {
                announcementPosts.push({
                    key,
                    imageUrl: post.imageUrl,
                    metadata: meta
                });
            }
        } catch (error) {
            console.error(`Failed to load announcement from ${key}:`, error);
        }
    }

    // 按日期排序（最新的在前）
    announcementPosts.sort((a, b) => {
        const dateA = new Date(a.metadata.date || 0);
        const dateB = new Date(b.metadata.date || 0);
        return dateB - dateA;
    });

    announcements.value = announcementPosts;
}

onMounted(() => {
    loadAnnouncements();
});

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '';
    return dateString.split(' ')[0]; // 移除时间部分
}

// 计算卡片样式
function getCardStyle(index) {
    const offset = index - currentIndex.value;
    if (offset < 0) {
        // 已浏览的卡片
        return {
            '--offset': offset,
            '--z-index': 0
        };
    } else {
        // 当前和未浏览的卡片
        return {
            '--offset': offset,
            '--z-index': announcements.value.length - index
        };
    }
}

// 处理卡片点击
function handleCardClick(index, announcement) {
    if (index === currentIndex.value) {
        navigateToPost(announcement);
    } else if (index > currentIndex.value) {
        goToAnnouncement(index);
    }
}

// 导航到文章页面
function navigateToPost(announcement) {
    const urlParts = announcement.key.split('/').filter(part => part);
    const mdName = urlParts[urlParts.length - 1].replace('.md', '');
    const collection = urlParts.length > 2 ? urlParts[1] : null;

    router.push({
        name: 'PostPage',
        params: { collection, mdName }
    });
}

// 导航控制
function prevAnnouncement() {
    if (currentIndex.value > 0) {
        currentIndex.value--;
    }
}

function nextAnnouncement() {
    if (currentIndex.value < announcements.value.length - 1) {
        currentIndex.value++;
    }
}

function goToAnnouncement(index) {
    currentIndex.value = index;
}
</script>

<style scoped>
.announcement-panel {
    width: 100%;
    margin: 2rem auto;
    padding: 0;
}

/* === 头部 === */
.panel-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
    padding: 0 1rem;
}

.header-icon {
    width: 2.5rem;
    height: 2.5rem;
    background: var(--theme-gradient);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--theme-button-text);
    animation: pulse 2s ease-in-out infinite;
}

.header-icon svg {
    width: 1.5rem;
    height: 1.5rem;
}

@keyframes pulse {

    0%,
    100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.05);
    }
}

.panel-title {
    font-family: 'Noto Serif SC', 'Source Han Serif SC', serif;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
    background: var(--theme-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.nav-indicators {
    display: flex;
    gap: 0.5rem;
    margin-left: auto;
}

.indicator {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    border: none;
    background: var(--theme-primary-disabled);
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 0;
}

.indicator:hover {
    background: var(--theme-primary-hover);
    transform: scale(1.2);
}

.indicator.active {
    width: 24px;
    border-radius: 4px;
    background: var(--theme-gradient);
}

/* === 公告容器 === */
.announcements-container {
    position: relative;
    width: 100%;
    min-height: 400px;
}

.cards-stack {
    position: relative;
    width: 100%;
    height: 400px;
    perspective: 1000px;
}

/* === 公告卡片 === */
.announcement-card {
    position: absolute;
    width: 100%;
    height: 100%;
    background: var(--theme-panel-bg);
    backdrop-filter: blur(20px) saturate(180%);
    border-radius: 20px;
    box-shadow:
        0 10px 40px var(--theme-shadow-lg),
        0 0 0 1px var(--theme-border-light);
    overflow: hidden;
    cursor: pointer;
    transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    transform-origin: center center;
    z-index: var(--z-index);
}

/* 当前卡片 */
.announcement-card.is-active {
    transform: translateY(0) scale(1) rotateY(0deg);
    opacity: 1;
}

/* 后面的卡片（层叠效果） */
.announcement-card.is-behind {
    transform:
        translateY(calc(var(--offset) * 15px)) scale(calc(1 - var(--offset) * 0.05)) translateZ(calc(var(--offset) * -50px));
    opacity: 0.8;
    pointer-events: auto;
}

.announcement-card.is-behind:hover {
    transform:
        translateY(calc(var(--offset) * 15px - 5px)) scale(calc(1 - var(--offset) * 0.05 + 0.02)) translateZ(calc(var(--offset) * -50px));
}

/* 已浏览的卡片（滑出左侧） */
.announcement-card.is-past {
    transform:
        translateX(-120%) scale(0.9) rotateY(-15deg);
    opacity: 0;
    pointer-events: none;
}

/* 当前卡片悬停效果 */
.announcement-card.is-active:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow:
        0 20px 60px var(--theme-shadow-xl),
        0 0 0 1px var(--theme-border-medium);
}

/* === 卡片内容 === */
.card-image-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
    opacity: 0.15;
}

.image-overlay {
    position: absolute;
    inset: 0;
    background: var(--theme-gradient);
    opacity: 0.4;
}

.card-content {
    position: relative;
    z-index: 1;
    height: 100%;
    padding: 2rem;
    display: flex;
    flex-direction: column;
}

.card-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: var(--theme-gradient);
    border-radius: 20px;
    color: var(--theme-button-text);
    font-size: 0.85rem;
    font-weight: 600;
    align-self: flex-start;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px var(--theme-shadow-md);
}

.badge-text {
    letter-spacing: 0.5px;
}

.badge-number {
    opacity: 0.8;
}

.card-title {
    font-family: 'Noto Serif SC', 'Source Han Serif SC', serif;
    font-size: 1.8rem;
    font-weight: 700;
    line-height: 1.3;
    margin: 0 0 1rem 0;
    color: var(--theme-heading-text);
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    overflow: hidden;
}

.card-meta {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.meta-date,
.meta-category {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.9rem;
    color: var(--theme-meta-text);
}

.meta-date svg,
.meta-category svg {
    width: 1rem;
    height: 1rem;
    opacity: 0.7;
}

.card-preview {
    flex: 1;
    font-size: 1rem;
    line-height: 1.7;
    color: var(--theme-content-text);
    margin: 0 0 1.5rem 0;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    overflow: hidden;
}

.card-actions {
    display: flex;
    gap: 1rem;
}

.action-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: none;
}

.action-btn.primary {
    background: var(--theme-gradient);
    color: var(--theme-button-text);
    box-shadow: 0 4px 12px var(--theme-shadow-md);
}

.action-btn.primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px var(--theme-shadow-lg);
}

.action-btn svg {
    width: 1rem;
    height: 1rem;
}

/* 卡片装饰 */
.card-corner {
    position: absolute;
    top: 0;
    right: 0;
    width: 150px;
    height: 150px;
    background: var(--theme-gradient);
    opacity: 0.05;
    border-radius: 0 20px 0 100%;
    pointer-events: none;
}

/* === 导航控制 === */
.nav-controls {
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    transform: translateY(-50%);
    display: flex;
    justify-content: space-between;
    padding: 0 1rem;
    pointer-events: none;
    z-index: 10;
}

.nav-btn {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    border: none;
    background: var(--theme-surface-default);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px var(--theme-shadow-md);
    color: var(--theme-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: auto;
}

.nav-btn:hover:not(:disabled) {
    background: var(--theme-gradient);
    color: var(--theme-button-text);
    transform: scale(1.1);
    box-shadow: 0 6px 20px var(--theme-shadow-lg);
}

.nav-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
}

.nav-btn svg {
    width: 1.5rem;
    height: 1.5rem;
}

/* === 响应式 === */
@media (max-width: 768px) {
    .announcement-panel {
        margin: 1rem auto;
    }

    .panel-header {
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .panel-title {
        font-size: 1.5rem;
    }

    .nav-indicators {
        width: 100%;
        justify-content: center;
        margin: 0.5rem 0 0 0;
    }

    .cards-stack {
        height: 450px;
    }

    .card-content {
        padding: 1.5rem;
    }

    .card-title {
        font-size: 1.5rem;
    }

    .nav-btn {
        width: 40px;
        height: 40px;
    }
}
</style>
