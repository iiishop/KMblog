<template>
    <div class="collections-page" :class="{ 'detail-open': selectedCollection }">
        <!-- Head Menu -->
        <HeadMenu />

        <!-- Hero Header -->
        <header class="gallery-header" :class="{ 'header-hidden': selectedCollection }">
            <h1 class="gallery-title">Archive Gallery</h1>
            <p class="gallery-subtitle">A curated collection of thoughts and memories</p>
        </header>

        <!-- 背景色填充层 -->
        <div class="color-fill" ref="colorFillRef"></div>

        <!-- 展开的Collection图片或纯色背景 -->
        <div v-if="expandedImage !== false" class="expanded-image" ref="expandedImageRef">
            <img v-if="expandedImage" :src="expandedImage" alt="Expanded collection" />
        </div>

        <!-- 展开的Collection信息（临时过渡用） -->
        <div v-if="expandedInfo" class="expanded-info" ref="expandedInfoRef" :style="expandedInfo.style">
            <div class="card-info">
                <h3 class="card-title">{{ expandedInfo.name }}</h3>
                <div class="card-meta">
                    <span class="card-date">{{ expandedInfo.date }}</span>
                    <span class="card-count">{{ expandedInfo.count }} items</span>
                </div>
            </div>
        </div>

        <!-- 半圆环容器 -->
        <div class="carousel-container" ref="carouselContainer">
            <div class="carousel-track" ref="carouselTrack">
                <div v-for="(collection, name, index) in collections" :key="name" :ref="el => collectionRefs[name] = el"
                    class="collection-item" :class="{
                        'active': activeIndex === index,
                        'selected': selectedCollection === name,
                        'hidden': selectedCollection && selectedCollection !== name
                    }" :style="getItemStyle(index)" @click="handleCollectionClick(name, collection, index)">
                    <div class="collection-card" :style="{ backgroundColor: collection.bgColor }">
                        <div class="card-image" v-if="collection.image">
                            <img :src="collection.image" :alt="name" />
                        </div>
                        <div class="card-info">
                            <h3 class="card-title">{{ name }}</h3>
                            <div class="card-meta">
                                <span class="card-date">{{ collection.date }}</span>
                                <span class="card-count">{{ collection.count }} 篇</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 导航提示 -->
            <div class="navigation-hint" v-if="!selectedCollection">
                <button class="nav-arrow nav-left" @click="scrollCarousel(-1)" :disabled="activeIndex === 0">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="15,18 9,12 15,6"></polyline>
                    </svg>
                </button>
                <button class="nav-arrow nav-right" @click="scrollCarousel(1)"
                    :disabled="activeIndex === collectionsArray.length - 1">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="9,18 15,12 9,6"></polyline>
                    </svg>
                </button>
            </div>
        </div>

        <!-- 文章列表侧边栏 -->
        <transition name="sidebar">
            <div v-if="showSidebar" class="articles-sidebar" ref="sidebarRef">
                <div class="sidebar-header">
                    <button class="close-btn" @click="closeDetail">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 6L6 18M6 6l12 12" />
                        </svg>
                    </button>
                    <h2>{{ selectedCollection }}</h2>
                    <p class="sidebar-subtitle">{{ articles.length }} 篇文章</p>
                </div>

                <div class="articles-list">
                    <TransitionGroup name="article-item" appear>
                        <article v-for="(article, index) in articles" :key="article.id" class="article-item"
                            :style="{ '--index': index }" @click="navigateToArticle(article)">
                            <div class="article-content">
                                <h3 class="article-title">{{ article.title }}</h3>
                                <p v-if="article.pre" class="article-preview">{{ article.pre }}</p>
                                <div class="article-meta">
                                    <time class="article-date">{{ article.date }}</time>
                                    <div v-if="article.tags && article.tags.length" class="article-tags">
                                        <span v-for="tag in article.tags.slice(0, 3)" :key="tag" class="tag">
                                            {{ tag }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </article>
                    </TransitionGroup>
                </div>
            </div>
        </transition>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import globalVar from '@/globalVar.js';
import { parseMarkdownMetadata } from '@/utils.js';
import axios from 'axios';
import { animate, createTimeline } from 'animejs';
import HeadMenu from '@/components/HeadMenu.vue';

const router = useRouter();
const route = useRoute();

// 数据
const collections = ref({});
const collectionsArray = computed(() => Object.entries(collections.value));
const activeIndex = ref(0);
const selectedCollection = ref(null);
const selectedCollectionData = ref(null);
const articles = ref([]);
const collectionRefs = ref({});
const expandedImage = ref(false); // false=未展开, null=无图片展开, string=有图片展开
const expandedInfo = ref(null); // 存储展开时的临时信息
const showSidebar = ref(false);
const clickedElementRef = ref(null); // 保存被点击的元素，用于关闭动画

// DOM引用
const carouselContainer = ref(null);
const carouselTrack = ref(null);
const colorFillRef = ref(null);
const sidebarRef = ref(null);
const expandedImageRef = ref(null);
const expandedInfoRef = ref(null);

// 生成随机纯色背景
const generateRandomColor = () => {
    const hue = Math.floor(Math.random() * 360);
    const saturation = 50 + Math.floor(Math.random() * 30); // 50-80%
    const lightness = 45 + Math.floor(Math.random() * 20); // 45-65%
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
};

// 监听路由query变化，自动打开指定Collection
watch(() => route.query.open, async (collectionName) => {
    if (collectionName && collections.value[collectionName]) {
        console.log('[CollectionsPage] Auto-opening collection from URL:', collectionName);
        await nextTick();

        // 找到该Collection的索引
        const index = collectionsArray.value.findIndex(([name]) => name === collectionName);
        if (index !== -1) {
            const collectionData = collections.value[collectionName];

            await new Promise(resolve => setTimeout(resolve, 10000));
            await nextTick();
            // 先设置activeIndex到目标位置，让卡片focus
            activeIndex.value = index;
            console.log('[CollectionsPage] Focused to collection:', collectionName, 'index:', index);

            // 等待1秒后执行展开动画
            await new Promise(resolve => setTimeout(resolve, 1000));
            await nextTick();

            // 使用forceExpand=true强制展开，跳过滚动检查
            console.log('[CollectionsPage] Expanding collection after 1s delay');
            handleCollectionClick(collectionName, collectionData, index, true);
        }
    }
}); // 移除immediate: true，改为在onMounted中手动触发

// 计算Collection位置样式（半圆环）- 从左下到右下的弧形
const getItemStyle = (index) => {
    const total = collectionsArray.value.length;
    const diff = index - activeIndex.value;

    // 半圆弧形布局：以activeIndex为中心(0°)，向两边展开
    // 左边为负角度，右边为正角度，形成半圆弧
    const maxSpread = 120; // 最大展开角度（左右各60度）
    const anglePerItem = total > 1 ? maxSpread / (total - 1) : 0;

    // 当前卡片相对于激活卡片的角度偏移
    const relativeAngle = diff * (anglePerItem / (total - 1)) * total / 2;

    // 半圆参数
    const radius = 650; // 半圆半径
    const centerY = -100; // 圆心Y轴偏移（向上抬高，使底部形成弧线）

    // 极坐标转换：0°在底部中心，负角度向左，正角度向右
    const angle = relativeAngle;
    const x = Math.sin((angle * Math.PI) / 180) * radius;
    const y = (1 - Math.cos((angle * Math.PI) / 180)) * radius + centerY;

    // Z轴深度：激活的卡片最靠前(正值)，其他卡片在基准平面(0)
    // 使用正值避免卡片"在屏幕后面"导致无法点击
    const z = diff === 0 ? 200 : 0;

    // 缩放：激活的最大，两边逐渐缩小
    const scale = diff === 0 ? 1 : Math.max(0.65 - Math.abs(diff) * 0.08, 0.4);

    // 透明度：激活的完全不透明，远离的逐渐透明
    const opacity = diff === 0 ? 1 : Math.max(0.6 - Math.abs(diff) * 0.15, 0.2);

    // 旋转：根据弧线位置轻微旋转卡片
    const rotateY = diff * 8;

    return {
        // 直接设置left/top为最终位置（确保点击检测准确）
        left: `calc(50% + ${x}px)`,
        top: `calc(50% + ${y}px)`,
        // item只使用translateZ和scale，不旋转（确保点击区域准确）
        transform: `translateZ(${z}px) scale(${scale})`,
        opacity: opacity,
        zIndex: 1000 - Math.abs(diff) * 100,
        // 将rotateY作为CSS变量传递给card
        '--card-rotate-y': `${rotateY}deg`,
    };
};

// 滚动轮播
const scrollCarousel = (direction) => {
    const newIndex = activeIndex.value + direction;
    if (newIndex >= 0 && newIndex < collectionsArray.value.length) {
        activeIndex.value = newIndex;

        // 使用anime.js平滑过渡
        animate('.collection-item', {
            duration: 600,
            easing: 'out-quad'
        });
    }
};

// 提取图片对比色
const extractContrastColor = async (imageUrl) => {
    return new Promise((resolve) => {
        const img = new Image();
        img.crossOrigin = 'Anonymous';

        img.onload = () => {
            try {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);

                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                let r = 0, g = 0, b = 0, count = 0;

                // 采样计算平均色
                for (let i = 0; i < imageData.length; i += 40) {
                    if (imageData[i + 3] > 0) { // 非透明
                        r += imageData[i];
                        g += imageData[i + 1];
                        b += imageData[i + 2];
                        count++;
                    }
                }

                r = Math.round(r / count);
                g = Math.round(g / count);
                b = Math.round(b / count);

                resolve(`rgb(${r}, ${g}, ${b})`);
            } catch (error) {
                console.warn('Cannot extract color (CORS):', error);
                resolve('rgb(102, 126, 234)');
            }
        };

        img.onerror = () => resolve('rgb(102, 126, 234)');
        img.src = imageUrl;
    });
};

