<template>
    <div class="post-panel">
        <div class="image-panel" v-if="imageSrc" :style="{ width: imagePanelWidth }">
            <img :src="imageSrc" alt="Image" @load="adjustImagePanelWidth" />
        </div>
        <div class="content-panel">
            <div v-if="metadata">
                <div class="title-panel">
                    <p>{{ metadata.title }}</p>
                </div>
                <div class="info-panel">
                    <div class="category-panel">
                        <IconCategory style="width: 1rem; height: 1rem;" v-if="lastCategory"/>
                        <a :href="categoryLink">{{ lastCategory }}</a>
                    </div>
                    <div class="date-panel">
                        <IconDate style="width: 1rem; height: 1rem;" v-if="metadata.date"/>
                        <a :href="archiveLink">{{ metadata.date }}</a>
                    </div>
                </div>
                <div class="pre-panel">
                    <pre>{{ metadata.pre }}</pre>
                </div>
                <div class="tag-panel">
                    <Tag v-for="(tag, index) in metadata.tags" :key="index" :tagname="tag" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import Tag from './PostPanelComps/Tag.vue';
import IconCategory from './icons/IconCategory.vue';
import IconDate from './icons/IconDate.vue';
import axios from 'axios';
import config from '@/config'; // 导入全局配置
import { parseMarkdown } from "@/utils";

// 定义 props
const props = defineProps({
    imageUrl: String,
    markdownUrl: String
});

// 定义 ref 来存储图片链接和 meta 数据
const imageSrc = ref(props.imageUrl || '');
const metadata = ref({});

// 定义 imagePanelWidth
const imagePanelWidth = ref('auto');

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
        const { meta } = parseMarkdown(content);
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
    if (url.startsWith('http') || url.startsWith('/')) {
        // 处理网络图片链接 或 本地绝对路径
        imageSrc.value = url;
    } else {
        // 处理本地相对路径图片文件
        imageSrc.value = new URL(url, import.meta.url).href;
    }
    console.log('Image source set to:', imageSrc.value);
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
        return `${config.ProjectUrl}/categories/${fullPath}/`;
    }
    return '#';
});

const archiveLink = computed(() => `${config.ProjectUrl}/Archive`);

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
</script>

<style scoped>
/* 添加一些样式 */

.post-panel {
    gap: 1rem;
    display: flex;
    height: 13rem;
    width: 100%;
    margin: auto;
}

.image-panel {
    border-radius: 1rem;
    height: 100%;
    width: 30%;
    overflow: hidden;
    box-shadow: 2px 2px 5px var(--image-box-shadow);
}

.image-panel img {
    width: 100%;
    height: 100%;
    border-radius: 1rem;
    transition: transform 0.2s ease;
}

.image-panel img:hover {
    transform: scale(1.2);
    transition: transform 0.2s ease;
}

.content-panel {
    padding: 1rem;
    border-radius: 1rem;
    background-color: var(--content-background-color);
    box-shadow: 1px 1px 5px var(--content-box-shadow);
    width: 70%;
    color: var(--content-text-color);
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    flex-shrink: 1;
    overflow: hidden;
    user-select: none;
    transition: all 0.2s ease;
}

.content-panel:hover {
    transform: scale(1.02);
}

.title-panel {
    display: flex;
    height: 3rem;
    align-items: center;
}

.title-panel p {
    font-family: 'Courier New', Courier, monospace;
    font-size: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    color: var(--title-text-color);
    transition: color 0.2s ease;
    text-decoration: none;
    user-select: none;
}

.title-panel p::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    width: 100%;
    height: 2px;
    background-color: currentColor;
    transform: scaleX(0);
    transform-origin: right;
    transition: transform 0.2s ease;
}

.title-panel p:hover {
    color: var(--title-hover-color);
}

.title-panel p:hover::after {
    transform-origin: left;
    transform: scaleX(1);
}

.info-panel {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 1.6rem;
}

.category-panel {
    display: flex;
    align-items: center;
    gap: 0.2rem;
    color: var(--info-text-color);
    margin: 0.2rem;
}

.category-panel a {
    text-decoration: none;
    display: flex;
    align-items: center;
    text-align: center;
    color: var(--info-text-color);
    position: relative;
    transition: color 0.2s ease;
}

.category-panel a::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    width: 100%;
    height: 2px;
    background-color: currentColor;
    transform: scaleX(0);
    transition: transform 0.2s ease;
}

.category-panel a:hover {
    color: var(--category-hover-color);
}

.category-panel a:hover::after {
    transform: scaleX(1);
}

.date-panel {
    display: flex;
    align-items: center;
    gap: 0.2rem;
    color: var(--info-text-color);
    margin: 0.2rem;
}

.date-panel a {
    text-decoration: none;
    display: flex;
    color: var(--info-text-color);
    align-items: center;
    text-align: center;
    position: relative;
    transition: color 0.2s ease;
}

.date-panel a:hover {
    color: var(--date-hover-color);
    animation: wave 1s infinite;
}

.pre-panel {
    font-family: 'Courier New', Courier, monospace;
    padding: 1rem;
    min-height: 5rem;
}

.pre-panel pre {
    font-family: 'Courier New', Courier, monospace;
    white-space: pre-wrap;
    word-wrap: break-word;
    margin: 0;
    padding: 0;
    line-height: 1.5;
    color: var(--pre-text-color);
    display: -webkit-box;
    -webkit-box-orient: vertical;
    line-clamp: 2;
    -webkit-line-clamp: 2;
    overflow: hidden;
}

.tag-panel {
    height: 2rem;
    display: flex;
    justify-content: flex-end;
    /* 使用 flex-end 代替 right */
    align-items: center;
    gap: 0.5rem;
    overflow-x: auto;
    /* 添加横向滚动条 */
    width: 100%;
    /* 确保有固定宽度 */
    white-space: nowrap;
    /* 确保内容不换行 */
}
@keyframes wave {
    0% {
        transform: translateY(0);
    }

    25% {
        transform: translateY(-2px);
    }

    50% {
        transform: translateY(0);
    }

    75% {
        transform: translateY(2px);
    }

    100% {
        transform: translateY(0);
    }
}
</style>