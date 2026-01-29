<template>
    <div class="graph-card" :class="{ 'is-hovered': isHovered, 'is-expanding': isExpanding }" :style="cardStyle"
        @mouseenter="handleMouseEnter" @mousemove="handleMouseMove" @mouseleave="handleMouseLeave" @click="handleClick"
        ref="cardRef">
        <!-- 图片容器 -->
        <div class="image-wrapper">
            <!-- 加载占位符 -->
            <div v-if="!isImageLoaded && !isImageError" class="image-placeholder">
                <div class="placeholder-shimmer"></div>
                <div class="placeholder-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" />
                        <circle cx="8.5" cy="8.5" r="1.5" />
                        <polyline points="21 15 16 10 5 21" />
                    </svg>
                </div>
            </div>

            <!-- 错误占位符 -->
            <div v-if="isImageError" class="image-error">
                <div class="error-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="8" x2="12" y2="12" />
                        <line x1="12" y1="16" x2="12.01" y2="16" />
                    </svg>
                </div>
                <p class="error-text">Failed to load</p>
            </div>

            <img v-if="shouldLoadImage" ref="imageRef" :src="imageSrc" :alt="image.alt" class="graph-image"
                :class="{ 'is-loaded': isImageLoaded, 'is-error': isImageError }" loading="lazy" @load="handleImageLoad"
                @error="handleImageError" />

            <!-- 动态光晕层 -->
            <div class="image-glow" :style="glowStyle"></div>

            <!-- 扫描线效果 -->
            <div class="scan-line"></div>
        </div>

        <!-- 悬停信息层 -->
        <transition name="info-fade">
            <div v-if="isHovered" class="info-overlay">
                <div class="info-content">
                    <h3 class="image-title">{{ image.title }}</h3>
                    <p class="image-meta">{{ image.date }}</p>
                </div>
            </div>
        </transition>

        <!-- 边框光效 -->
        <div class="border-glow"></div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import gsap from 'gsap';

const props = defineProps({
    image: {
        type: Object,
        required: true
    },
    index: {
        type: Number,
        required: true
    },
    column: {
        type: Number,
        default: 0
    },
    position: {
        type: Object,
        default: null
    }
});

const emit = defineEmits(['click', 'mouseenter', 'mouseleave']);

// Refs
const cardRef = ref(null);
const imageRef = ref(null);

// 状态
const isHovered = ref(false);
const isExpanding = ref(false);
const isImageLoaded = ref(false);
const isImageError = ref(false);
const isIntersecting = ref(false);
const shouldLoadImage = ref(false);
const mouseX = ref(0.5);
const mouseY = ref(0.5);
const glowX = ref('50%');
const glowY = ref('50%');

// Intersection Observer
let observer = null;

// 计算属性
const cardStyle = computed(() => {
    const style = {
        '--card-aspect-ratio': props.image.aspectRatio || 1,
        '--glow-x': glowX.value,
        '--glow-y': glowY.value,
    };

    // 应用瀑布流位置
    if (props.position) {
        style.position = 'absolute';
        style.left = `${props.position.x}px`;
        style.top = `${props.position.y}px`;
        style.width = `${props.position.width}px`;
        style.height = `${props.position.height}px`;
    }

    return style;
});

const glowStyle = computed(() => {
    return {
        '--card-glow': props.image.dominantColor || 'hsl(250, 60%, 65%)',
    };
});

// 计算实际图片源 - 只有在应该加载时才返回真实路径
const imageSrc = computed(() => {
    return shouldLoadImage.value ? props.image.src : '';
});

// 事件处理
function handleMouseEnter(e) {
    // 使用 nextTick 确保 DOM 更新后再添加 class，让 transition 生效
    requestAnimationFrame(() => {
        isHovered.value = true;
    });
    emit('mouseenter', props.index);
}

function handleMouseMove(e) {
    if (!cardRef.value || !isHovered.value) return;

    // 计算鼠标相对位置 (0 到 1)
    const rect = cardRef.value.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;

    mouseX.value = x;
    mouseY.value = y;

    // 只更新光晕位置，不修改 transform
    glowX.value = `${x * 100}%`;
    glowY.value = `${y * 100}%`;
}

function handleMouseLeave(e) {
    isHovered.value = false;
    // 重置光晕位置
    glowX.value = '50%';
    glowY.value = '50%';
    emit('mouseleave', props.index);
}

