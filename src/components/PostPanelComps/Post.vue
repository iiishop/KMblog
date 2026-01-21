<template>
    <div class="post-panel">
        <div class="image-panel" v-if="imageSrc && imageSrc !== loadingGif" :style="{ width: imagePanelWidth }">
            <img :src="imageSrc" alt="Image" @load="adjustImagePanelWidth" @error="handleImageError" />
        </div>
        <div class="content-panel">
            <div v-if="metadata" class="content-wrapper">

                <!-- Left Main Content Area -->
                <div class="main-content-area">
                    <div class="title-panel" @click="navigateToPost">
                        <p>{{ metadata.title }}</p>
                    </div>

                    <div class="pre-panel" @click="navigateToPost">
                        <pre>{{ metadata.pre }}</pre>
                    </div>
                </div>

                <!-- Right Meta Sidebar -->
                <div class="meta-sidebar">
                    <div class="meta-list">
                        <div class="meta-item category-row" v-if="lastCategory">
                            <IconCategory class="meta-icon" />
                            <router-link :to="categoryLink" class="meta-link">{{ lastCategory }}</router-link>
                        </div>
                        <div class="meta-item date-row" v-if="metadata.date">
                            <IconDate class="meta-icon" />
                            <router-link :to="archiveLink" class="meta-link">{{ metadata.date }}</router-link>
                        </div>
                    </div>

                    <div class="props-divider"></div>

                    <div class="tags-container">
                        <Tag v-for="(tag, index) in metadata.tags" :key="index" :tagname="tag" />
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, defineAsyncComponent } from 'vue';
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

// 定义导航到 PostPage 的函数
function navigateToPost() {
    const urlParts = props.markdownUrl.split('/');
    const mdName = urlParts.pop().replace('.md', '');
    const collection = urlParts.length > 3 ? urlParts[3] : null;

    router.push({
        name: 'PostPage',
        params: { collection, mdName }
    });
}
</script>

<style scoped>
.post-panel {
    gap: 1.5rem;
    display: flex;
    height: 16rem;
    /* Slightly taller for correct spacing */
    width: 100%;
    margin: auto;
    transition: all 0.3s ease;
}

/* Image Panel */
.image-panel {
    border-radius: 16px;
    height: 100%;
    overflow: hidden;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    position: relative;
    flex-shrink: 0;
}

.image-panel img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 16px;
    transition: transform 0.5s cubic-bezier(0.25, 1, 0.5, 1);
}

.post-panel:hover .image-panel img {
    transform: scale(1.1);
}

/* Content Panel - Glassmorphism & Modern Card */
.content-panel {
    padding: 1.5rem;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(12px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.6);
    box-shadow:
        0 4px 6px -1px rgba(0, 0, 0, 0.05),
        0 2px 4px -1px rgba(0, 0, 0, 0.03);

    width: 70%;
    /* Fallback */
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.content-panel:hover {
    /* transform: translateY(-5px); Removed to avoid interfering with clicks */
    box-shadow:
        0 20px 25px -5px rgba(0, 0, 0, 0.1),
        0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Sheen Effect */
.content-panel::after {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(to right,
            transparent 0%,
            rgba(255, 255, 255, 0.6) 50%,
            transparent 100%);
    transform: skewX(-25deg);
    transition: none;
    pointer-events: none;
}

.content-panel:hover::after {
    left: 200%;
    transition: left 0.8s ease-in-out;
}

/* --- Layout Structure --- */
.content-wrapper {
    display: flex;
    height: 100%;
    gap: 2rem;
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
    min-width: 160px;
    border-left: 1px solid rgba(0, 0, 0, 0.05);
    padding-left: 1.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 1.5rem;
}

/* --- Typography & Elements --- */

/* Title Panel - Restored Underline Effect */
.title-panel {
    display: flex;
    align-items: center;
    cursor: pointer;
    margin-bottom: 0.8rem;
    height: 3rem;
    /* Fixed height for alignment */
}

.title-panel p {
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-weight: 700;
    font-size: 1.6rem;
    color: var(--title-text-color, #2c3e50);
    position: relative;
    transition: color 0.2s ease;
    user-select: none;
    margin: 0;
    line-height: 1.2;
    display: inline-block;
}

.title-panel p::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -2px;
    width: 100%;
    height: 2px;
    background-color: currentColor;
    transform: scaleX(0);
    transform-origin: right;
    transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

.title-panel p:hover {
    color: var(--title-hover-color, #4ca1af);
}

.title-panel p:hover::after {
    transform-origin: left;
    transform: scaleX(1);
}

/* Preview Text */
.pre-panel {
    flex-grow: 1;
    cursor: pointer;
    border-radius: 8px;
    padding: 0.5rem 0;
    transition: opacity 0.3s ease;
}

.pre-panel:hover {
    opacity: 0.8;
}

.pre-panel pre {
    font-family: 'Inter', system-ui, sans-serif;
    font-size: 0.95rem;
    color: var(--pre-text-color, #555);
    white-space: pre-wrap;
    word-wrap: break-word;
    margin: 0;
    line-height: 1.6;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    line-clamp: 4;
    /* Show more lines now that it's narrower */
    -webkit-line-clamp: 4;
    overflow: hidden;
}

/* Sidebar Elements */
.meta-list {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    color: #666;
}

.meta-icon {
    width: 1.2rem;
    height: 1.2rem;
    opacity: 0.7;
}

.meta-link {
    text-decoration: none;
    color: inherit;
    font-weight: 500;
    transition: color 0.2s ease;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.meta-link:hover {
    color: var(--nav-link-hover-color, #4facfe);
}

.props-divider {
    height: 1px;
    background: rgba(0, 0, 0, 0.06);
    width: 100%;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

/* Responsive Handling */
@media (max-width: 768px) {
    .content-wrapper {
        flex-direction: column;
        gap: 1rem;
    }

    .meta-sidebar {
        width: 100%;
        border-left: none;
        padding-left: 0;
        border-top: 1px solid rgba(0, 0, 0, 0.05);
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

    .props-divider {
        display: none;
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
}
</style>