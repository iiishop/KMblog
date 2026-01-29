<template>
    <div class="waterfall-container" ref="containerRef">
        <!-- 背景粒子系统 -->
        <canvas ref="particleCanvas" class="particle-layer"></canvas>

        <!-- 磁力线层 -->
        <canvas ref="magneticCanvas" class="magnetic-layer"></canvas>

        <!-- 页面标题区域 -->
        <div class="gallery-header">
            <div class="header-content">
                <h1 class="gallery-title">
                    <span class="title-main">流光画廊</span>
                    <span class="title-sub">Flowing Light Gallery</span>
                </h1>
                <p class="gallery-description">
                    探索光影交织的视觉世界，每一帧都是独特的记忆
                </p>
                <div class="header-stats">
                    <div class="stat-item">
                        <span class="stat-number">{{ images.length }}</span>
                        <span class="stat-label">作品</span>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat-item">
                        <span class="stat-number">{{ columnCount }}</span>
                        <span class="stat-label">列</span>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat-item">
                        <span class="stat-number">{{ visibleImages.length }}</span>
                        <span class="stat-label">可见</span>
                    </div>
                </div>
            </div>

            <!-- 装饰性元素 -->
            <div class="header-decoration">
                <div class="deco-circle deco-1"></div>
                <div class="deco-circle deco-2"></div>
                <div class="deco-circle deco-3"></div>
            </div>
        </div>

        <!-- 瀑布流网格 -->
        <div class="waterfall-grid" :style="gridStyle">
            <Graph v-for="(image, index) in visibleImages" :key="image.id" :ref="el => setGraphRef(image.id, el)"
                :image="image" :index="index" :column="getColumn(image.id)" :position="getPosition(image.id)"
                @click="handleGraphClick" @mouseenter="handleCardHover(image.id)"
                @mouseleave="handleCardLeave(image.id)" />
        </div>

        <!-- 页脚装饰 -->
        <div class="gallery-footer" v-if="visibleImages.length > 0">
            <div class="footer-line"></div>
            <p class="footer-text">已加载全部作品</p>
            <div class="footer-line"></div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import Graph from './WaterfallPanelComps/Graph.vue';

const props = defineProps({
    images: {
        type: Array,
        default: () => []
    }
});

const emit = defineEmits(['image-click']);

// Refs
const containerRef = ref(null);
const particleCanvas = ref(null);
const magneticCanvas = ref(null);

// 状态
const visibleImages = ref([]);
const hoveredCardIndex = ref(null);
const cardPositions = ref([]);
const columnCount = ref(4);
const cardWidth = ref(300);
const cardGap = ref(20);
const cardGapVariance = ref(8); // 有机偏移的最大值
const graphRefs = ref(new Map()); // 存储 Graph 组件引用
const imageOffsets = ref(new Map()); // 存储每个图片的固定偏移量

// 14.5 使用 requestAnimationFrame 优化滚动
let scrollTicking = false;
let scrollRAF = null;

// 15.6 添加鼠标位置追踪
function handleMouseMove(event) {
    if (!containerRef.value) return;

    const rect = containerRef.value.getBoundingClientRect();
    mousePosition.value = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top + window.scrollY
    };
}

// 计算属性
const gridStyle = computed(() => {
    return {
        position: 'relative',
        width: '100%',
        minHeight: `${getMaxColumnHeight()}px`
    };
});

// 13.2 实现响应式列数计算
function calculateColumnCount() {
    if (!containerRef.value) return 4;

    const containerWidth = containerRef.value.offsetWidth;
    const padding = 32; // 左右 padding
    const availableWidth = containerWidth - padding * 2;

    // 根据容器宽度计算最优列数
    if (availableWidth < 600) {
        return 1; // 手机
    } else if (availableWidth < 900) {
        return 2; // 小平板
    } else if (availableWidth < 1200) {
        return 3; // 大平板
    } else {
        return 4; // 桌面
    }
}

// 13.4 实现有机偏移生成（randomOffset）- 为每个图片生成固定的偏移
function getImageOffset(imageId, axis) {
    const key = `${imageId}-${axis}`;

    // 如果已经有偏移值，直接返回
    if (imageOffsets.value.has(key)) {
        return imageOffsets.value.get(key);
    }

    // 生成新的偏移值并保存
    const offset = (Math.random() - 0.5) * 2 * cardGapVariance.value;
    imageOffsets.value.set(key, offset);
    return offset;
}