function handleClick() {
    // Prevent multiple clicks during animation
    if (isExpanding.value) return;

    isExpanding.value = true;

    // Get card position for modal animation
    const rect = cardRef.value?.getBoundingClientRect();

    // Create GSAP timeline for orchestrated animation
    const tl = gsap.timeline({
        onComplete: () => {
            // Trigger parent component modal open with card position
            emit('click', props.image, rect);
        }
    });

    // Smooth scale up with elastic ease
    tl.to(cardRef.value, {
        scale: 1.05,
        duration: 0.3,
        ease: 'power2.out'
    });

    // Keep card visible during modal transition
    // The modal will handle the rest of the animation
}

// Reset card state after modal closes
function resetCardState() {
    isExpanding.value = false;
    if (cardRef.value) {
        gsap.to(cardRef.value, {
            scale: 1,
            opacity: 1,
            duration: 0.4,
            ease: 'power2.out'
        });
    }
}

// Expose reset method for parent component
defineExpose({
    resetCardState
});

// 图片加载处理
function handleImageLoad() {
    isImageLoaded.value = true;
    isImageError.value = false;
}

function handleImageError() {
    isImageError.value = true;
    isImageLoaded.value = false;
    console.error(`Failed to load image: ${props.image.src}`);
}

// 设置 Intersection Observer
function setupIntersectionObserver() {
    if (!cardRef.value) return;

    const options = {
        root: null, // 使用视口作为根
        rootMargin: '200px', // 提前 200px 开始加载
        threshold: 0.01 // 只要 1% 可见就触发
    };

    observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                isIntersecting.value = true;
                shouldLoadImage.value = true;

                // 一旦开始加载，就停止观察
                if (observer && cardRef.value) {
                    observer.unobserve(cardRef.value);
                }
            }
        });
    }, options);

    observer.observe(cardRef.value);
}

// 清理 Observer
function cleanupObserver() {
    if (observer && cardRef.value) {
        observer.unobserve(cardRef.value);
        observer.disconnect();
        observer = null;
    }
}

onMounted(() => {
    setupIntersectionObserver();
});

onBeforeUnmount(() => {
    cleanupObserver();
});
</script>

<style scoped>
/* === 悬浮记忆：Graph Card 极致美化 === */

/* 
  美学宣言：
  - 磁场光晕系统：卡片具有"引力场"，鼠标接近时产生动态光晕
  - 呼吸动画：创造生命感
  - 全息质感：半透明边框和光效
  - 黄金比例间距：自然的视觉韵律
*/

.graph-card {
    position: absolute;
    cursor: pointer;
    transform: translateY(0) scale(1);
    transform-style: preserve-3d;
    transition: transform 0.6s cubic-bezier(0.23, 1, 0.32, 1),
        opacity 0.6s cubic-bezier(0.23, 1, 0.32, 1),
        box-shadow 0.6s cubic-bezier(0.23, 1, 0.32, 1),
        z-index 0s;
    will-change: transform;
    padding: 0;
    background: transparent;
    border-radius: 20px;
}

/* 呼吸动画 - 只在非 hover 状态下运行 */
.graph-card:not(.is-hovered) {
    animation: cardBreathe 2.5s ease-in-out infinite;
}

/* 呼吸动画 - 创造生命感 */
@keyframes cardBreathe {

    0%,
    100% {
        transform: translateY(0) scale(1);
    }

    50% {
        transform: translateY(0) scale(1.002);
    }
}

/* 全息边框 - 第一层：外发光 */
.graph-card::before {
    content: '';
    position: absolute;
    inset: -3px;
    border-radius: 23px;
    background: linear-gradient(135deg,
            hsla(250, 60%, 65%, 0.4),
            hsla(340, 85%, 65%, 0.3),
            hsla(250, 60%, 65%, 0.4));
    opacity: 0;
    filter: blur(20px);
    transition: opacity 0.6s cubic-bezier(0.23, 1, 0.32, 1);
    pointer-events: none;
    z-index: -1;
}

/* 全息边框 - 第二层：内边框 */
.graph-card::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    padding: 1.5px;
    background: linear-gradient(135deg,
            hsla(250, 60%, 85%, 0.6),
            hsla(340, 85%, 75%, 0.4),
            hsla(250, 60%, 85%, 0.6));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1);
    pointer-events: none;
    animation: borderFlow 3s linear infinite;
}

@keyframes borderFlow {
    0% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }

    100% {
        background-position: 0% 50%;
    }
}

/* 悬停状态 - 磁场激活 */
.graph-card.is-hovered {
    z-index: 10;
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.4),
        0 0 0 1px hsla(250, 60%, 85%, 0.2);
}

