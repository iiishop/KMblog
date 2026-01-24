<template>
    <div class="post-panel" @mouseenter="handleMouseEnter" @mousemove="handleMouseMove" @mouseleave="handleMouseLeave"
        :style="{ '--mouse-x': mouseX, '--mouse-y': mouseY }">
        <!-- 粒子背景容器 -->
        <canvas ref="particleCanvas" class="particle-canvas"></canvas>

        <!-- 光晕效果 -->
        <div class="glow-orb" :style="glowStyle"></div>

        <div class="image-panel" v-if="imageSrc && imageSrc !== loadingGif" :style="{ width: imagePanelWidth }">
            <div class="image-border-frame">
                <img :src="imageSrc" alt="Image" @load="adjustImagePanelWidth" @error="handleImageError" />
                <div class="image-shimmer"></div>
            </div>
        </div>
        <div class="content-panel">
            <!-- 装饰性几何图形 -->
            <div class="deco-geometry">
                <div class="deco-circle"></div>
                <div class="deco-triangle"></div>
            </div>

            <div v-if="metadata" class="content-wrapper">

                <!-- Left Main Content Area -->
                <div class="main-content-area">
                    <div class="title-panel" @click="initiateTransition">
                        <p class="title-text">
                            <span v-for="(char, index) in metadata.title" :key="index" class="title-char"
                                :style="{ '--char-index': index }">
                                {{ char === ' ' ? '\u00A0' : char }}
                            </span>
                        </p>
                        <div class="title-underline"></div>
                    </div>

                    <div class="pre-panel" @click="initiateTransition">
                        <pre class="pre-text">{{ metadata.pre }}</pre>
                        <div class="pre-gradient-overlay"></div>
                    </div>
                </div>

                <!-- Right Meta Sidebar -->
                <div class="meta-sidebar">
                    <div class="meta-list">
                        <div class="meta-item category-row" v-if="lastCategory">
                            <div class="meta-icon-wrapper">
                                <IconCategory class="meta-icon" />
                                <div class="icon-ripple"></div>
                            </div>
                            <router-link :to="categoryLink" class="meta-link">
                                <span class="link-text">{{ lastCategory }}</span>
                                <span class="link-arrow">→</span>
                            </router-link>
                        </div>
                        <div class="meta-item date-row" v-if="metadata.date">
                            <div class="meta-icon-wrapper">
                                <IconDate class="meta-icon" />
                                <div class="icon-ripple"></div>
                            </div>
                            <router-link :to="archiveLink" class="meta-link">
                                <span class="link-text">{{ metadata.date }}</span>
                                <span class="link-arrow">→</span>
                            </router-link>
                        </div>
                    </div>

                    <div class="props-divider">
                        <div class="divider-glow"></div>
                    </div>

                    <div class="tags-container">
                        <Tag v-for="(tag, index) in metadata.tags" :key="index" :tagname="tag"
                            :style="{ '--tag-index': index }" class="animated-tag" />
                    </div>
                </div>

            </div>

            <!-- 光效扫描线 -->
            <div class="scan-line"></div>
        </div>

    </div>
    
    <!-- 全屏过渡遮罩 - 使用Teleport确保最高层级 -->
    <teleport to="body">
        <transition name="page-transition">
            <div v-if="isTransitioning" class="transition-overlay">
                <!-- 背景粒子爆发 -->
                <canvas ref="transitionCanvas" class="transition-canvas"></canvas>
                
                <!-- 径向扩散波纹 -->
                <div class="radial-waves">
                    <div class="wave" v-for="i in 5" :key="i" :style="{ '--wave-delay': i * 0.1 + 's' }"></div>
                </div>
                
                <!-- 几何图形动画 -->
                <div class="floating-shapes">
                    <div class="shape shape-circle" v-for="i in 8" :key="'c' + i" 
                        :style="{ '--shape-delay': Math.random() * 0.5 + 's', '--shape-x': Math.random() * 100 + '%', '--shape-y': Math.random() * 100 + '%' }">
                    </div>
                    <div class="shape shape-square" v-for="i in 6" :key="'s' + i"
                        :style="{ '--shape-delay': Math.random() * 0.5 + 's', '--shape-x': Math.random() * 100 + '%', '--shape-y': Math.random() * 100 + '%' }">
                    </div>
                </div>
                
                <!-- 主要内容 -->
                <div class="transition-content">
                    <div class="transition-spinner">
                        <div class="spinner-ring"></div>
                        <div class="spinner-ring"></div>
                        <div class="spinner-ring"></div>
                    </div>
                    
                    <!-- 文字碎片化效果 -->
                    <div class="transition-text-wrapper">
                        <p class="transition-text">{{ metadata.title }}</p>
                        <div class="text-particles">
                            <span v-for="i in 20" :key="i" class="text-particle"
                                :style="{ '--particle-delay': Math.random() * 0.3 + 's', '--particle-angle': Math.random() * 360 + 'deg' }">
                            </span>
                        </div>
                    </div>
                    
                    <!-- 加载进度条 -->
                    <div class="loading-bar">
                        <div class="loading-progress"></div>
                    </div>
                </div>
            </div>
        </transition>
    </teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, defineAsyncComponent } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import config from '@/config'; // 导入全局配置
