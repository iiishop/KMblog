<template>
    <BaseLayout :show-tip-list="false" :show-info-list="false">
        <template #main>
            <WaterfallPanel ref="waterfallPanelRef" :images="galleryImages" @image-click="handleImageClick" />
        </template>
    </BaseLayout>

    <!-- 全屏图片模态框 -->
    <ImageModal v-if="selectedImage" :image="selectedImage" :description="imageDescription"
        :trigger-card-rect="triggerCardRect" @close="handleModalClose" />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import BaseLayout from './BaseLayout.vue';
import WaterfallPanel from '@/components/WaterfallPanel.vue';
import ImageModal from '@/components/WaterfallPanelComps/ImageModal.vue';
import { loadGalleryImage } from '@/utils/galleryImage';

// Refs
const waterfallPanelRef = ref(null);

// 状态管理
const galleryImages = ref([]);      // 图片列表
const selectedImage = ref(null);    // 当前选中图片
const imageDescription = ref('');   // 图片描述内容
const isModalOpen = ref(false);     // 模态框状态
const triggerCardRect = ref(null);  // 触发卡片的位置信息

// 支持的图片格式
const IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.avif'];

// 扫描 WaterfallGraph 目录获取所有文件
async function scanWaterfallDirectory() {
    const basePath = '/Posts/WaterfallGraph';
    const files = [];

    try {
        // 递归扫描目录
        await scanDirectory(basePath, files);
        console.log('[WaterfallPage] Scanned files:', files);
        return files;
    } catch (error) {
        console.error('[WaterfallPage] Error scanning directory:', error);
        return [];
    }
}

// 递归扫描目录的辅助函数
async function scanDirectory(path, files) {
    try {
        // 尝试获取目录内容
        // 由于浏览器无法直接访问文件系统，我们需要使用一个变通方法
        // 方案1: 使用 import.meta.glob (Vite特性)
        // 方案2: 维护一个图片索引文件
        // 这里我们使用 Vite 的 import.meta.glob 来动态导入

        // 注意：这需要在构建时确定，所以我们使用一个固定的 glob 模式
        const imageModules = import.meta.glob('/public/Posts/WaterfallGraph/**/*.{png,jpg,jpeg,gif,webp,svg,avif}', {
            eager: false,
            as: 'url'
        });

        console.log('[WaterfallPage] Image modules found:', Object.keys(imageModules));

        // 将模块路径转换为文件信息
        for (const path in imageModules) {
            // 移除 /public 前缀，因为在运行时这些文件会在根路径下
            const publicPath = path.replace('/public', '');
            const fileName = publicPath.split('/').pop();
            const directory = publicPath.substring(0, publicPath.lastIndexOf('/'));

            files.push({
                path: publicPath,
                name: fileName,
                directory: directory,
                fullPath: path
            });
        }

        console.log('[WaterfallPage] Processed files:', files);
    } catch (error) {
        console.error(`[WaterfallPage] Error scanning ${path}:`, error);
    }
}

// 过滤支持的图片格式
function filterImageFiles(files) {
    const filtered = files.filter(file => {
        // 处理特殊文件名（如包含 @ 符号的文件）
        // 获取最后一个点之后的内容作为扩展名
        const lastDotIndex = file.name.lastIndexOf('.');
        if (lastDotIndex === -1) {
            console.log(`[WaterfallPage] File has no extension: ${file.name}`);
            return false;
        }

        const ext = '.' + file.name.substring(lastDotIndex + 1).toLowerCase();
        const isSupported = IMAGE_EXTENSIONS.includes(ext);
        console.log(`[WaterfallPage] File: ${file.name}, Extension: ${ext}, Supported: ${isSupported}`);
        return isSupported;
    });
    console.log('[WaterfallPage] Filtered images:', filtered);
    return filtered;
}

async function loadImageMetadata(files) {
    const images = await Promise.all(files.map(file => loadGalleryImage(file).catch(error => {
        console.error(`[WaterfallPage] Failed to load metadata for ${file.path}:`, error);
        return null;
    })));
    return images.filter(Boolean);
}

// 检测关联的 .md 文件是否存在
async function checkMarkdownFiles(images) {
    const promises = images.map(async (image) => {
        try {
            // 尝试获取 .md 文件
            const response = await fetch(image.mdPath, { method: 'HEAD' });
            image.hasDescription = response.ok;
        } catch (error) {
            // 文件不存在或无法访问
            image.hasDescription = false;
        }
        return image;
    });

    return await Promise.all(promises);
}

// 按日期排序图片列表（最新的在前）
function sortImagesByDate(images) {
    return images.sort((a, b) => {
        const dateA = new Date(a.date);
        const dateB = new Date(b.date);
        return dateB - dateA; // 降序排列（最新的在前）
    });
}

// 图片加载逻辑
async function loadGalleryImages() {
    try {
        // 扫描 WaterfallGraph 目录获取图片文件
        const imageFiles = await scanWaterfallDirectory();

        // 过滤支持的图片格式
        const validImages = filterImageFiles(imageFiles);

        // 加载图片元数据（尺寸、宽高比）
        const imagesWithMetadata = await loadImageMetadata(validImages);

        // 检测关联的 .md 文件是否存在
        const imagesWithDescriptions = await checkMarkdownFiles(imagesWithMetadata);

        // 按日期排序图片列表（最新的在前）
        const sortedImages = sortImagesByDate(imagesWithDescriptions);

        galleryImages.value = sortedImages;

        console.log(`[WaterfallPage] Loaded ${sortedImages.length} images`);
    } catch (error) {
        console.error('[WaterfallPage] Failed to load gallery images:', error);
        galleryImages.value = [];
    }
}

// 事件处理

// 12.1 创建 handleImageClick 函数
async function handleImageClick(image, cardRect) {
    console.log('[WaterfallPage] Image clicked:', image, cardRect);

    // 保存触发卡片的位置信息
    triggerCardRect.value = cardRect;

    // 设置选中的图片
    selectedImage.value = image;
    isModalOpen.value = true;

    // 12.3 加载选中图片的描述文件
    if (image.hasDescription && image.mdPath) {
        try {
            console.log('[WaterfallPage] Loading description from:', image.mdPath);

            // 获取 markdown 文件内容
            const response = await fetch(image.mdPath);

            if (response.ok) {
                const markdownContent = await response.text();

                imageDescription.value = markdownContent;

                console.log('[WaterfallPage] Description loaded and rendered successfully');
            } else {
                console.warn('[WaterfallPage] Failed to load description:', response.status);
                imageDescription.value = '';
            }
        } catch (error) {
            console.error('[WaterfallPage] Error loading description:', error);
            imageDescription.value = '';
        }
    } else {
        // 没有描述文件
        console.log('[WaterfallPage] No description file for this image');
        imageDescription.value = '';
    }
}

// 12.2 创建 handleModalClose 函数
function handleModalClose() {
    console.log('[WaterfallPage] Closing modal');

    // 清除选中的图片
    selectedImage.value = null;
    isModalOpen.value = false;

    // 清除描述内容
    imageDescription.value = '';

    // 清除触发卡片位置信息
    triggerCardRect.value = null;

    // 重置所有卡片状态
    if (waterfallPanelRef.value && waterfallPanelRef.value.resetAllCardStates) {
        waterfallPanelRef.value.resetAllCardStates();
    }
}

onMounted(() => {
    loadGalleryImages();
});
</script>

<style scoped>
/* WaterfallPage specific styles */
</style>