.graph-card.is-hovered::before {
    opacity: 1;
    animation: glowPulse 2s ease-in-out infinite;
}

.graph-card.is-hovered::after {
    opacity: 1;
}

@keyframes glowPulse {

    0%,
    100% {
        opacity: 0.8;
        filter: blur(20px);
    }

    50% {
        opacity: 1;
        filter: blur(25px);
    }
}

/* 图片容器 - 有机形态的圆角 */
.image-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: linear-gradient(135deg,
            hsla(250, 20%, 15%, 0.95),
            hsla(250, 20%, 10%, 0.98));
    /* 使用不规则的圆角创造有机感 */
    border-radius: 18px 22px 20px 24px;
    box-shadow:
        inset 0 1px 0 hsla(250, 60%, 85%, 0.1),
        inset 0 -1px 0 hsla(250, 20%, 5%, 0.5);
    backdrop-filter: blur(10px);
    /* 添加微妙的形态动画 */
    animation: morphShape 8s ease-in-out infinite;
}

/* 有机形态动画 - 圆角的微妙变化 */
@keyframes morphShape {

    0%,
    100% {
        border-radius: 18px 22px 20px 24px;
    }

    25% {
        border-radius: 22px 18px 24px 20px;
    }

    50% {
        border-radius: 20px 24px 18px 22px;
    }

    75% {
        border-radius: 24px 20px 22px 18px;
    }
}

.graph-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.8s cubic-bezier(0.23, 1, 0.32, 1),
        opacity 0.6s cubic-bezier(0.23, 1, 0.32, 1),
        filter 0.6s cubic-bezier(0.23, 1, 0.32, 1);
    opacity: 0;
}

.graph-image.is-loaded {
    opacity: 1;
}

.graph-image.is-error {
    opacity: 0.3;
    filter: grayscale(1);
}

.graph-card.is-hovered .graph-image {
    filter: brightness(1.1) contrast(1.05);
}

/* 磁场光晕 - 核心记忆点 */
.image-glow {
    position: absolute;
    inset: -20%;
    background: radial-gradient(circle at var(--glow-x) var(--glow-y),
            var(--card-glow, hsl(250, 60%, 65%)) 0%,
            transparent 50%);
    opacity: 0;
    mix-blend-mode: screen;
    transition: opacity 0.6s cubic-bezier(0.23, 1, 0.32, 1);
    pointer-events: none;
    filter: blur(30px);
}

.graph-card.is-hovered .image-glow {
    opacity: 0.7;
    animation: glowBreath 2s ease-in-out infinite;
}

@keyframes glowBreath {

    0%,
    100% {
        opacity: 0.6;
        transform: scale(1);
    }

    50% {
        opacity: 0.8;
        transform: scale(1.1);
    }
}

/* 扫描线 - 未来感交互反馈 */
.scan-line {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg,
            transparent 0%,
            hsla(340, 100%, 75%, 0.8) 20%,
            hsla(340, 100%, 85%, 1) 50%,
            hsla(340, 100%, 75%, 0.8) 80%,
            transparent 100%);
    transform: translateY(-100%);
    opacity: 0;
    box-shadow: 0 0 20px hsla(340, 100%, 75%, 0.6);
}

.graph-card.is-hovered .scan-line {
    animation: scan 2.5s cubic-bezier(0.23, 1, 0.32, 1) infinite;
}

@keyframes scan {
    0% {
        transform: translateY(-100%);
        opacity: 0;
    }

    5% {
        opacity: 1;
    }

    95% {
        opacity: 1;
    }

    100% {
        transform: translateY(calc(100% + 100vh));
        opacity: 0;
    }
}

/* 信息覆盖层 - 优雅的渐变遮罩 */
.info-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg,
            transparent 0%,
            hsla(250, 20%, 10%, 0.3) 50%,
            hsla(250, 20%, 5%, 0.95) 100%);
    display: flex;
    align-items: flex-end;
    padding: clamp(1rem, 3vw, 2rem);
    backdrop-filter: blur(12px) saturate(150%);
    border-radius: 18px;
}