import { parseMarkdownMetadata } from "@/utils";
import loadingGif from '/public/assets/loading.gif';

// 使用动态导入进行代码分割
const Tag = defineAsyncComponent(() => import('./Tag.vue'));
const IconCategory = defineAsyncComponent(() => import('@/components/icons/IconCategory.vue'));
const IconDate = defineAsyncComponent(() => import('@/components/icons/IconDate.vue'));

// 定义 props
const props = defineProps({
    imageUrl: String,
    markdownUrl: String
});

// 定义 ref 来存储图片链接和 meta 数据
const imageSrc = ref(props.imageUrl || loadingGif);
const metadata = ref({});

// 定义 imagePanelWidth
const imagePanelWidth = ref('auto');

// 鼠标位置追踪
const mouseX = ref(0);
const mouseY = ref(0);
const glowStyle = ref({});

// 过渡动画状态
const isTransitioning = ref(false);

// 粒子系统
const particleCanvas = ref(null);
let particleAnimationFrame = null;
let particles = [];

// 过渡画布
const transitionCanvas = ref(null);
let transitionAnimationFrame = null;

class Particle {
    constructor(canvasWidth, canvasHeight) {
        this.x = Math.random() * canvasWidth;
        this.y = Math.random() * canvasHeight;
        this.size = Math.random() * 2 + 0.5;
        this.speedX = Math.random() * 0.5 - 0.25;
        this.speedY = Math.random() * 0.5 - 0.25;
        this.opacity = Math.random() * 0.5 + 0.2;
    }