// 13.3 实现最短列查找逻辑
function findShortestColumn(columnHeights) {
    let shortestIndex = 0;
    let shortestHeight = columnHeights[0];

    for (let i = 1; i < columnHeights.length; i++) {
        if (columnHeights[i] < shortestHeight) {
            shortestHeight = columnHeights[i];
            shortestIndex = i;
        }
    }

    return shortestIndex;
}

// 13.5 计算每个卡片的位置坐标
function calculateCardPosition(columnIndex, columnHeight, imageAspectRatio, imageId) {
    const padding = 32;
    const totalGap = cardGap.value * (columnCount.value - 1);
    const availableWidth = (containerRef.value?.offsetWidth || 1200) - padding * 2 - totalGap;
    const actualCardWidth = availableWidth / columnCount.value;

    // 计算卡片高度（保持宽高比）
    const cardHeight = actualCardWidth / (imageAspectRatio || 1);

    // 计算 x 坐标（使用固定的偏移量）
    const offsetX = getImageOffset(imageId, 'x');
    const x = padding + columnIndex * (actualCardWidth + cardGap.value) + offsetX;

    // 计算 y 坐标（使用固定的偏移量）
    const offsetY = getImageOffset(imageId, 'y');
    const y = columnHeight + offsetY;

    return {
        x,
        y,
        width: actualCardWidth,
        height: cardHeight,
        column: columnIndex
    };
}

// 获取最大列高度
function getMaxColumnHeight() {
    if (cardPositions.value.length === 0) return 0;

    const columnHeights = new Array(columnCount.value).fill(0);

    cardPositions.value.forEach(pos => {
        const columnBottom = pos.y + pos.height;
        if (columnBottom > columnHeights[pos.column]) {
            columnHeights[pos.column] = columnBottom;
        }
    });

    return Math.max(...columnHeights) + 32; // 添加底部 padding
}

// 13.1 创建 calculateWaterfallLayout 函数
function calculateWaterfallLayout(images, colCount) {
    if (!images || images.length === 0) {
        return [];
    }

    // 初始化列高度数组
    const columnHeights = new Array(colCount).fill(0);
    const positions = [];

    images.forEach((image, index) => {
        // 获取图片宽高比（默认为 1:1）
        const aspectRatio = image.aspectRatio || (image.width && image.height ? image.width / image.height : 1);

        // 找到最短的列
        const shortestColumn = findShortestColumn(columnHeights);

        // 计算卡片位置（传入 imageId 以获取固定偏移）
        const position = calculateCardPosition(shortestColumn, columnHeights[shortestColumn], aspectRatio, image.id);

        positions.push({
            ...position,
            id: image.id,
            index
        });

        // 更新列高度
        columnHeights[shortestColumn] = position.y + position.height + cardGap.value;
    });

    return positions;
}

// 14.1 创建 calculateVisibleCards 函数
// 14.2 计算可视区域范围
// 14.3 添加上下缓冲区
// 14.4 过滤可见卡片
function calculateVisibleCards() {
    if (!containerRef.value || cardPositions.value.length === 0) {
        visibleImages.value = props.images;
        return;
    }

    // 14.2 计算可视区域范围
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const viewportHeight = window.innerHeight;
    const containerTop = containerRef.value.offsetTop;

    // 相对于容器的可视区域
    const visibleTop = scrollTop - containerTop;
    const visibleBottom = visibleTop + viewportHeight;

    // 14.3 添加上下缓冲区（提前加载上下各一屏的内容）
    const bufferSize = viewportHeight;
    const rangeTop = Math.max(0, visibleTop - bufferSize);
    const rangeBottom = visibleBottom + bufferSize;

    // 14.4 过滤可见卡片
    const visible = [];
    cardPositions.value.forEach((position) => {
        const cardTop = position.y;
        const cardBottom = position.y + position.height;

        // 检查卡片是否在可视范围内（包含缓冲区）
        if (cardBottom >= rangeTop && cardTop <= rangeBottom) {
            const image = props.images[position.index];
            if (image) {
                visible.push(image);
            }
        }
    });

    visibleImages.value = visible;
}