// 点击Collection展开
const handleCollectionClick = async (name, collection, index, forceExpand = false) => {
    console.log('点击Collection:', name, 'index:', index, 'activeIndex:', activeIndex.value);

    if (selectedCollection.value) {
        console.log('已有展开的Collection，忽略点击');
        return;
    }

    // 如果点击的不是当前激活的Collection，先滚动到该Collection（除非forceExpand=true）
    if (!forceExpand && activeIndex.value !== index) {
        console.log('点击的不是激活项，开始滚动到index:', index);
        // 平滑滚动到目标Collection
        const scrollSteps = Math.abs(index - activeIndex.value);
        const scrollDuration = Math.min(scrollSteps * 150, 800); // 最多800ms

        activeIndex.value = index;
        console.log('滚动时间:', scrollDuration, 'ms');

        // 等待滚动动画完成
        await new Promise(resolve => setTimeout(resolve, scrollDuration));
        await nextTick();
        console.log('滚动完成，需要再次点击以展开');
        return; // 滚动后不立即展开，需要再次点击
    }

    console.log('当前已是激活状态，开始执行展开动画');
    // 当前已经是激活状态，执行展开动画
    await nextTick();

    const clickedElement = collectionRefs.value[name];
    if (!clickedElement) return;

    // 保存到ref供closeDetail使用
    clickedElementRef.value = clickedElement;

    selectedCollection.value = name;
    selectedCollectionData.value = collection;

    // 确保Collection有背景色（图片或随机纯色）
    if (!collection.bgColor) {
        collection.bgColor = collection.image ? 'transparent' : generateRandomColor();
    }

    const card = clickedElement.querySelector('.collection-card');
    const cardImgEl = card.querySelector('.card-image');
    const cardInfoEl = card.querySelector('.card-info');

    const cardRect = card.getBoundingClientRect();
    const infoRect = cardInfoEl.getBoundingClientRect();

    // 准备展开的图片/背景
    let imageRect;
    if (collection.image && cardImgEl) {
        expandedImage.value = collection.image;
        imageRect = cardImgEl.getBoundingClientRect();
    } else {
        expandedImage.value = null; // 表示纯色
        imageRect = cardRect;
    }

    // 准备展开的信息
    expandedInfo.value = {
        name: name,
        date: collection.date,
        count: collection.count,
        style: {
            position: 'fixed',
            left: `${infoRect.left}px`,
            top: `${infoRect.top}px`,
            width: `${infoRect.width}px`,
            height: `${infoRect.height}px`,
            zIndex: '152', // 高于 expandedImage
            opacity: 1
        }
    };

    // 设置此时ExpandedImage的初始状态 (Fixed Overlay)
    await nextTick();
    const expImg = expandedImageRef.value;
    const expInfo = expandedInfoRef.value;

    expImg.style.position = 'fixed';
    expImg.style.left = `${imageRect.left}px`;
    expImg.style.top = `${imageRect.top}px`;
    expImg.style.width = `${imageRect.width}px`;
    expImg.style.height = `${imageRect.height}px`;
    expImg.style.zIndex = '151'; // 高于 ColorFill
    expImg.style.background = collection.bgColor; // 如果无图片，应用背景色

    if (collection.image && cardImgEl) {
        expImg.style.borderRadius = '20px 20px 0 0';
    } else {
        expImg.style.borderRadius = '20px';
    }

    // 隐藏原始元素 (视觉替换)
    clickedElement.style.opacity = '0';

    // 提取对比色（反色）
    let contrastColor = 'var(--theme-primary)';
    if (collection.image) {
        const avgColor = await extractContrastColor(collection.image);
        const match = avgColor.match(/rgb\((\d+), (\d+), (\d+)\)/);
        if (match) {
            const [, r, g, b] = match.map(Number);
            contrastColor = `rgb(${255 - r}, ${255 - g}, ${255 - b})`;
        }
    } else {
        const bgColor = collection.bgColor;
        if (bgColor.startsWith('hsl')) {
            const match = bgColor.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
            if (match) {
                const [, h, s, l] = match.map(Number);
                contrastColor = `hsl(${(parseInt(h) + 180) % 360}, ${s}%, ${100 - l}%)`;
            }
        }
    }

    // 阶段1：从左向右滑入对比色背景（0.2s）
    // 覆盖除了被点击的块以外的内容 -> zIndex 100 (below expanded elements)
    const colorFill = colorFillRef.value;
    colorFill.style.background = contrastColor;
    colorFill.style.left = '0';
    colorFill.style.top = '0';
    colorFill.style.width = '0';
    colorFill.style.height = '100vh';
    colorFill.style.display = 'block';
    colorFill.style.zIndex = '100';

    await animate(colorFill, {
        width: '100vw',
        duration: 300,
        easing: 'outQuart'
    });

    // 阶段2：Collection信息向内折叠消失（0.25s）
    await animate(expInfo, {
        opacity: 0,
        scale: 0.9,
        duration: 250,
        easing: 'inCubic'
    });

    // 阶段3：图片放大并移动到屏幕中心（0.6s流畅动画）
    // 目标尺寸 height:70vh; width:50vw;
    // 居中位置: left: 25vw, top: 15vh
    await animate(expImg, {
        left: '25vw',
        top: '15vh',
        width: '50vw',
        height: '70vh',
        borderRadius: '20px', // 最终变为统一圆角
        duration: 600,
        easing: 'outExpo'
    });

    // 阶段4：图片向左移动，右侧滑出文章列表（0.5s）
    await loadArticles(name);

    await Promise.all([
        animate(expImg, {
            left: '5vw',
            width: '40vw',
            duration: 500,
            easing: 'outCubic'
        }),
        new Promise(resolve => {
            showSidebar.value = true;
            setTimeout(resolve, 500);
        })
    ]);
};

