<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue';

const props = defineProps({
    images: {
        type: Array,
        required: true
    },
    autoplay: {
        type: Boolean,
        default: true
    },
    interval: {
        type: Number,
        default: 4000
    },
    showIndicators: {
        type: Boolean,
        default: true
    },
    showArrows: {
        type: Boolean,
        default: true
    },
    height: {
        type: String,
        default: '400px'
    }
});

const currentIndex = ref(0);
const isTransitioning = ref(false);
const autoplayTimer = ref(null);
const carouselRef = ref(null);
const touchStartX = ref(0);
const touchEndX = ref(0);
const isDragging = ref(false);
const dragOffset = ref(0);

// 计算属性
const totalImages = computed(() => props.images.length);
const canGoPrev = computed(() => totalImages.value > 1);
const canGoNext = computed(() => totalImages.value > 1);

// 轮播图样式
const carouselStyle = computed(() => ({
    height: props.height,
    transform: `translateX(calc(-${currentIndex.value * 100}% + ${dragOffset.value}px))`,
    transition: isDragging.value ? 'none' : 'transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)'
}));

// 自动播放控制
const startAutoplay = () => {
    if (!props.autoplay || totalImages.value <= 1) return;

    stopAutoplay();
    autoplayTimer.value = setInterval(() => {
        next();
    }, props.interval);
};

const stopAutoplay = () => {
    if (autoplayTimer.value) {
        clearInterval(autoplayTimer.value);
        autoplayTimer.value = null;
    }
};

// 导航方法
const goTo = (index) => {
    if (isTransitioning.value || index === currentIndex.value) return;

    isTransitioning.value = true;
    currentIndex.value = index;

    setTimeout(() => {
        isTransitioning.value = false;
    }, 600);
};

const next = () => {
    if (!canGoNext.value || isTransitioning.value) return;

    const nextIndex = (currentIndex.value + 1) % totalImages.value;
    goTo(nextIndex);
};

const prev = () => {
    if (!canGoPrev.value || isTransitioning.value) return;

    const prevIndex = (currentIndex.value - 1 + totalImages.value) % totalImages.value;
    goTo(prevIndex);
};

// 触摸/鼠标事件处理
const handleTouchStart = (e) => {
    if (totalImages.value <= 1) return;

    stopAutoplay();
    isDragging.value = true;
    touchStartX.value = e.type === 'mousedown' ? e.clientX : e.touches[0].clientX;
    dragOffset.value = 0;
};

const handleTouchMove = (e) => {
    if (!isDragging.value || totalImages.value <= 1) return;

    e.preventDefault();
    const currentX = e.type === 'mousemove' ? e.clientX : e.touches[0].clientX;
    dragOffset.value = currentX - touchStartX.value;

    // 限制拖拽距离
    const maxDrag = carouselRef.value?.offsetWidth * 0.3 || 100;
    dragOffset.value = Math.max(-maxDrag, Math.min(maxDrag, dragOffset.value));
};

const handleTouchEnd = (e) => {
    if (!isDragging.value || totalImages.value <= 1) return;

    isDragging.value = false;
    touchEndX.value = e.type === 'mouseup' ? e.clientX : e.changedTouches[0].clientX;

    const deltaX = touchEndX.value - touchStartX.value;
    const threshold = 50; // 最小滑动距离

    if (Math.abs(deltaX) > threshold) {
        if (deltaX > 0) {
            prev();
        } else {
            next();
        }
    }

    dragOffset.value = 0;

    // 重新开始自动播放
    if (props.autoplay) {
        setTimeout(startAutoplay, 1000);
    }
};

// 键盘事件处理
const handleKeydown = (e) => {
    if (totalImages.value <= 1) return;

    switch (e.key) {
        case 'ArrowLeft':
            e.preventDefault();
            prev();
            break;
        case 'ArrowRight':
            e.preventDefault();
            next();
            break;
        case ' ':
            e.preventDefault();
            if (autoplayTimer.value) {
                stopAutoplay();
            } else {
                startAutoplay();
            }
            break;
    }
};

// 鼠标悬停控制
const handleMouseEnter = () => {
    stopAutoplay();
};

const handleMouseLeave = () => {
    if (props.autoplay && !isDragging.value) {
        startAutoplay();
    }
};

// 生命周期
onMounted(() => {
    if (props.autoplay) {
        startAutoplay();
    }

    // 添加键盘事件监听
    document.addEventListener('keydown', handleKeydown);

    // 添加鼠标事件监听
    if (carouselRef.value) {
        carouselRef.value.addEventListener('mousedown', handleTouchStart);
        document.addEventListener('mousemove', handleTouchMove);
        document.addEventListener('mouseup', handleTouchEnd);
    }
});

