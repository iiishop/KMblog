<template>
    <Transition name="viewer-fade">
        <div v-if="visible" class="image-viewer-overlay" @click="close">
            <div class="image-viewer-container" @click.stop>
                <!-- 关闭按钮 -->
                <button class="viewer-close-btn" @click="close" title="关闭 (ESC)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 6L6 18M6 6l12 12" />
                    </svg>
                </button>

                <!-- 图片/SVG 内容 -->
                <div class="viewer-content" ref="contentRef">
                    <!-- 普通图片 -->
                    <img v-if="imageType === 'img'" :src="imageSrc" :alt="imageAlt" class="viewer-image"
                        @load="onImageLoad" />

                    <!-- SVG（Mermaid 图表） -->
                    <div v-else-if="imageType === 'svg'" class="viewer-svg-container" v-html="svgContent"></div>
                </div>

                <!-- 缩放控制按钮 -->
                <div class="viewer-controls">
                    <button @click="zoomOut" title="缩小 (-)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8" />
                            <path d="M21 21l-4.35-4.35M8 11h6" />
                        </svg>
                    </button>
                    <span class="zoom-level">{{ Math.round(scale * 100) }}%</span>
                    <button @click="zoomIn" title="放大 (+)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8" />
                            <path d="M21 21l-4.35-4.35M11 8v6M8 11h6" />
                        </svg>
                    </button>
                    <button @click="resetZoom" title="重置 (0)">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                            <path d="M3 3v5h5" />
                        </svg>
                    </button>
                </div>

                <!-- 图片信息（可选） -->
                <div v-if="imageAlt" class="viewer-info">
                    {{ imageAlt }}
                </div>
            </div>
        </div>
    </Transition>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';

const props = defineProps({
    visible: {
        type: Boolean,
        default: false
    },
    imageSrc: {
        type: String,
        default: ''
    },
    imageAlt: {
        type: String,
        default: ''
    },
    imageType: {
        type: String,
        default: 'img', // 'img' 或 'svg'
        validator: (value) => ['img', 'svg'].includes(value)
    },
    svgContent: {
        type: String,
        default: ''
    }
});

const emit = defineEmits(['update:visible', 'close']);

const contentRef = ref(null);
const scale = ref(1);
const minScale = 0.5;
const maxScale = 3;
const scaleStep = 0.25;

// 关闭查看器
const close = () => {
    emit('update:visible', false);
    emit('close');
    resetZoom();
};

// 放大
const zoomIn = () => {
    if (scale.value < maxScale) {
        scale.value = Math.min(scale.value + scaleStep, maxScale);
        applyScale();
    }
};

// 缩小
const zoomOut = () => {
    if (scale.value > minScale) {
        scale.value = Math.max(scale.value - scaleStep, minScale);
        applyScale();
    }
};

// 重置缩放
const resetZoom = () => {
    scale.value = 1;
    applyScale();
};

// 应用缩放
const applyScale = () => {
    if (contentRef.value) {
        const element = contentRef.value.querySelector('img, .viewer-svg-container');
        if (element) {
            element.style.transform = `scale(${scale.value})`;
        }
    }
};

// 图片加载完成
const onImageLoad = () => {
    // 可以在这里添加加载完成后的逻辑
};

// 键盘事件处理
const handleKeydown = (e) => {
    if (!props.visible) return;

    switch (e.key) {
        case 'Escape':
            close();
            break;
        case '+':
        case '=':
            zoomIn();
            break;
        case '-':
            zoomOut();
            break;
        case '0':
            resetZoom();
            break;
    }
};

// 监听可见性变化
watch(() => props.visible, (newVal) => {
    if (newVal) {
        // 阻止背景滚动
        document.body.style.overflow = 'hidden';
    } else {
        // 恢复滚动
        document.body.style.overflow = '';
        resetZoom();
    }
});

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
    document.body.style.overflow = '';
});
</script>

<style scoped>
.image-viewer-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.9);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    backdrop-filter: blur(10px);
}

.image-viewer-container {
    position: relative;
    max-width: 95vw;
    max-height: 95vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.viewer-content {
    max-width: 100%;
    max-height: calc(95vh - 120px);
    overflow: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
}

.viewer-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    transition: transform 0.3s ease;
    transform-origin: center;
}

.viewer-svg-container {
    transition: transform 0.3s ease;
    transform-origin: center;
    background: white;
    padding: 2rem;
    border-radius: 8px;
}

.viewer-svg-container :deep(svg) {
    max-width: 80vw !important;
    max-height: 70vh !important;
    width: auto !important;
    height: auto !important;
}

.viewer-close-btn {
    position: absolute;
    top: -3rem;
    right: 0;
    background: rgba(255, 255, 255, 0.1);
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: white;
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    backdrop-filter: blur(5px);
}

.viewer-close-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.5);
    transform: rotate(90deg);
}

.viewer-close-btn svg {
    width: 1.5rem;
    height: 1.5rem;
}

.viewer-controls {
    position: absolute;
    bottom: -4rem;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(255, 255, 255, 0.1);
    padding: 0.75rem 1.5rem;
    border-radius: 2rem;
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.viewer-controls button {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.viewer-controls button:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.5);
    transform: scale(1.1);
}

.viewer-controls button svg {
    width: 1rem;
    height: 1rem;
}

.zoom-level {
    color: white;
    font-size: 0.9rem;
    font-weight: 600;
    min-width: 3rem;
    text-align: center;
    user-select: none;
}

.viewer-info {
    position: absolute;
    bottom: -6rem;
    left: 50%;
    transform: translateX(-50%);
    color: rgba(255, 255, 255, 0.9);
    font-size: 0.9rem;
    background: rgba(0, 0, 0, 0.5);
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    max-width: 80%;
    text-align: center;
    backdrop-filter: blur(5px);
}

/* 过渡动画 */
.viewer-fade-enter-active,
.viewer-fade-leave-active {
    transition: opacity 0.3s ease;
}

.viewer-fade-enter-from,
.viewer-fade-leave-to {
    opacity: 0;
}

/* 响应式 */
@media (max-width: 768px) {
    .image-viewer-overlay {
        padding: 1rem;
    }

    .viewer-content {
        max-height: calc(95vh - 150px);
    }

    .viewer-controls {
        bottom: -5rem;
        padding: 0.5rem 1rem;
        gap: 0.3rem;
    }

    .viewer-controls button {
        width: 1.75rem;
        height: 1.75rem;
    }

    .zoom-level {
        font-size: 0.85rem;
        min-width: 2.5rem;
    }

    .viewer-svg-container {
        padding: 1rem;
    }

    .viewer-svg-container :deep(svg) {
        max-width: 90vw !important;
        max-height: 60vh !important;
    }
}
</style>