// 加载文章列表
const loadArticles = async (collectionName) => {
    try {
        const postDirResponse = await axios.get('/assets/PostDirectory.json');
        const postDirectory = postDirResponse.data;

        if (postDirectory[collectionName] && postDirectory[collectionName].Markdowns) {
            const markdownPaths = postDirectory[collectionName].Markdowns;

            const articlePromises = markdownPaths.map(async (item) => {
                try {
                    const response = await axios.get(item.path);
                    const metadata = await parseMarkdownMetadata(response.data);

                    return {
                        id: item.id,
                        path: item.path,
                        title: metadata.meta?.title || metadata.title || '无标题',
                        date: metadata.meta?.date || metadata.date || '',
                        pre: metadata.meta?.pre || metadata.pre || '',
                        tags: metadata.meta?.tags || metadata.tags || [],
                    };
                } catch (error) {
                    console.error(`Failed to load article: ${item.path}`, error);
                    return null;
                }
            });

            const loadedArticles = await Promise.all(articlePromises);
            articles.value = loadedArticles.filter(a => a !== null)
                .sort((a, b) => new Date(b.date) - new Date(a.date));
        }
    } catch (error) {
        console.error('Error loading articles:', error);
    }
};

// 关闭详情
const closeDetail = async () => {
    if (!selectedCollection.value || !expandedImageRef.value) return;

    console.log('开始关闭动画');

    try {
        // 阶段1：隐藏侧边栏（0.4s）
        console.log('阶段1：隐藏侧边栏');
        showSidebar.value = false;
        await new Promise(resolve => setTimeout(resolve, 400));

        // 阶段2：图片从左边回到中心（0.4s）
        console.log('阶段2：图片回到中心');
        const expandedImg = expandedImageRef.value;
        if (!expandedImg) {
            console.error('expandedImg not found');
            return;
        }

        console.log('当前图片位置:', expandedImg.style.left, expandedImg.style.width);

        await animate(expandedImg, {
            left: '25vw',
            width: '50vw',
            duration: 400,
            easing: 'inOutCubic'
        });

        console.log('阶段2完成，图片已回到中心');
        await new Promise(resolve => setTimeout(resolve, 50)); // 稍微等待确保动画完成

        // 阶段3：图片缩小回到原始卡片位置（0.5s）
        console.log('阶段3：图片缩小回原位');

        if (!clickedElementRef.value) {
            console.error('clickedElementRef not found');
            return;
        }

        const card = clickedElementRef.value.querySelector('.collection-card');
        const cardImgEl = card?.querySelector('.card-image');
        const cardInfoEl = card?.querySelector('.card-info');

        if (!card) {
            console.error('card not found');
            return;
        }

        // 获取目标位置
        let targetRect;
        let targetRadius = '20px';

        if (cardImgEl && expandedImage.value) {
            targetRect = cardImgEl.getBoundingClientRect();
            targetRadius = '20px 20px 0 0';
        } else {
            targetRect = card.getBoundingClientRect();
        }

        console.log('目标位置:', targetRect);
        console.log('开始阶段3动画，从', expandedImg.style.left, '到', targetRect.left + 'px');

        await animate(expandedImg, {
            left: `${targetRect.left}px`,
            top: `${targetRect.top}px`,
            width: `${targetRect.width}px`,
            height: `${targetRect.height}px`,
            borderRadius: targetRadius,
            duration: 500,
            easing: 'inExpo'
        });

        console.log('阶段3完成，图片已缩小回原位');
        await new Promise(resolve => setTimeout(resolve, 50));
        // 阶段4：文字信息重新展开（0.2s）并恢复原始卡片
        console.log('阶段4：文字信息重新展开');
        clickedElementRef.value.style.opacity = '1';

        if (cardInfoEl) {
            cardInfoEl.style.display = 'flex';
            await animate(cardInfoEl, {
                opacity: [0, 1],
                scale: [0.9, 1],
                duration: 200,
                easing: 'outQuad'
            });
            console.log('文字信息展开完成');
        }

        await new Promise(resolve => setTimeout(resolve, 50));

        // 阶段5：背景色从右向左消失（0.25s）
        console.log('阶段5：背景色消失');
        if (colorFillRef.value) {
            await animate(colorFillRef.value, {
                width: '0',
                duration: 250,
                easing: 'inQuart'
            });

            colorFillRef.value.style.display = 'none';
            console.log('背景色消失完成');
        }


        console.log('关闭动画完成');
    } catch (error) {
        console.error('Close animation error:', error);
    } finally {
        // 最终清理状态（所有动画完成后才清理）
        expandedImage.value = false;
        expandedInfo.value = null;
        selectedCollection.value = null;
        selectedCollectionData.value = null;
        articles.value = [];
        clickedElementRef.value = null;
    }
};