.info-content {
    width: 100%;
    transform: translateY(8px);
    animation: infoSlideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes infoSlideUp {
    to {
        transform: translateY(0);
    }
}

/* 标题 - 戏剧性衬线字体 */
.image-title {
    font-family: 'Playfair Display', 'Noto Serif SC', serif;
    font-size: clamp(1.1rem, 2.5vw, 1.8rem);
    font-weight: 700;
    font-variation-settings: 'wght' 700, 'opsz' 72;
    color: hsla(250, 10%, 98%, 1);
    margin: 0 0 clamp(0.3rem, 1vw, 0.6rem) 0;
    text-shadow:
        0 2px 8px rgba(0, 0, 0, 0.6),
        0 0 20px hsla(340, 85%, 65%, 0.3);
    letter-spacing: -0.02em;
    line-height: 1.2;

    /* 文字超出处理 */
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* 元数据 - 未来感等宽字体 */
.image-meta {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: clamp(0.65rem, 1.5vw, 0.8rem);
    font-weight: 500;
    color: hsla(250, 10%, 75%, 0.9);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
    opacity: 0.8;
}

/* 边框光效 - 简化但更强烈 */
.border-glow {
    position: absolute;
    inset: -8px;
    border-radius: 28px;
    background: radial-gradient(circle at 50% 50%,
            hsla(250, 60%, 65%, 0.4),
            hsla(340, 85%, 65%, 0.3),
            transparent 70%);
    opacity: 0;
    filter: blur(20px);
    transition: opacity 0.6s cubic-bezier(0.23, 1, 0.32, 1);
    z-index: -2;
}

.graph-card.is-hovered .border-glow {
    opacity: 1;
    animation: borderGlowPulse 2s ease-in-out infinite;
}

@keyframes borderGlowPulse {

    0%,
    100% {
        opacity: 0.8;
        transform: scale(1);
    }

    50% {
        opacity: 1;
        transform: scale(1.05);
    }
}

/* 过渡动画 - 流畅的淡入淡出 */
.info-fade-enter-active {
    transition: opacity 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.info-fade-leave-active {
    transition: opacity 0.3s cubic-bezier(0.23, 1, 0.32, 1);
}

.info-fade-enter-from,
.info-fade-leave-to {
    opacity: 0;
}

/* 加载占位符 - 优雅的骨架屏 */
.image-placeholder {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg,
            hsla(250, 20%, 15%, 1),
            hsla(250, 20%, 12%, 1));
    overflow: hidden;
    border-radius: 18px;
}

.placeholder-shimmer {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg,
            transparent 0%,
            hsla(250, 60%, 65%, 0.08) 50%,
            transparent 100%);
    animation: shimmer 2.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

@keyframes shimmer {
    0% {
        transform: translateX(-100%);
    }

    100% {
        transform: translateX(100%);
    }
}

.placeholder-icon {
    position: relative;
    z-index: 1;
    width: clamp(40px, 8vw, 64px);
    height: clamp(40px, 8vw, 64px);
    color: hsla(250, 10%, 60%, 0.4);
    animation: iconPulse 2s ease-in-out infinite;
}

@keyframes iconPulse {

    0%,
    100% {
        opacity: 0.3;
        transform: scale(1);
    }

    50% {
        opacity: 0.5;
        transform: scale(1.05);
    }
}

.placeholder-icon svg {
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 0 10px hsla(250, 60%, 65%, 0.2));
}

/* 错误占位符 - 优雅的错误提示 */
.image-error {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg,
            hsla(0, 20%, 15%, 1),
            hsla(0, 20%, 12%, 1));
    gap: clamp(0.5rem, 2vw, 1rem);
    border-radius: 18px;
}

.error-icon {
    width: clamp(40px, 8vw, 64px);
    height: clamp(40px, 8vw, 64px);
    color: hsla(0, 70%, 60%, 0.7);
    animation: errorShake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97);
}

@keyframes errorShake {

    0%,
    100% {
        transform: translateX(0);
    }

    25% {
        transform: translateX(-4px);
    }

    75% {
        transform: translateX(4px);
    }
}

.error-icon svg {
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 0 10px hsla(0, 70%, 60%, 0.3));
}

.error-text {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: clamp(0.65rem, 1.5vw, 0.8rem);
    font-weight: 500;
    color: hsla(0, 10%, 70%, 0.8);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 0;
}

/* 响应式优化 */
@media (max-width: 768px) {
    .graph-card {
        border-radius: 16px;
    }

    .image-wrapper {
        border-radius: 14px;
    }

    .graph-card.is-hovered {
        transform: translateY(-8px) scale(1.01);
    }

    .info-overlay {
        padding: 1rem;
    }
}

/* 性能优化 */
@media (prefers-reduced-motion: reduce) {

    .graph-card,
    .graph-image,
    .image-glow,
    .scan-line,
    .border-glow {
        animation: none !important;
        transition-duration: 0.1s !important;
    }
}
</style>
