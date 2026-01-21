<script setup>
import { ref, computed, watchEffect } from 'vue';
import { useRouter } from 'vue-router';
import config from '@/config'; // 导入全局配置

// 定义 props
const props = defineProps({
    tagname: {
        type: String,
        required: true,
        validator: value => value.length <= 8 // 确保 tagname 不超过 8 个字符
    },
    count: {
        type: Number,
        required: false,
        default: 1 // 默认 count 为 1
    }
});

// 计算要显示的 tagname，如果超过 8 个字符，则截断并加上 ...
const displayTagname = computed(() => {
    return props.tagname.length > 7 ? props.tagname.slice(0, 7) + '...' : props.tagname;
});

// 生成随机颜色的函数
function randomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// 计算对比颜色的函数 (黑或白)
function getContrastColor(hex) {
    // 将 hex 颜色值转换为 RGB
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    // 计算亮度 (YIQ)
    const yiq = (r * 299 + g * 587 + b * 114) / 1000;
    if (yiq >= 128) return '#000000';
    return '#FFFFFF';
}

// 辅助函数：将 Hex 转换为 RGB 字符串 (用于 CSS 变量)
function hexToRgb(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `${r}, ${g}, ${b}`;
}

// 初始化背景颜色和文字颜色
const backgroundColor = ref(randomColor());
const textColor = computed(() => getContrastColor(backgroundColor.value));

// 计算尺寸比例
const sizeFactor = computed(() => 1 + (props.count - 1) * 0.05);

// 计算样式 - 将动态颜色传给 CSS 变量
const tagStyle = computed(() => {
    const rgb = hexToRgb(backgroundColor.value);
    return {
        '--tag-bg-color': backgroundColor.value,
        '--tag-text-color': textColor.value,
        '--tag-shadow-color': `rgba(${rgb}, 0.4)`,
        '--tag-glow-color': `rgba(${rgb}, 0.6)`,
        padding: `${0.4 * sizeFactor.value}rem ${0.8 * sizeFactor.value}rem`, // 稍微调整 padding 让视觉更舒服
        fontSize: `${0.85 * sizeFactor.value}rem`,
    };
});

// 在组件挂载时生成随机背景颜色
watchEffect(() => {
    backgroundColor.value = randomColor();
});

// 获取路由实例
const router = useRouter();

// 处理标签点击事件
function handleTagClick() {
    router.push({ path: `/archive/tags/${props.tagname}` });
}
</script>

<template>
    <div :style="tagStyle" class="tag" @click="handleTagClick">
        <span class="hash">#</span>
        <span class="text">{{ displayTagname }}</span>
    </div>
</template>

<style scoped>
.tag {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: auto;
    /* Allow padding to define height */
    min-height: 1.8em;
    border-radius: 8px;
    /* Modern rounded corners */

    background: var(--tag-bg-color);
    color: var(--tag-text-color);

    font-family: 'Segoe UI', system-ui, sans-serif;
    font-weight: 600;
    line-height: 1;
    white-space: nowrap;

    cursor: pointer;
    user-select: none;
    overflow: hidden;

    /* Base Shadow */
    box-shadow:
        0 4px 6px -1px rgba(0, 0, 0, 0.1),
        0 2px 4px -1px rgba(0, 0, 0, 0.06),
        0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    /* Inner subtle border */

    transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

/* Glassy/Glossy Gradient Overlay */
.tag::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.3) 0%,
            rgba(255, 255, 255, 0) 50%,
            rgba(0, 0, 0, 0.05) 100%);
    z-index: 1;
}

/* Hash Icon Styling */
.hash {
    opacity: 0.6;
    margin-right: 4px;
    font-size: 0.9em;
    font-weight: 400;
    position: relative;
    z-index: 2;
    transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s ease;
}

.text {
    position: relative;
    z-index: 2;
    transition: letter-spacing 0.3s ease;
}

/* Hover Effects */
.tag:hover {
    transform: translateY(-2px) scale(1.05);
    /* Gentle lift & grow */
    box-shadow:
        0 10px 15px -3px var(--tag-shadow-color),
        0 4px 6px -2px rgba(0, 0, 0, 0.05);
    filter: brightness(1.1);
    /* Slightly brighter on hover */
}

/* Hover Interaction: Icon Rotate & Text Expand */
.tag:hover .hash {
    opacity: 1;
    transform: rotate(20deg) scale(1.2);
}

.tag:hover .text {
    letter-spacing: 0.5px;
}

/* Active/Click Effect */
.tag:active {
    transform: translateY(0) scale(0.95);
    box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}
</style>