// 导航到文章
const navigateToArticle = (article) => {
    const parts = article.path.replace(/^\//, '').split('/');
    let collection = null;
    let filename = '';

    if (parts.length >= 3) {
        collection = parts[1];
        filename = parts[2];
    } else if (parts.length === 2) {
        filename = parts[1];
    }

    const mdName = filename.replace('.md', '');

    if (collection) {
        router.push({ name: 'PostPage', params: { collection, mdName } });
    } else {
        router.push({ name: 'PostPage', params: { mdName } });
    }
};

// 键盘导航
const handleKeydown = (e) => {
    if (selectedCollection.value) return;

    if (e.key === 'ArrowLeft') {
        scrollCarousel(-1);
    } else if (e.key === 'ArrowRight') {
        scrollCarousel(1);
    } else if (e.key === 'Enter' && collectionsArray.value[activeIndex.value]) {
        const [name, collection] = collectionsArray.value[activeIndex.value];
        handleCollectionClick(name, collection, activeIndex.value);
    }
};

onMounted(() => {
    collections.value = globalVar.collections;

    // 为每个Collection生成随机背景色（如果没有图片）
    Object.values(collections.value).forEach(collection => {
        if (!collection.image) {
            collection.bgColor = generateRandomColor();
        }
    });

    document.addEventListener('keydown', handleKeydown);

    // 检查URL中是否有要自动打开的Collection
    const collectionName = route.query.open;
    if (collectionName && collections.value[collectionName]) {
        console.log('[CollectionsPage] Initial auto-open from URL:', collectionName);
        (async () => {
            await nextTick();
            const index = collectionsArray.value.findIndex(([name]) => name === collectionName);
            if (index !== -1) {
                const collectionData = collections.value[collectionName];

                // 先设置activeIndex到目标位置
                activeIndex.value = index;
                console.log('[CollectionsPage] Focused to collection:', collectionName, 'index:', index);

                // 等待600ms让画廊入场动画完成，再等待200ms执行focus动画
                console.log('[CollectionsPage] Waiting 800ms...');
                await new Promise(resolve => setTimeout(resolve, 800));
                await nextTick();

                console.log('[CollectionsPage] Expanding collection');
                handleCollectionClick(collectionName, collectionData, index, true);
            }
        })();
    }
});

onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
/* 
  === Collections Gallery Theme ===
  Aesthetics: Minimalist, Immersive, Organic Motion
*/

.collections-page {
    position: fixed;
    inset: 0;
    background: var(--theme-body-bg);
    overflow: hidden;
    perspective: 2500px;
    perspective-origin: 50% 50%;
    font-family: var(--gallery-font-body);
}

/* 当展开详情时，隐藏HeadMenu */
.collections-page.detail-open :deep(.header-menu) {
    transform: translateY(-120%);
    opacity: 0;
    pointer-events: none;
    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1),
        opacity 0.6s ease;
}