onUnmounted(() => {
    stopAutoplay();
    document.removeEventListener('keydown', handleKeydown);

    if (carouselRef.value) {
        carouselRef.value.removeEventListener('mousedown', handleTouchStart);
        document.removeEventListener('mousemove', handleTouchMove);
        document.removeEventListener('mouseup', handleTouchEnd);
    }
});

// 监听图片数组变化
watch(() => props.images, () => {
    currentIndex.value = 0;
    if (props.autoplay) {
        nextTick(() => {
            startAutoplay();
        });
    }
}, { immediate: true });
</script>

<template>
    <div class="carousel-container" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave"
        @touchstart="handleTouchStart" @touchmove="handleTouchMove" @touchend="handleTouchEnd">

        <!-- 主轮播区域 -->
        <div class="carousel-viewport" ref="carouselRef">
            <div class="carousel-track" :style="carouselStyle">
                <div v-for="(image, index) in images" :key="index" class="carousel-slide"
                    :class="{ 'active': index === currentIndex }">
                    <div class="image-container">
                        <img :src="image.src" :alt="image.alt || `Slide ${index + 1}`" class="carousel-image"
                            loading="lazy" />

                        <!-- 图片标题和描述 -->
                        <div v-if="image.title || image.description" class="image-overlay">
                            <div class="overlay-content">
                                <h3 v-if="image.title" class="image-title">{{ image.title }}</h3>
                                <p v-if="image.description" class="image-description">{{ image.description }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 导航箭头 -->
        <template v-if="showArrows && totalImages > 1">
            <button class="carousel-arrow carousel-arrow-prev" @click="prev" :disabled="!canGoPrev"
                aria-label="Previous image">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="15,18 9,12 15,6"></polyline>
                </svg>
            </button>

            <button class="carousel-arrow carousel-arrow-next" @click="next" :disabled="!canGoNext"
                aria-label="Next image">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9,18 15,12 9,6"></polyline>
                </svg>
            </button>
        </template>

        <!-- 指示器 -->
        <div v-if="showIndicators && totalImages > 1" class="carousel-indicators">
            <button v-for="(image, index) in images" :key="index" class="indicator"
                :class="{ 'active': index === currentIndex }" @click="goTo(index)"
                :aria-label="`Go to slide ${index + 1}`">
                <span class="indicator-dot"></span>
            </button>
        </div>

        <!-- 进度条 -->
        <div v-if="autoplay && totalImages > 1" class="carousel-progress">
            <div class="progress-bar" :style="{
                animationDuration: interval + 'ms',
                animationPlayState: autoplayTimer ? 'running' : 'paused'
            }"></div>
        </div>

        <!-- 计数器 -->
        <div v-if="totalImages > 1" class="carousel-counter">
            <span class="current">{{ currentIndex + 1 }}</span>
            <span class="separator">/</span>
            <span class="total">{{ totalImages }}</span>
        </div>
    </div>
</template>

<style scoped>
.carousel-container {
    position: relative;
    width: 100%;
    border-radius: 12px;
    overflow: hidden;
    background: var(--theme-content-bg);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    margin: 2rem 0;
    user-select: none;
}

.carousel-viewport {
    position: relative;
    width: 100%;
    overflow: hidden;
    cursor: grab;
}

.carousel-viewport:active {
    cursor: grabbing;
}

.carousel-track {
    display: flex;
    width: 100%;
    will-change: transform;
}

.carousel-slide {
    flex: 0 0 100%;
    width: 100%;
    position: relative;
}

.image-container {
    position: relative;
    width: 100%;
    height: 100%;
}

.carousel-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.3s ease;
}

.carousel-slide.active .carousel-image {
    transform: scale(1.02);
}

.image-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    /* 最小化背景覆盖，只在文字区域做轻微反衬 */
    background: 
        linear-gradient(to top, 
            rgba(0, 0, 0, 0.7) 0%, 
            rgba(0, 0, 0, 0.4) 40%,
            transparent 100%);
    color: white;
    padding: 3.5rem 1.5rem 2rem;
    transform: translateY(100%);
    transition: transform 0.5s cubic-bezier(0.23, 1, 0.32, 1);
    z-index: 2;
}

.carousel-slide.active .image-overlay {
    transform: translateY(0);
}

.overlay-content {
    max-width: 800px;
    margin: 0 auto;
    position: relative;
    z-index: 3;
}