    update(canvasWidth, canvasHeight) {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x > canvasWidth) this.x = 0;
        if (this.x < 0) this.x = canvasWidth;
        if (this.y > canvasHeight) this.y = 0;
        if (this.y < 0) this.y = canvasHeight;
    }

    draw(ctx) {
        ctx.fillStyle = `rgba(102, 126, 234, ${this.opacity})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

function initParticles() {
    if (!particleCanvas.value) return;
    
    const canvas = particleCanvas.value;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    particles = [];
    const particleCount = Math.floor((canvas.width * canvas.height) / 15000);
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle(canvas.width, canvas.height));
    }
}

function animateParticles() {
    if (!particleCanvas.value) return;

    const canvas = particleCanvas.value;
    const ctx = canvas.getContext('2d');
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(particle => {
        particle.update(canvas.width, canvas.height);
        particle.draw(ctx);
    });

    // 连接附近的粒子
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 100) {
                ctx.strokeStyle = `rgba(102, 126, 234, ${0.1 * (1 - distance / 100)})`;
                ctx.lineWidth = 0.5;
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
            }
        }
    }

    particleAnimationFrame = requestAnimationFrame(animateParticles);
}

// 鼠标事件处理
function handleMouseEnter() {
    initParticles();
    animateParticles();
}

function handleMouseMove(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width);
    const y = ((e.clientY - rect.top) / rect.height);
    
    mouseX.value = x;
    mouseY.value = y;

    glowStyle.value = {
        left: `${e.clientX - rect.left}px`,
        top: `${e.clientY - rect.top}px`,
    };
}

function handleMouseLeave() {
    if (particleAnimationFrame) {
        cancelAnimationFrame(particleAnimationFrame);
        particleAnimationFrame = null;
    }
}

// 图片加载时调整 image-panel 宽度
const adjustImagePanelWidth = (event) => {
    const img = event.target;
    const naturalWidth = img.naturalWidth;
    const naturalHeight = img.naturalHeight;
    const aspectRatio = naturalWidth / naturalHeight;

    // 计算新的宽度，最大不超过 30%
    const newWidth = Math.min(30, aspectRatio * 13); // 13 是 image-panel 的高度
    imagePanelWidth.value = `${newWidth}rem`;
};

// 初始化 Markdown meta 数据的函数
async function initializeMarkdown(url) {
    console.log('Initializing markdown with URL:', url);
    try {
        const response = await axios.get(url.startsWith('http') ? url : new URL(url, import.meta.url).href);
        const content = response.data;

        // 解析 Markdown 内容，仅解析 meta 数据
        const { meta } = await parseMarkdownMetadata(content);
        metadata.value = meta;

        // 格式化日期
        if (metadata.value.date) {
            metadata.value.date = formatDateString(metadata.value.date);
        }

        console.log('Metadata:', metadata.value);
    } catch (error) {
        console.error('Failed to fetch markdown content:', error);
    }
}

// 去掉日期中的时间部分
function formatDateString(dateString) {
    // 使用正则表达式匹配 YYYY-MM-DD hh-mm-ss 格式
    const dateTimeRegex = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/;

    // 如果匹配到该格式，去掉 hh-mm-ss 部分
    if (dateTimeRegex.test(dateString)) {
        return dateString.split(' ')[0];
    }

    // 如果格式不匹配，则返回原始字符串
    return dateString;
}

// 初始化图片链接的函数
function initializeImage(url) {
    console.log('Initializing image with URL:', url);
    if (url) {
        if (url.startsWith('http') || url.startsWith('/')) {
            // 处理网络图片链接 或 本地绝对路径
            imageSrc.value = loadingGif;
            const img = new Image();
            img.src = url;
            img.onload = () => {
                imageSrc.value = url;
            };
            img.onerror = () => {
                console.error('Failed to load image:', url);
                imageSrc.value = '';
            };
        } else {
            // 处理本地相对路径图片文件
            imageSrc.value = new URL(url, import.meta.url).href;
        }
    } else {
        imageSrc.value = '';
    }
    console.log('Image source set to:', imageSrc.value);
}

// 图片加载错误时处理函数
function handleImageError() {
    imageSrc.value = loadingGif;
}

// 计算最后一个目录和链接
const lastCategory = computed(() => {
    if (metadata.value.categories && metadata.value.categories.length > 0) {
        return metadata.value.categories[metadata.value.categories.length - 1];
    }
    return '';
});

const categoryLink = computed(() => {
    if (metadata.value.categories && metadata.value.categories.length > 0) {
        const fullPath = metadata.value.categories.join('/');
        return { name: 'CategoryPage', params: { fullPath } };
    }
    return '#';
});

const archiveLink = computed(() => ({ name: 'ArchivePage' }));

// 在组件挂载时初始化链接
onMounted(() => {
    console.log('Component mounted');
    if (props.imageUrl) {
        initializeImage(props.imageUrl);
    }
    if (props.markdownUrl) {
        initializeMarkdown(props.markdownUrl);
    }
});

// 使用 useRouter 钩子获取路由实例
const router = useRouter();

// 过渡动画粒子爆发
function animateTransitionParticles() {
    if (!transitionCanvas.value) return;
    
    const canvas = transitionCanvas.value;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    const particleCount = 100;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    // 创建粒子
    for (let i = 0; i < particleCount; i++) {
        const angle = (Math.PI * 2 * i) / particleCount;
        particles.push({
            x: centerX,
            y: centerY,
            vx: Math.cos(angle) * (Math.random() * 3 + 2),
            vy: Math.sin(angle) * (Math.random() * 3 + 2),
            size: Math.random() * 4 + 2,
            opacity: 1,
            color: `hsl(${250 + Math.random() * 30}, 70%, ${50 + Math.random() * 20}%)`
        });
    }
    
    function animate() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach((p, index) => {
            p.x += p.vx;
            p.y += p.vy;
            p.opacity -= 0.01;
            p.size *= 0.98;
            
            if (p.opacity <= 0) return;
            
            ctx.fillStyle = p.color.replace(')', `, ${p.opacity})`);
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
        });
        
        if (particles.some(p => p.opacity > 0)) {
            transitionAnimationFrame = requestAnimationFrame(animate);
        }
    }
    
    animate();
}

// 全屏过渡动画
function initiateTransition() {
    isTransitioning.value = true;
    
    // 启动粒子爆发效果
    setTimeout(() => {
        animateTransitionParticles();
    }, 100);
    
    // 延迟导航，让动画播放
    setTimeout(() => {
        navigateToPost();
    }, 1200);
}

// 定义导航到 PostPage 的函数
function navigateToPost() {
    // markdownUrl 格式: /Posts/Collection/file.md 或 /Posts/file.md
    const urlParts = props.markdownUrl.split('/').filter(part => part); // 过滤空字符串
    const mdName = urlParts[urlParts.length - 1].replace('.md', '');

    // 如果路径有3个部分 ['Posts', 'Collection', 'file.md']，则有合集
    // 如果路径有2个部分 ['Posts', 'file.md']，则无合集
    const collection = urlParts.length > 2 ? urlParts[1] : null;

    router.push({
        name: 'PostPage',
        params: { collection, mdName }
    });
}

// 清理
onUnmounted(() => {
    if (particleAnimationFrame) {
        cancelAnimationFrame(particleAnimationFrame);
    }
    if (transitionAnimationFrame) {
        cancelAnimationFrame(transitionAnimationFrame);
    }
});
</script>

<style scoped>
.post-panel {
    gap: 1.5rem;
    display: flex;
    height: 16rem;
    width: 100%;
    margin: auto;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    isolation: isolate;
}

/* === 粒子背景 === */
.particle-canvas {
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    opacity: 0;
    transition: opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 16px;
}

.post-panel:hover .particle-canvas {
    opacity: 1;
}

/* === 光晕效果 === */
.glow-orb {
    position: absolute;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(102, 126, 234, 0.15) 0%, transparent 70%);
    pointer-events: none;
    transform: translate(-50%, -50%);
    transition: opacity 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    opacity: 0;
    z-index: 1;
    filter: blur(40px);
}

.post-panel:hover .glow-orb {
    opacity: 1;
}

/* === Image Panel === */
.image-panel {
    border-radius: 20px;
    height: 100%;
    position: relative;
    flex-shrink: 0;
    z-index: 2;
}

.image-border-frame {
    position: relative;
    width: 100%;
    height: 100%;
    border-radius: 20px;
    overflow: hidden;
    box-shadow:
        0 10px 40px rgba(102, 126, 234, 0.2),
        0 0 0 1px rgba(255, 255, 255, 0.5),
        inset 0 0 0 1px rgba(102, 126, 234, 0.1);
    background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.1) 0%,
            rgba(102, 126, 234, 0.05) 100%);
}

.image-border-frame::before {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 20px;
    padding: 2px;
    background: linear-gradient(135deg,
            rgba(102, 126, 234, 0.5),
            rgba(118, 75, 162, 0.5),
            rgba(102, 126, 234, 0.5));
    -webkit-mask: linear-gradient(#fff 0 0) content-box,
        linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    transition: opacity 0.5s ease;
    z-index: -1;
}

.post-panel:hover .image-border-frame::before {
    opacity: 1;
    animation: borderRotate 3s linear infinite;
}

@keyframes borderRotate {
    0% {
        filter: hue-rotate(0deg);
    }

    100% {
        filter: hue-rotate(360deg);
    }
}

.image-border-frame img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.8s cubic-bezier(0.25, 1, 0.5, 1);
    display: block;
}

.post-panel:hover .image-border-frame img {
    transform: scale(1.1) rotate(2deg);
}

/* 图片光芒效果 */
.image-shimmer {
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg,
            transparent 0%,
            rgba(255, 255, 255, 0.6) 50%,
            transparent 100%);
    transform: translateX(-100%) skewX(-15deg);
    transition: none;
}

.post-panel:hover .image-shimmer {
    animation: shimmer 1.5s ease-in-out;
}

@keyframes shimmer {
    0% {
        transform: translateX(-100%) skewX(-15deg);
    }

    100% {
        transform: translateX(200%) skewX(-15deg);
    }
}

/* === Content Panel === */
.content-panel {
    padding: 2rem;
    border-radius: 20px;
    background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.75) 0%,
            rgba(255, 255, 255, 0.65) 100%);
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.8);
    box-shadow:
        0 8px 32px rgba(102, 126, 234, 0.12),
        0 0 0 1px rgba(102, 126, 234, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);

    flex-grow: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 2;
}

.post-panel:hover .content-panel {
    transform: translateY(-3px);
    box-shadow:
        0 20px 60px rgba(102, 126, 234, 0.2),
        0 0 0 1px rgba(102, 126, 234, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 1);
    background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.85) 0%,
            rgba(255, 255, 255, 0.75) 100%);
}

/* === 装饰几何图形 === */
.deco-geometry {
    position: absolute;
    top: -50px;
    right: -50px;
    width: 200px;
    height: 200px;
    pointer-events: none;
    opacity: 0.05;
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.post-panel:hover .deco-geometry {
    opacity: 0.1;
    transform: rotate(45deg) scale(1.2);
}

.deco-circle {
    position: absolute;
    width: 120px;
    height: 120px;
    border: 3px solid #667eea;
    border-radius: 50%;
    top: 20%;
    left: 20%;
    animation: float 6s ease-in-out infinite;
}

.deco-triangle {
    position: absolute;
    width: 0;
    height: 0;
    border-left: 60px solid transparent;
    border-right: 60px solid transparent;
    border-bottom: 100px solid #764ba2;
    bottom: 10%;
    right: 10%;
    animation: float 6s ease-in-out infinite reverse;
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0) rotate(0deg);
    }

    50% {
        transform: translateY(-20px) rotate(10deg);
    }
}

/* === Layout Structure === */
.content-wrapper {
    display: flex;
    height: 100%;
    gap: 2rem;
    position: relative;
    z-index: 1;
}

.main-content-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    overflow: hidden;
}

.meta-sidebar {
    width: 25%;
    min-width: 180px;
    border-left: 2px solid transparent;
    border-image: linear-gradient(to bottom,
            transparent 0%,
            rgba(102, 126, 234, 0.2) 50%,
            transparent 100%) 1;
    padding-left: 1.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 1.5rem;
}

/* === Typography & Elements === */

/* Title Panel - 字符动画 */
.title-panel {
    display: flex;
    flex-direction: column;
    cursor: pointer;
    margin-bottom: 1rem;
    position: relative;
}

.title-text {
    font-family: 'Noto Serif SC', 'Source Han Serif SC', 'Georgia', serif;
    font-weight: 800;
    font-size: 1.75rem;
    color: #2c3e50;
    margin: 0;
    line-height: 1.3;
    display: flex;
    flex-wrap: wrap;
    gap: 0.1em;
}

.title-char {
    display: inline-block;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: titleAppear 0.8s ease-out backwards;
    animation-delay: calc(var(--char-index) * 0.03s);
}

@keyframes titleAppear {
    from {
        opacity: 0;
        transform: translateY(20px) rotateX(-90deg);
    }

    to {
        opacity: 1;
        transform: translateY(0) rotateX(0);
    }
}

.title-panel:hover .title-char {
    color: #667eea;
    transform: translateY(-2px);
    text-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.title-panel:hover .title-char:nth-child(even) {
    animation: bounce 0.6s ease-in-out;
}

@keyframes bounce {

    0%,
    100% {
        transform: translateY(-2px);
    }

    50% {
        transform: translateY(-8px);
    }
}

/* 标题下划线 */
.title-underline {
    height: 3px;
    width: 0;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 2px;
    margin-top: 0.5rem;
    transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 10px rgba(102, 126, 234, 0.4);
}

.title-panel:hover .title-underline {
    width: 100%;
}

/* Preview Text */
.pre-panel {
    flex-grow: 1;
    cursor: pointer;
    border-radius: 12px;
    padding: 1rem;
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    background: linear-gradient(135deg,
            rgba(102, 126, 234, 0.02) 0%,
            rgba(118, 75, 162, 0.02) 100%);
}

.pre-panel:hover {
    background: linear-gradient(135deg,
            rgba(102, 126, 234, 0.05) 0%,
            rgba(118, 75, 162, 0.05) 100%);
    transform: translateX(5px);
}

.pre-text {
    font-family: 'Merriweather', 'Noto Serif SC', serif;
    font-size: 0.95rem;
    color: #555;
    white-space: pre-wrap;
    word-wrap: break-word;
    margin: 0;
    line-height: 1.8;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 4;
    overflow: hidden;
    position: relative;
    z-index: 1;
}

.pre-gradient-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 50%;
    background: linear-gradient(to bottom,
            transparent 0%,
            rgba(255, 255, 255, 0.8) 100%);
    pointer-events: none;
}

/* === Sidebar Elements === */
.meta-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.9rem;
    color: #666;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.meta-item:hover {
    transform: translateX(5px);
}

.meta-icon-wrapper {
    position: relative;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: linear-gradient(135deg,
            rgba(102, 126, 234, 0.1) 0%,
            rgba(118, 75, 162, 0.1) 100%);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.meta-item:hover .meta-icon-wrapper {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    transform: scale(1.1) rotate(5deg);
}

.meta-icon {
    width: 1.2rem;
    height: 1.2rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1;
}

.meta-item:hover .meta-icon {
    color: white;
}

.icon-ripple {
    position: absolute;
    inset: 0;
    border-radius: 10px;
    border: 2px solid #667eea;
    opacity: 0;
}

.meta-item:hover .icon-ripple {
    animation: ripple 0.6s ease-out;
}

@keyframes ripple {
    0% {
        transform: scale(1);
        opacity: 1;
    }

    100% {
        transform: scale(1.5);
        opacity: 0;
    }
}

.meta-link {
    text-decoration: none;
    color: inherit;
    font-weight: 600;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex: 1;
}

.link-text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.link-arrow {
    opacity: 0;
    transform: translateX(-10px);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    color: #667eea;
    font-weight: bold;
}

.meta-item:hover .link-arrow {
    opacity: 1;
    transform: translateX(0);
}

.meta-item:hover .meta-link {
    color: #667eea;
}

/* Divider */
.props-divider {
    height: 2px;
    background: linear-gradient(90deg,
            transparent 0%,
            rgba(102, 126, 234, 0.2) 50%,
            transparent 100%);
    width: 100%;
    position: relative;
    overflow: hidden;
}

.divider-glow {
    position: absolute;
    inset: -2px;
    background: linear-gradient(90deg,
            transparent 0%,
            rgba(102, 126, 234, 0.6) 50%,
            transparent 100%);
    opacity: 0;
    filter: blur(5px);
}

.post-panel:hover .divider-glow {
    animation: dividerGlow 2s ease-in-out infinite;
}

@keyframes dividerGlow {

    0%,
    100% {
        opacity: 0;
        transform: translateX(-100%);
    }

    50% {
        opacity: 1;
        transform: translateX(100%);
    }
}

/* Tags Container */
.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.animated-tag {
    animation: tagAppear 0.5s ease-out backwards;
    animation-delay: calc(var(--tag-index) * 0.1s);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes tagAppear {
    from {
        opacity: 0;
        transform: scale(0.5) rotate(-10deg);
    }

    to {
        opacity: 1;
        transform: scale(1) rotate(0);
    }
}

.animated-tag:hover {
    transform: translateY(-3px) scale(1.05);
}

/* === 光效扫描线 === */
.scan-line {
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg,
            transparent 0%,
            rgba(102, 126, 234, 0.1) 50%,
            transparent 100%);
    pointer-events: none;
    z-index: 10;
}

.post-panel:hover .scan-line {
    animation: scan 2s ease-in-out infinite;
}

@keyframes scan {
    0% {
        left: -100%;
    }

    100% {
        left: 200%;
    }
}

/* === 全屏过渡动画 === */
.transition-overlay {
    position: fixed;
    inset: 0;
    background: radial-gradient(circle at center,
            rgba(102, 126, 234, 0.98) 0%,
            rgba(118, 75, 162, 0.98) 50%,
            rgba(79, 70, 229, 0.98) 100%);
    backdrop-filter: blur(30px) saturate(150%);
    z-index: 999999;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    overflow: hidden;
}

/* 过渡画布 */
.transition-canvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

/* 径向波纹 */
.radial-waves {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.wave {
    position: absolute;
    width: 100px;
    height: 100px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    animation: waveExpand 2s ease-out infinite;
    animation-delay: var(--wave-delay);
}

@keyframes waveExpand {
    0% {
        width: 100px;
        height: 100px;
        opacity: 1;
    }
    100% {
        width: 1500px;
        height: 1500px;
        opacity: 0;
    }
}

/* 浮动几何图形 */
.floating-shapes {
    position: absolute;
    inset: 0;
    pointer-events: none;
}

.shape {
    position: absolute;
    left: var(--shape-x);
    top: var(--shape-y);
    animation: shapeFloat 3s ease-in-out infinite;
    animation-delay: var(--shape-delay);
}

.shape-circle {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.4);
    border-radius: 50%;
}

.shape-square {
    width: 15px;
    height: 15px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    transform: rotate(45deg);
}

@keyframes shapeFloat {
    0%, 100% {
        transform: translate(0, 0) rotate(0deg) scale(1);
        opacity: 0.4;
    }
    25% {
        transform: translate(30px, -30px) rotate(90deg) scale(1.2);
        opacity: 0.6;
    }
    50% {
        transform: translate(-20px, -60px) rotate(180deg) scale(0.8);
        opacity: 0.3;
    }
    75% {
        transform: translate(-40px, -30px) rotate(270deg) scale(1.1);
        opacity: 0.5;
    }
}

.transition-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2.5rem;
    position: relative;
    z-index: 10;
}

/* 文字包装器 */
.transition-text-wrapper {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

/* 文字粒子 */
.text-particles {
    position: absolute;
    inset: 0;
    pointer-events: none;
}

.text-particle {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 4px;
    height: 4px;
    background: white;
    border-radius: 50%;
    animation: particleExplode 1.5s ease-out infinite;
    animation-delay: var(--particle-delay);
}

@keyframes particleExplode {
    0% {
        transform: translate(-50%, -50%) rotate(var(--particle-angle)) translateY(0) scale(1);
        opacity: 1;
    }
    100% {
        transform: translate(-50%, -50%) rotate(var(--particle-angle)) translateY(-50px) scale(0);
        opacity: 0;
    }
}

/* 加载进度条 */
.loading-bar {
    width: 300px;
    height: 4px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 2px;
    overflow: hidden;
    position: relative;
}

.loading-progress {
    height: 100%;
    background: linear-gradient(90deg, 
        rgba(255, 255, 255, 0.5) 0%,
        rgba(255, 255, 255, 1) 50%,
        rgba(255, 255, 255, 0.5) 100%);
    background-size: 200% 100%;
    border-radius: 2px;
    animation: loadingProgress 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

@keyframes loadingProgress {
    0% {
        width: 0%;
        background-position: 0% 50%;
    }
    50% {
        width: 70%;
        background-position: 100% 50%;
    }
    100% {
        width: 100%;
        background-position: 200% 50%;
    }
}

.transition-spinner {
    position: relative;
    width: 120px;
    height: 120px;
    filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
}

.spinner-ring {
    position: absolute;
    inset: 0;
    border: 3px solid transparent;
    border-top-color: white;
    border-right-color: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    animation: spin 1.2s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

.spinner-ring:nth-child(2) {
    inset: 15px;
    animation-duration: 1s;
    animation-direction: reverse;
    border-top-color: rgba(255, 255, 255, 0.8);
    border-right-color: rgba(255, 255, 255, 0.2);
    border-width: 4px;
}

.spinner-ring:nth-child(3) {
    inset: 30px;
    animation-duration: 0.8s;
    border-top-color: rgba(255, 255, 255, 0.5);
    border-right-color: rgba(255, 255, 255, 0.1);
    border-width: 2px;
}

@keyframes spin {
    0% {
        transform: rotate(0deg) scale(1);
    }
    50% {
        transform: rotate(180deg) scale(1.1);
    }
    100% {
        transform: rotate(360deg) scale(1);
    }
}

.transition-text {
    font-family: 'Noto Serif SC', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: white;
    text-align: center;
    max-width: 80%;
    text-shadow: 
        0 0 20px rgba(255, 255, 255, 0.5),
        0 0 40px rgba(102, 126, 234, 0.3);
    animation: textFloat 2s ease-in-out infinite;
    position: relative;
    z-index: 1;
}

@keyframes textFloat {
    0%, 100% {
        opacity: 0.85;
        transform: translateY(0) scale(1);
        filter: blur(0px);
    }
    25% {
        opacity: 1;
        transform: translateY(-5px) scale(1.02);
        filter: blur(0px);
    }
    50% {
        opacity: 0.9;
        transform: translateY(0) scale(1.05);
        filter: blur(0.5px);
    }
    75% {
        opacity: 1;
        transform: translateY(-3px) scale(1.02);
        filter: blur(0px);
    }
}

/* 过渡动画效果 */
.page-transition-enter-active {
    animation: transitionIn 1s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.page-transition-leave-active {
    animation: transitionOut 0.6s cubic-bezier(0.55, 0.085, 0.68, 0.53);
}

@keyframes transitionIn {
    0% {
        opacity: 0;
        transform: scale(0.5) rotate(-10deg);
        filter: blur(20px);
    }
    50% {
        opacity: 0.8;
        transform: scale(1.05) rotate(2deg);
        filter: blur(5px);
    }
    100% {
        opacity: 1;
        transform: scale(1) rotate(0deg);
        filter: blur(0px);
    }
}

@keyframes transitionOut {
    0% {
        opacity: 1;
        transform: scale(1) rotate(0deg);
        filter: blur(0px);
    }
    100% {
        opacity: 0;
        transform: scale(1.3) rotate(5deg);
        filter: blur(10px);
    }
}

/* === 响应式 === */
@media (max-width: 768px) {
    .content-wrapper {
        flex-direction: column;
        gap: 1rem;
    }

    .meta-sidebar {
        width: 100%;
        border-left: none;
        padding-left: 0;
        border-top: 2px solid transparent;
        border-image: linear-gradient(to right,
                transparent 0%,
                rgba(102, 126, 234, 0.2) 50%,
                transparent 100%) 1;
        padding-top: 1rem;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
    }

    .tags-container {
        justify-content: flex-end;
    }

    .meta-list {
        flex-direction: row;
        gap: 1.5rem;
    }

    .post-panel {
        flex-direction: column;
        height: auto;
    }

    .image-panel {
        width: 100% !important;
        height: 200px;
    }

    .content-panel {
        width: 100%;
    }

    .particle-canvas {
        display: none;
    }
    
    .transition-text {
        font-size: 1.2rem;
    }
    
    .transition-spinner {
        width: 80px;
        height: 80px;
    }
    
    .loading-bar {
        width: 200px;
    }
    
    .wave {
        width: 50px;
        height: 50px;
    }
}
</style>