/* Header Typography */
.gallery-header {
    position: absolute;
    top: calc(80px + 4vh);
    /* 为HeadMenu留出空间 */
    left: 8vw;
    z-index: 10;
    transition: opacity 0.6s var(--ease-organic), transform 0.6s var(--ease-organic);
}

.header-hidden {
    opacity: 0;
    transform: translateY(-20px);
    pointer-events: none;
}

.gallery-title {
    font-family: var(--gallery-font-hero);
    font-size: var(--gallery-hero-size);
    font-weight: var(--gallery-hero-weight);
    letter-spacing: var(--gallery-hero-letter-spacing);
    color: var(--theme-heading-text);
    margin: 0;
    line-height: 1;
    background: linear-gradient(135deg, var(--theme-heading-text) 0%, var(--theme-meta-text) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    transform-origin: left;
}

.gallery-subtitle {
    font-family: var(--gallery-font-mono);
    font-size: var(--gallery-meta-size);
    letter-spacing: var(--gallery-meta-letter-spacing);
    color: var(--theme-meta-text);
    margin-top: 1rem;
    text-transform: uppercase;
    opacity: 0.7;
}

/* Color Fill Layer */
.color-fill {
    position: fixed;
    display: none;
    z-index: 50;
    /* border-radius via js */
}

/* Expanded Image View */
.expanded-image {
    position: fixed;
    z-index: 150;
    overflow: hidden;
    box-shadow: 0 40px 100px rgba(0, 0, 0, 0.5);
    pointer-events: auto;
    /* 允许交互 */
    /* Heavier shadow for impact */
    /* Border radius handled by JS animation */
}

.expanded-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

/* Expanded Info Ghost Element */
.expanded-info {
    background: var(--theme-panel-bg);
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    pointer-events: none;
    border-radius: 0 0 20px 20px;
    overflow: hidden;
    /* Matches card-info styles but positioned fixed */
}

/* Carousel 3D Container */
.carousel-container {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: calc(70vh - 40px);
    /* 减去HeadMenu高度 */
    display: flex;
    align-items: flex-end;
    justify-content: center;
    transform-style: preserve-3d;
    padding-bottom: 5vh;
}

.carousel-track {
    position: relative;
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;
}

/* Collection Item Wrapper */
.collection-item {
    position: absolute;
    width: 380px;
    /* Slightly wider */
    height: 520px;
    /* Taller golden ratio */
    margin-left: -190px;
    margin-top: -260px;
    /* 移除 transform-style: preserve-3d 以修复点击检测问题 */
    transition: left 1s cubic-bezier(0.34, 1.56, 0.64, 1),
        top 1s cubic-bezier(0.34, 1.56, 0.64, 1),
        transform 1s cubic-bezier(0.34, 1.56, 0.64, 1),
        opacity 0.8s ease;
    cursor: pointer;
    will-change: left, top, transform, opacity;
    isolation: isolate;
    /* 创建独立的层叠上下文，确保z-index生效 */
}

.collection-item.hidden {
    pointer-events: none;
}

.collection-item.active {
    z-index: 200 !important;
}

/* The Card Itself */
.collection-card {
    width: 100%;
    height: 100%;
    background: var(--theme-panel-bg);
    border-radius: 20px;
    /* Should match JS logic */
    overflow: hidden;
    box-shadow: 0 15px 40px var(--theme-shadow-xl);
    border: 1px solid rgba(255, 255, 255, 0.05);
    /* Subtle rim */
    transition: all 0.4s var(--ease-organic);
    transform-origin: center center;
    display: flex;
    flex-direction: column;
    /* 应用rotateY旋转，提供3D视觉效果 */
    transform: rotateY(var(--card-rotate-y, 0deg));
    transform-style: preserve-3d;
}

.collection-item:hover .collection-card {
    transform: translateY(-15px) scale(1.02);
    box-shadow: 0 30px 60px var(--theme-shadow-xl);
}

.collection-item.active .collection-card {
    box-shadow: 0 25px 50px var(--theme-shadow-xl), 0 0 0 1px var(--theme-primary);
}

/* Card Image Area */
.card-image {
    width: 100%;
    height: 75%;
    /* More image focus */
    overflow: hidden;
    position: relative;
}

.card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.8s var(--ease-fluid);
}