// 获取列索引
function getColumn(imageId) {
    const position = cardPositions.value.find(pos => pos.id === imageId);
    return position ? position.column : 0;
}

// 获取卡片位置
function getPosition(imageId) {
    return cardPositions.value.find(pos => pos.id === imageId) || null;
}

// 更新布局
function updateLayout() {
    // 重新计算列数
    columnCount.value = calculateColumnCount();

    // 重新计算布局
    cardPositions.value = calculateWaterfallLayout(props.images, columnCount.value);

    // 更新可见卡片
    calculateVisibleCards();
}

// 设置 Graph 组件引用
function setGraphRef(imageId, el) {
    if (el) {
        graphRefs.value.set(imageId, el);
    } else {
        graphRefs.value.delete(imageId);
    }
}

// 事件处理
function handleCardHover(imageId) {
    // 找到图片在原始列表中的索引
    const position = cardPositions.value.find(pos => pos.id === imageId);
    if (position) {
        hoveredCardIndex.value = position.index;
    }
}

function handleCardLeave(imageId) {
    hoveredCardIndex.value = null;
}

// 处理 Graph 点击事件
function handleGraphClick(image, cardRect) {
    emit('image-click', image, cardRect);
}

// 重置所有卡片状态
function resetAllCardStates() {
    graphRefs.value.forEach(graphRef => {
        if (graphRef && graphRef.resetCardState) {
            graphRef.resetCardState();
        }
    });
}

// 暴露方法给父组件
defineExpose({
    resetAllCardStates
});

// 15.1 创建 GalleryParticle 类
class GalleryParticle {
    constructor(canvas) {
        this.canvas = canvas;
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.size = Math.random() * 2 + 1;
        this.opacity = Math.random() * 0.3 + 0.1;
        this.hue = 250 + Math.random() * 30; // 紫色系
    }

    // 15.3 实现粒子更新逻辑（引力场效果）
    update(mouseX, mouseY) {
        // 引力场效果 - 粒子被鼠标吸引
        const dx = mouseX - this.x;
        const dy = mouseY - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 200) {
            const force = (200 - distance) / 200;
            this.vx += (dx / distance) * force * 0.1;
            this.vy += (dy / distance) * force * 0.1;
        }

        // 速度衰减
        this.vx *= 0.95;
        this.vy *= 0.95;

        // 更新位置
        this.x += this.vx;
        this.y += this.vy;