.image-title {
    font-size: 1.75rem;
    font-weight: 800;
    margin: 0 0 0.75rem 0;
    line-height: 1.2;
    text-shadow: 
        0 0 16px rgba(0, 0, 0, 0.7),
        0 2px 8px rgba(0, 0, 0, 0.6);
    letter-spacing: -0.02em;
    color: #fff;
}

.image-description {
    font-size: 1.125rem;
    line-height: 1.6;
    margin: 0;
    color: rgba(255, 255, 255, 0.95);
    text-shadow: 
        0 0 12px rgba(0, 0, 0, 0.6),
        0 1px 4px rgba(0, 0, 0, 0.5);
}

/* 导航箭头 */
.carousel-arrow {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 48px;
    height: 48px;
    background: rgba(255, 255, 255, 0.9);
    border: none;
    border-radius: 50%;
    color: var(--theme-text);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    z-index: 10;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.carousel-arrow:hover {
    background: rgba(255, 255, 255, 1);
    transform: translateY(-50%) scale(1.1);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.carousel-arrow:disabled {
    opacity: 0.3;
    cursor: not-allowed;
    transform: translateY(-50%) scale(0.9);
}

.carousel-arrow svg {
    width: 20px;
    height: 20px;
}

.carousel-arrow-prev {
    left: 1rem;
}

.carousel-arrow-next {
    right: 1rem;
}

/* 指示器 */
.carousel-indicators {
    position: absolute;
    bottom: 1rem;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 0.5rem;
    z-index: 10;
}

.indicator {
    background: none;
    border: none;
    padding: 0.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.indicator-dot {
    display: block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transition: all 0.3s ease;
}

.indicator.active .indicator-dot {
    background: white;
    transform: scale(1.5);
    box-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

.indicator:hover .indicator-dot {
    background: rgba(255, 255, 255, 0.8);
    transform: scale(1.2);
}

/* 进度条 */
.carousel-progress {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: rgba(255, 255, 255, 0.2);
    z-index: 10;
}

.progress-bar {
    height: 100%;
    background: var(--theme-primary);
    width: 0;
    animation: progress linear;
    transform-origin: left;
}

@keyframes progress {
    from {
        width: 0;
    }

    to {
        width: 100%;
    }
}

/* 计数器 */
.carousel-counter {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
    backdrop-filter: blur(10px);
    z-index: 10;
}

.current {
    color: var(--theme-primary);
    font-weight: 700;
}

.separator {
    margin: 0 0.25rem;
    opacity: 0.7;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .carousel-container {
        margin: 1.5rem 0;
        border-radius: 8px;
    }

    .carousel-arrow {
        width: 40px;
        height: 40px;
    }

    .carousel-arrow svg {
        width: 16px;
        height: 16px;
    }

    .carousel-arrow-prev {
        left: 0.5rem;
    }

    .carousel-arrow-next {
        right: 0.5rem;
    }

    .image-overlay {
        padding: 1.5rem 1rem 1rem;
    }

    .image-title {
        font-size: 1.25rem;
    }

    .image-description {
        font-size: 0.875rem;
    }

    .carousel-counter {
        top: 0.5rem;
        right: 0.5rem;
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
    }
}

@media (max-width: 480px) {
    .carousel-arrow {
        width: 36px;
        height: 36px;
    }

    .carousel-arrow svg {
        width: 14px;
        height: 14px;
    }

    .image-title {
        font-size: 1.125rem;
    }

    .indicator-dot {
        width: 6px;
        height: 6px;
    }

    .carousel-indicators {
        bottom: 0.5rem;
        gap: 0.25rem;
    }

    .indicator {
        padding: 0.25rem;
    }
}

/* 深色主题适配 */
@media (prefers-color-scheme: dark) {
    .carousel-arrow {
        background: rgba(0, 0, 0, 0.8);
        color: white;
    }

    .carousel-arrow:hover {
        background: rgba(0, 0, 0, 0.9);
    }
}

/* 主题变量适配 */
[data-theme="dark"] .carousel-arrow,
[data-theme="night"] .carousel-arrow {
    background: rgba(0, 0, 0, 0.8);
    color: white;
}

[data-theme="dark"] .carousel-arrow:hover,
[data-theme="night"] .carousel-arrow:hover {
    background: rgba(0, 0, 0, 0.9);
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {

    .carousel-track,
    .carousel-image,
    .image-overlay,
    .carousel-arrow,
    .indicator-dot,
    .progress-bar {
        transition: none;
        animation: none;
    }
}

/* 焦点样式 */
.carousel-arrow:focus,
.indicator:focus {
    outline: 2px solid var(--theme-primary);
    outline-offset: 2px;
}
</style>