.collection-item:hover .card-image img {
    transform: scale(1.05);
}

/* Card Info Area */
.card-info {
    flex: 1;
    padding: 1.5rem;
    background: var(--theme-panel-bg);
    display: flex;
    flex-direction: column;
    justify-content: center;
    backdrop-filter: blur(20px);
    position: relative;
}

/* Text-only Cards */
.collection-card:not(:has(.card-image)) .card-info {
    height: 100%;
    align-items: center;
    text-align: center;
}

/* Typography inside Card */
.card-title {
    font-family: var(--gallery-font-hero);
    font-size: 1.75rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: var(--theme-heading-text);
    line-height: 1.2;
}

.card-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: var(--gallery-font-mono);
    font-size: 0.8rem;
    color: var(--theme-meta-text);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    width: 100%;
    margin-top: auto;
}

.card-date {
    opacity: 0.7;
}

.card-count {
    font-weight: 600;
    color: var(--theme-primary);
}

/* Navigation Controls - Minimalist */
.navigation-hint {
    position: fixed;
    bottom: 8vh;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 4rem;
    z-index: 100;
    pointer-events: none;
    /* 不阻挡卡片点击 */
}

.nav-arrow {
    width: 60px;
    height: 60px;
    background: transparent;
    border: 1px solid var(--theme-border-medium);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s var(--ease-bounce);
    color: var(--theme-body-text);
    pointer-events: auto;
    /* 按钮本身可点击 */
}