        // 边界处理 - 循环
        if (this.x < 0) this.x = this.canvas.width;
        if (this.x > this.canvas.width) this.x = 0;
        if (this.y < 0) this.y = this.canvas.height;
        if (this.y > this.canvas.height) this.y = 0;
    }

    // 15.4 实现粒子绘制逻辑
    draw(ctx) {
        ctx.fillStyle = `hsla(${this.hue}, 70%, 65%, ${this.opacity})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

// 粒子系统状态
let particles = [];
let particleAnimationId = null;
let particleResizeHandler = null;
const mousePosition = ref({ x: 0, y: 0 });

// 17.1 创建粒子 Canvas 层
// 17.3 实现 Canvas 尺寸自适应
function setupParticleCanvas() {
    if (!particleCanvas.value) return null;

    const canvas = particleCanvas.value;
    const ctx = canvas.getContext('2d');

    // 在测试环境中，getContext 可能返回 null
    if (!ctx) return null;

    // 设置 canvas 尺寸自适应
    const resizeCanvas = () => {
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;

        // 设置实际像素尺寸（考虑设备像素比）
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;

        // 设置显示尺寸
        canvas.style.width = `${rect.width}px`;
        canvas.style.height = `${rect.height}px`;

        // 缩放上下文以匹配设备像素比
        ctx.scale(dpr, dpr);

        // 重新创建粒子（因为画布尺寸改变了）
        initParticles(canvas);
    };

    // 初始化尺寸
    resizeCanvas();

    // 保存 resize 处理器以便后续清理
    particleResizeHandler = resizeCanvas;
    window.addEventListener('resize', particleResizeHandler);

    return { canvas, ctx };
}

// 15.2 实现粒子初始化逻辑
function initParticles(canvas) {
    // 根据画布大小调整粒子数量（考虑显示尺寸而非实际像素）
    const displayWidth = canvas.offsetWidth || canvas.width;
    const displayHeight = canvas.offsetHeight || canvas.height;
    const particleCount = Math.floor((displayWidth * displayHeight) / 15000);

    particles = [];
    for (let i = 0; i < particleCount; i++) {
        particles.push(new GalleryParticle(canvas));
    }
}

// 15.5 实现粒子动画循环
function animateParticles(ctx, canvas) {
    if (!ctx || !canvas) return;

    // 清除画布（使用显示尺寸）
    const displayWidth = canvas.offsetWidth || canvas.width;
    const displayHeight = canvas.offsetHeight || canvas.height;
    ctx.clearRect(0, 0, displayWidth, displayHeight);

    // 更新和绘制每个粒子
    particles.forEach(particle => {
        particle.update(mousePosition.value.x, mousePosition.value.y);
        particle.draw(ctx);
    });

    particleAnimationId = requestAnimationFrame(() => animateParticles(ctx, canvas));
}

// 初始化粒子系统
function initParticleSystem() {
    const canvasData = setupParticleCanvas();
    if (!canvasData) return;

    const { canvas, ctx } = canvasData;
    animateParticles(ctx, canvas);
}

// 17.4 实现 Canvas 清理逻辑
function cleanupParticleCanvas() {
    // 取消动画帧
    if (particleAnimationId) {
        cancelAnimationFrame(particleAnimationId);
        particleAnimationId = null;
    }

    // 移除 resize 监听器
    if (particleResizeHandler) {
        window.removeEventListener('resize', particleResizeHandler);
        particleResizeHandler = null;
    }

    // 清空粒子数组
    particles = [];

    // 清除画布
    if (particleCanvas.value) {
        const ctx = particleCanvas.value.getContext('2d');
        if (ctx) {
            ctx.clearRect(0, 0, particleCanvas.value.width, particleCanvas.value.height);
        }
    }
}

// 磁力线系统状态
let magneticAnimationId = null;
let magneticResizeHandler = null;
const magneticLineTime = ref(0);

// 17.2 创建磁力线 Canvas 层
// 17.3 实现 Canvas 尺寸自适应
function setupMagneticCanvas() {
    if (!magneticCanvas.value) return null;

    const canvas = magneticCanvas.value;
    const ctx = canvas.getContext('2d');

    // 在测试环境中，getContext 可能返回 null
    if (!ctx) return null;

    // 设置 canvas 尺寸自适应
    const resizeCanvas = () => {
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;

        // 设置实际像素尺寸（考虑设备像素比）
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;

        // 设置显示尺寸
        canvas.style.width = `${rect.width}px`;
        canvas.style.height = `${rect.height}px`;

        // 缩放上下文以匹配设备像素比
        ctx.scale(dpr, dpr);
    };

    // 初始化尺寸
    resizeCanvas();

    // 保存 resize 处理器以便后续清理
    magneticResizeHandler = resizeCanvas;
    window.addEventListener('resize', magneticResizeHandler);

    return { canvas, ctx };
}

// 磁力线动画循环
function animateMagneticLines(ctx, canvas) {
    if (!ctx || !canvas) return;

    // 清除画布（使用显示尺寸）
    const displayWidth = canvas.offsetWidth || canvas.width;
    const displayHeight = canvas.offsetHeight || canvas.height;
    ctx.clearRect(0, 0, displayWidth, displayHeight);

    // 只在有悬停卡片时绘制磁力线
    if (hoveredCardIndex.value !== null) {
        drawMagneticLines(ctx, cardPositions.value, hoveredCardIndex.value, magneticLineTime.value);
    }

    // 更新时间
    magneticLineTime.value += 16; // 约 60fps

    magneticAnimationId = requestAnimationFrame(() => animateMagneticLines(ctx, canvas));
}

// 磁力线系统初始化
function initMagneticLines() {
    const canvasData = setupMagneticCanvas();
    if (!canvasData) return;

    const { canvas, ctx } = canvasData;
    animateMagneticLines(ctx, canvas);
}

// 17.4 实现 Canvas 清理逻辑
function cleanupMagneticCanvas() {
    // 取消动画帧
    if (magneticAnimationId) {
        cancelAnimationFrame(magneticAnimationId);
        magneticAnimationId = null;
    }

    // 移除 resize 监听器
    if (magneticResizeHandler) {
        window.removeEventListener('resize', magneticResizeHandler);
        magneticResizeHandler = null;
    }

    // 重置时间
    magneticLineTime.value = 0;

    // 清除画布
    if (magneticCanvas.value) {
        const ctx = magneticCanvas.value.getContext('2d');
        if (ctx) {
            ctx.clearRect(0, 0, magneticCanvas.value.width, magneticCanvas.value.height);
        }
    }
}

// 16.1 创建 drawMagneticLines 函数
// 16.2 计算卡片间距离
// 16.3 绘制贝塞尔曲线连接线
// 16.4 实现光点沿线移动动画
// 16.5 添加悬停卡片高亮
function drawMagneticLines(ctx, cards, hoveredIndex, time) {
    if (hoveredIndex === null || !cards || cards.length === 0) return;

    const hoveredCard = cards[hoveredIndex];
    if (!hoveredCard) return;

    // 计算悬停卡片的中心点
    const hoveredCenterX = hoveredCard.x + hoveredCard.width / 2;
    const hoveredCenterY = hoveredCard.y + hoveredCard.height / 2;

    cards.forEach((card, index) => {
        if (index === hoveredIndex) return;

        // 计算当前卡片的中心点
        const cardCenterX = card.x + card.width / 2;
        const cardCenterY = card.y + card.height / 2;

        // 16.2 计算卡片间距离
        const dx = cardCenterX - hoveredCenterX;
        const dy = cardCenterY - hoveredCenterY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // 只连接附近的卡片（距离小于 300px）
        if (distance < 300) {
            const opacity = (1 - distance / 300) * 0.3;

            // 16.3 绘制贝塞尔曲线连接线
            // 贝塞尔曲线控制点 - 创造有机感
            const cpx = (cardCenterX + hoveredCenterX) / 2 + (Math.random() - 0.5) * 50;
            const cpy = (cardCenterY + hoveredCenterY) / 2 + (Math.random() - 0.5) * 50;

            // 绘制连接线
            ctx.strokeStyle = `hsla(250, 70%, 65%, ${opacity})`;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(hoveredCenterX, hoveredCenterY);
            ctx.quadraticCurveTo(cpx, cpy, cardCenterX, cardCenterY);
            ctx.stroke();

            // 16.4 实现光点沿线移动动画
            drawMovingDot(ctx, hoveredCenterX, hoveredCenterY, cardCenterX, cardCenterY, cpx, cpy, time, distance);
        }
    });

    // 16.5 添加悬停卡片高亮
    // 在悬停卡片周围绘制光晕
    const glowRadius = 30;
    const gradient = ctx.createRadialGradient(
        hoveredCenterX, hoveredCenterY, 0,
        hoveredCenterX, hoveredCenterY, glowRadius
    );
    gradient.addColorStop(0, 'hsla(340, 85%, 65%, 0.4)');
    gradient.addColorStop(1, 'hsla(340, 85%, 65%, 0)');

    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(hoveredCenterX, hoveredCenterY, glowRadius, 0, Math.PI * 2);
    ctx.fill();
}

// 16.4 实现光点沿线移动动画
function drawMovingDot(ctx, startX, startY, endX, endY, cpx, cpy, time, distance) {
    // 根据距离调整动画速度（距离越远，速度越慢）
    const speed = 2000 + distance * 2; // 基础速度 + 距离因子
    const t = (time % speed) / speed; // 0 到 1 之间的值

    // 贝塞尔曲线上的点计算
    const x = (1 - t) * (1 - t) * startX + 2 * (1 - t) * t * cpx + t * t * endX;
    const y = (1 - t) * (1 - t) * startY + 2 * (1 - t) * t * cpy + t * t * endY;

    // 绘制光点
    const dotGradient = ctx.createRadialGradient(x, y, 0, x, y, 6);
    dotGradient.addColorStop(0, 'hsla(340, 85%, 65%, 0.9)');
    dotGradient.addColorStop(0.5, 'hsla(340, 85%, 65%, 0.5)');
    dotGradient.addColorStop(1, 'hsla(340, 85%, 65%, 0)');

    ctx.fillStyle = dotGradient;
    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    ctx.fill();

    // 绘制光点核心
    ctx.fillStyle = 'hsla(340, 100%, 75%, 1)';
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    ctx.fill();
}

// 14.5 使用 requestAnimationFrame 优化滚动
function handleScroll() {
    if (!scrollTicking) {
        scrollRAF = requestAnimationFrame(() => {
            calculateVisibleCards();
            scrollTicking = false;
        });
        scrollTicking = true;
    }
}

// 窗口大小变化监听
let resizeObserver = null;

onMounted(() => {
    initParticleSystem();
    initMagneticLines();
    updateLayout();

    // 监听容器大小变化
    if (containerRef.value && typeof ResizeObserver !== 'undefined') {
        resizeObserver = new ResizeObserver(() => {
            updateLayout();
        });
        resizeObserver.observe(containerRef.value);
    }

    // 14.5 添加滚动监听（使用 requestAnimationFrame 优化）
    window.addEventListener('scroll', handleScroll, { passive: true });

    // 15.6 添加鼠标移动监听
    if (containerRef.value) {
        containerRef.value.addEventListener('mousemove', handleMouseMove, { passive: true });
    }

    // 初始计算可见卡片
    calculateVisibleCards();
});

onUnmounted(() => {
    // 清理 ResizeObserver
    if (resizeObserver && containerRef.value) {
        resizeObserver.unobserve(containerRef.value);
        resizeObserver.disconnect();
    }

    // 14.5 清理滚动监听和 requestAnimationFrame
    window.removeEventListener('scroll', handleScroll);
    if (scrollRAF) {
        cancelAnimationFrame(scrollRAF);
    }

    // 17.4 清理粒子 Canvas 层
    cleanupParticleCanvas();

    // 17.4 清理磁力线 Canvas 层
    cleanupMagneticCanvas();

    // 15.6 清理鼠标移动监听
    if (containerRef.value) {
        containerRef.value.removeEventListener('mousemove', handleMouseMove);
    }
});

// 监听图片列表变化
watch(() => props.images, () => {
    updateLayout();
}, { deep: true });
</script>

<style scoped>
/* === 流光画廊：WaterfallPanel 极致美化 === */

/* 
  美学宣言：
  - 深邃宇宙背景：渐变 + 噪点纹理（支持主题切换）
  - 动态光晕系统：径向渐变 + 脉冲动画
  - 粒子星空：Canvas 粒子 + 引力场
  - 磁力连接线：贝塞尔曲线 + 光点动画
  - 流畅过渡：所有元素都有呼吸感
*/

.waterfall-container {
    position: relative;
    width: 100vw;
    /* 使用视口宽度 */
    min-height: 100vh;
    overflow: hidden;
    margin-left: calc(-50vw + 50%);
    /* 突破父容器限制 */

    /* 使用主题变量作为基础背景 */
    background-color: var(--theme-body-bg);

    /* 优雅的渐变背景 - 更柔和的过渡 */
    background-image:
        /* 主光晕 - 左上角 */
        radial-gradient(circle at 15% 20%,
            color-mix(in srgb, var(--gallery-primary) 12%, transparent) 0%,
            transparent 40%),
        /* 次光晕 - 右下角 */
        radial-gradient(circle at 85% 80%,
            color-mix(in srgb, var(--gallery-accent) 10%, transparent) 0%,
            transparent 40%),
        /* 中心光晕 - 增加深度 */
        radial-gradient(ellipse at 50% 50%,
            color-mix(in srgb, var(--gallery-primary-light) 6%, transparent) 0%,
            transparent 60%),
        /* 微妙的噪点纹理 */
        url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.015'/%3E%3C/svg%3E");

    /* 背景动画 - 微妙的呼吸感 */
    animation: backgroundPulse 25s ease-in-out infinite;

    /* 平滑过渡主题切换 */
    transition: background-color var(--theme-transition-duration) var(--theme-transition-easing);
}

@keyframes backgroundPulse {

    0%,
    100% {
        background-position: 0% 0%, 100% 100%, 50% 50%, 0% 0%;
        background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%;
    }

    50% {
        background-position: 5% 5%, 95% 95%, 55% 45%, 0% 0%;
        background-size: 110% 110%, 110% 110%, 105% 105%, 100% 100%;
    }
}

/* 粒子层 - 星空效果 */
.particle-layer {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    opacity: 0.8;

    /* 微妙的闪烁效果 */
    animation: particleShimmer 8s ease-in-out infinite;
}

@keyframes particleShimmer {

    0%,
    100% {
        opacity: 0.7;
    }

    50% {
        opacity: 0.9;
    }
}

/* 磁力线层 - 连接效果 */
.magnetic-layer {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 2;
    opacity: 1;
    mix-blend-mode: screen;

    /* 光晕效果 */
    filter: blur(0.5px);
}

/* 瀑布流网格 */
.waterfall-grid {
    margin-top: 1rem;
    position: relative;
    z-index: 1;
    padding: clamp(1.5rem, 4vw, 3rem);
    /* 防止布局抖动 */
    will-change: auto;

    /* 添加微妙的内发光（使用主题色） */
    &::before {
        content: '';
        position: absolute;
        inset: 0;
        pointer-events: none;
        background: radial-gradient(ellipse at 50% 0%,
                var(--gallery-primary) 0%,
                transparent 50%);
        opacity: 0.05;
        animation: gridGlow 10s ease-in-out infinite;
    }
}

/* === 页面标题区域 === */
.gallery-header {
    position: relative;
    padding: clamp(3rem, 8vw, 6rem) clamp(1.5rem, 4vw, 3rem) clamp(2rem, 5vw, 4rem);
    text-align: center;
    z-index: 1;
}

.header-content {
    position: relative;
    z-index: 2;
}

.gallery-title {
    margin: 0 0 clamp(1rem, 2vw, 1.5rem) 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: clamp(0.5rem, 1vw, 0.75rem);
}

.title-main {
    font-family: var(--gallery-font-hero);
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: var(--gallery-weight-black);
    background: linear-gradient(135deg,
            var(--gallery-primary-light) 0%,
            var(--gallery-accent) 50%,
            var(--gallery-primary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    line-height: 1.1;
    animation: titleShimmer 3s ease-in-out infinite;
}

@keyframes titleShimmer {

    0%,
    100% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }
}

.title-sub {
    font-family: var(--gallery-font-mono);
    font-size: clamp(0.75rem, 1.5vw, 1rem);
    font-weight: var(--gallery-weight-medium);
    color: var(--gallery-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.2em;
    opacity: 0.8;
}

.gallery-description {
    font-family: var(--gallery-font-body);
    font-size: clamp(0.95rem, 1.8vw, 1.2rem);
    font-weight: var(--gallery-weight-regular);
    color: var(--gallery-text-muted);
    max-width: 600px;
    margin: 0 auto clamp(1.5rem, 3vw, 2.5rem) auto;
    line-height: 1.6;
    opacity: 0.9;
}

/* 统计信息 */
.header-stats {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: clamp(1.5rem, 3vw, 2.5rem);
    margin-top: clamp(1.5rem, 3vw, 2rem);
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}

.stat-number {
    font-family: var(--gallery-font-mono);
    font-size: clamp(1.5rem, 3vw, 2.5rem);
    font-weight: var(--gallery-weight-bold);
    color: var(--gallery-primary-light);
    line-height: 1;
}

.stat-label {
    font-family: var(--gallery-font-body);
    font-size: clamp(0.75rem, 1.2vw, 0.9rem);
    font-weight: var(--gallery-weight-medium);
    color: var(--gallery-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    opacity: 0.7;
}

.stat-divider {
    width: 1px;
    height: clamp(2rem, 4vw, 3rem);
    background: linear-gradient(180deg,
            transparent 0%,
            var(--gallery-primary) 50%,
            transparent 100%);
    opacity: 0.3;
}

/* 装饰性元素 */
.header-decoration {
    position: absolute;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
    z-index: 1;
}

.deco-circle {
    position: absolute;
    border-radius: 50%;
    opacity: 0.1;
    animation: float 20s ease-in-out infinite;
}

.deco-1 {
    width: clamp(150px, 20vw, 300px);
    height: clamp(150px, 20vw, 300px);
    top: 10%;
    left: 5%;
    background: radial-gradient(circle,
            var(--gallery-primary-light) 0%,
            transparent 70%);
    animation-delay: 0s;
}

.deco-2 {
    width: clamp(200px, 25vw, 400px);
    height: clamp(200px, 25vw, 400px);
    top: 20%;
    right: 10%;
    background: radial-gradient(circle,
            var(--gallery-accent) 0%,
            transparent 70%);
    animation-delay: -7s;
}

.deco-3 {
    width: clamp(100px, 15vw, 200px);
    height: clamp(100px, 15vw, 200px);
    bottom: 10%;
    left: 50%;
    transform: translateX(-50%);
    background: radial-gradient(circle,
            var(--gallery-primary) 0%,
            transparent 70%);
    animation-delay: -14s;
}

@keyframes float {

    0%,
    100% {
        transform: translate(0, 0) scale(1);
    }

    33% {
        transform: translate(20px, -20px) scale(1.1);
    }

    66% {
        transform: translate(-20px, 20px) scale(0.9);
    }
}

/* === 页脚装饰 === */
.gallery-footer {
    position: relative;
    padding: clamp(3rem, 6vw, 5rem) clamp(1.5rem, 4vw, 3rem);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: clamp(1rem, 2vw, 2rem);
    z-index: 1;
}

.footer-line {
    flex: 1;
    height: 1px;
    max-width: clamp(100px, 20vw, 200px);
    background: linear-gradient(90deg,
            transparent 0%,
            var(--gallery-primary) 50%,
            transparent 100%);
    opacity: 0.3;
}

.footer-text {
    font-family: var(--gallery-font-mono);
    font-size: clamp(0.75rem, 1.2vw, 0.9rem);
    font-weight: var(--gallery-weight-medium);
    color: var(--gallery-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin: 0;
    opacity: 0.6;
}

@keyframes gridGlow {

    0%,
    100% {
        opacity: 0.03;
        transform: translateY(0);
    }

    50% {
        opacity: 0.08;
        transform: translateY(-20px);
    }
}

/* 容器边缘渐变遮罩 - 创造无限延伸感（使用主题色） */
.waterfall-container::before {
    justify-content: center;
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 120px;
    background: linear-gradient(180deg,
            var(--theme-body-bg) 0%,
            color-mix(in srgb, var(--theme-body-bg) 80%, transparent) 40%,
            transparent 100%);
    pointer-events: none;
    z-index: 3;
    transition: background var(--theme-transition-duration) var(--theme-transition-easing);
}

.waterfall-container::after {
    content: '';
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 120px;
    background: linear-gradient(0deg,
            var(--theme-body-bg) 0%,
            color-mix(in srgb, var(--theme-body-bg) 80%, transparent) 40%,
            transparent 100%);
    pointer-events: none;
    z-index: 3;
    transition: background var(--theme-transition-duration) var(--theme-transition-easing);
}

/* 响应式优化 */
@media (max-width: 768px) {
    .waterfall-grid {
        padding: clamp(1rem, 3vw, 1.5rem);
    }

    .waterfall-container::before,
    .waterfall-container::after {
        height: 80px;
    }
}

/* 性能优化 - 减少动画 */
@media (prefers-reduced-motion: reduce) {

    .waterfall-container,
    .particle-layer,
    .waterfall-grid::before {
        animation: none !important;
    }

    .waterfall-container {
        background-position: 0% 0%, 100% 100%, 50% 50%, 0% 0% !important;
    }
}

/* 滚动条美化（使用主题色） */
.waterfall-container::-webkit-scrollbar {
    width: 8px;
}

.waterfall-container::-webkit-scrollbar-track {
    background: var(--gallery-surface);
    transition: background var(--theme-transition-duration) var(--theme-transition-easing);
}

.waterfall-container::-webkit-scrollbar-thumb {
    background: color-mix(in srgb, var(--gallery-primary) 30%, transparent);
    border-radius: 4px;
    transition: background var(--theme-transition-duration) var(--theme-transition-easing);
}

.waterfall-container::-webkit-scrollbar-thumb:hover {
    background: color-mix(in srgb, var(--gallery-primary) 50%, transparent);
}
</style>
