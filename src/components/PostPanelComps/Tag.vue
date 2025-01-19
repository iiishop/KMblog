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
    // 如果亮度大于 128，返回黑色，否则返回白色
    return yiq >= 128 ? '#000000' : '#FFFFFF';
}

// 初始化背景颜色和文字颜色
const backgroundColor = ref(randomColor());
const textColor = computed(() => getContrastColor(backgroundColor.value));

// 计算尺寸比例
const sizeFactor = computed(() => 1 + (props.count - 1) * 0.05);

// 计算样式
const tagStyle = computed(() => ({
    backgroundColor: backgroundColor.value,
    color: textColor.value,
    padding: `${0.7 * sizeFactor.value}rem ${0.4 * sizeFactor.value}rem`,
    fontSize: `${0.8 * sizeFactor.value}rem`,
    fontFamily: 'Arial, sans-serif',
    fontWeight: 'bold',
    cursor: 'pointer' // 添加手型光标
}));

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
        {{ displayTagname }}
    </div>
</template>

<style scoped>
.tag {
    text-align: center;
    flex-wrap: nowrap;
    height: 1.6rem;
    border-radius: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    white-space: nowrap;
}
</style>