.nav-arrow:not(:disabled):hover {
    border-color: var(--theme-primary);
    color: var(--theme-primary);
    transform: scale(1.1);
}

.nav-arrow:disabled {
    opacity: 0.2;
    cursor: not-allowed;
    border-color: transparent;
}

.nav-arrow svg {
    width: 20px;
    height: 20px;
}

/* Sidebar - Magazine Layout */
.articles-sidebar {
    position: fixed;
    right: 0;
    top: 0;
    bottom: 0;
    width: 45vw;
    /* Much wider for reading */
    max-width: 800px;
    background: var(--theme-panel-bg);
    box-shadow: -20px 0 60px rgba(0, 0, 0, 0.1);
    z-index: 100;
    display: flex;
    flex-direction: column;
    border-left: 1px solid var(--theme-border-light);
    backdrop-filter: blur(40px);
}

.sidebar-header {
    padding: 4rem;
    padding-bottom: 2rem;
    position: relative;
}

/* Close Button - Top Right */
.close-btn {
    position: absolute;
    top: 2rem;
    right: 2rem;
    width: 48px;
    height: 48px;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.4s var(--ease-organic);
}

.close-btn:hover {
    border-color: var(--theme-border-medium);
    transform: rotate(90deg);
}

.sidebar-header h2 {
    font-family: var(--gallery-font-hero);
    font-size: 3.5rem;
    font-weight: 700;
    margin: 0;
    line-height: 1;
    color: var(--theme-heading-text);
    margin-bottom: 0.5rem;
}

.sidebar-subtitle {
    font-family: var(--gallery-font-mono);
    color: var(--theme-meta-text);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.articles-list {
    flex: 1;
    overflow-y: auto;
    padding: 0 4rem 4rem 4rem;
}

/* Individual Article Item - Minimalist List */
.article-item {
    background: transparent;
    border-bottom: 1px solid var(--theme-border-light);
    padding: 2rem 0;
    cursor: pointer;
    transition: all 0.3s ease;
    group: article;
}

.article-item:last-child {
    border-bottom: none;
}

.article-item:hover .article-title {
    color: var(--theme-primary);
    transform: translateX(10px);
}

.article-title {
    font-family: var(--gallery-font-hero);
    font-size: 1.8rem;
    font-weight: 500;
    margin: 0 0 1rem 0;
    color: var(--theme-heading-text);
    transition: transform 0.3s ease, color 0.3s ease;
}

.article-preview {
    font-family: var(--gallery-font-body);
    font-size: 1rem;
    line-height: 1.6;
    color: var(--theme-body-text);
    opacity: 0.7;
    max-width: 90%;
    margin-bottom: 1.5rem;
}

.article-meta {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    font-family: var(--gallery-font-mono);
    font-size: 0.8rem;
}

.article-date {
    color: var(--theme-meta-text);
}

.tag {
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
    border: 1px solid var(--theme-border-medium);
    color: var(--theme-body-text);
    border-radius: 4px;
    font-weight: 500;
    text-transform: uppercase;
}

/* Transitions */
.sidebar-enter-active {
    transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.5s;
}

.sidebar-leave-active {
    transition: transform 0.4s cubic-bezier(0.55, 0.085, 0.68, 0.53), opacity 0.4s;
}

.sidebar-enter-from,
.sidebar-leave-to {
    transform: translateX(100%);
    opacity: 0;
}

.article-item-enter-active {
    transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    transition-delay: calc(var(--index) * 0.06s + 0.2s);
    /* Staggered delay */
}

.article-item-enter-from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
}

/* Responsive */
@media (max-width: 1024px) {
    .articles-sidebar {
        width: 60vw;
    }

    .gallery-header {
        top: calc(70px + 3vh);
        /* 适配平板的HeadMenu */
    }
}

@media (max-width: 768px) {
    .gallery-header {
        top: calc(65px + 2vh);
        /* 移动端HeadMenu更小 */
        left: 5vw;
    }

    .gallery-title {
        font-size: 2.5rem;
    }

    .carousel-container {
        height: calc(65vh - 30px);
        /* 移动端调整 */
        padding-bottom: 3vh;
    }

    .collection-item {
        width: 280px;
        height: 400px;
        margin-left: -140px;
        margin-top: -200px;
    }

    .card-title {
        font-size: 1.4rem;
    }

    .articles-sidebar {
        width: 100%;
        padding: 0;
    }

    .sidebar-header,
    .articles-list {
        padding: 2rem;
    }

    .sidebar-header h2 {
        font-size: 2.5rem;
    }

    .article-title {
        font-size: 1.4rem;
    }

    .expanded-image {
        /* Mobile adjustments handled by inline styles largely, but reset generic rules if needed */
    }

    .navigation-hint {
        gap: 2rem;
        bottom: 5vh;
    }
}
</style>
