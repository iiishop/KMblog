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
import md from '@/components/MarkdownPanelComps/MarkdownRenender.js';
import fm from 'front-matter';

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

// 加载图片元数据（尺寸、宽高比）
async function loadImageMetadata(files) {
    console.log('[WaterfallPage] Loading metadata for', files.length, 'files');

    const promises = files.map(async (file) => {
        try {
            // 创建 Image 对象来加载图片并获取尺寸
            const img = await loadImage(file.path);

            // 提取文件名（不含扩展名）作为标题
            const lastDotIndex = file.name.lastIndexOf('.');
            const nameWithoutExt = lastDotIndex > 0
                ? file.name.substring(0, lastDotIndex)
                : file.name;

            // 生成唯一 ID
            const id = generateImageId(file.path);

            // 尝试从文件名提取日期（如果文件名包含日期格式）
            const extractedDate = extractDateFromFilename(file.name);
            const date = extractedDate || new Date().toISOString();

            // 提取图片主色调
            const dominantColor = await extractDominantColor(img);

            const imageData = {
                id,
                src: file.path,
                alt: nameWithoutExt,
                title: nameWithoutExt,
                width: img.naturalWidth,
                height: img.naturalHeight,
                aspectRatio: img.naturalWidth / img.naturalHeight,
                dominantColor, // 存储主色调到图片数据
                date,
                tags: [],
                mdPath: file.path.replace(/\.[^.]+$/, '.md'),
                hasDescription: false, // 将在下一步检查
                directory: file.directory,
                fileName: file.name
            };

            console.log('[WaterfallPage] Loaded metadata for:', file.name, imageData);
            return imageData;
        } catch (error) {
            console.error(`[WaterfallPage] Failed to load metadata for ${file.path}:`, error);
            return null;
        }
    });

    const results = await Promise.all(promises);
    const validResults = results.filter(img => img !== null);
    console.log('[WaterfallPage] Successfully loaded', validResults.length, 'images');
    return validResults;
}

// 加载单个图片的辅助函数
function loadImage(src) {
    return new Promise((resolve, reject) => {
        const img = new Image();

        // 设置超时（10秒）
        const timeout = setTimeout(() => {
            img.src = ''; // 取消加载
            reject(new Error(`Timeout loading image: ${src}`));
        }, 10000);

        img.onload = () => {
            clearTimeout(timeout);
            console.log('[WaterfallPage] Image loaded successfully:', src);
            resolve(img);
        };

        img.onerror = (e) => {
            clearTimeout(timeout);
            console.error('[WaterfallPage] Image load error:', src, e);
            reject(new Error(`Failed to load image: ${src}`));
        };

        img.src = src;
    });
}

// 提取图片主色调
async function extractDominantColor(img) {
    try {
        // 创建离屏 Canvas
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d', { willReadFrequently: true });

        // 设置 Canvas 尺寸为图片的采样区域
        // 为了性能，我们只分析中心区域的一个较小的样本
        const sampleSize = 100; // 采样区域大小
        canvas.width = sampleSize;
        canvas.height = sampleSize;

        // 计算中心区域的坐标
        const centerX = img.naturalWidth / 2;
        const centerY = img.naturalHeight / 2;
        const sourceX = Math.max(0, centerX - sampleSize / 2);
        const sourceY = Math.max(0, centerY - sampleSize / 2);
        const sourceWidth = Math.min(sampleSize, img.naturalWidth);
        const sourceHeight = Math.min(sampleSize, img.naturalHeight);

        // 使用 Canvas API 分析图片像素
        // 将图片的中心区域绘制到 Canvas 上
        ctx.drawImage(
            img,
            sourceX, sourceY, sourceWidth, sourceHeight,
            0, 0, sampleSize, sampleSize
        );

        // 获取像素数据
        const imageData = ctx.getImageData(0, 0, sampleSize, sampleSize);
        const pixels = imageData.data;

        // 计算中心区域平均色
        let totalR = 0;
        let totalG = 0;
        let totalB = 0;
        let pixelCount = 0;

        // 遍历所有像素（每个像素有 4 个值：R, G, B, A）
        for (let i = 0; i < pixels.length; i += 4) {
            const r = pixels[i];
            const g = pixels[i + 1];
            const b = pixels[i + 2];
            const a = pixels[i + 3];

            // 忽略透明或接近透明的像素
            if (a > 128) {
                totalR += r;
                totalG += g;
                totalB += b;
                pixelCount++;
            }
        }

        // 计算平均值
        const avgR = Math.round(totalR / pixelCount);
        const avgG = Math.round(totalG / pixelCount);
        const avgB = Math.round(totalB / pixelCount);

        // 转换 RGB 到 HSL 格式
        const hsl = rgbToHsl(avgR, avgG, avgB);

        // 返回 HSL 字符串格式
        return `hsl(${hsl.h}, ${hsl.s}%, ${hsl.l}%)`;
    } catch (error) {
        console.error('[WaterfallPage] Failed to extract dominant color:', error);
        // 返回默认颜色（紫色系）
        return 'hsl(250, 60%, 65%)';
    }
}

// 转换 RGB 到 HSL 格式
function rgbToHsl(r, g, b) {
    // 将 RGB 值归一化到 0-1 范围
    r /= 255;
    g /= 255;
    b /= 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const delta = max - min;

    let h = 0;
    let s = 0;
    let l = (max + min) / 2;

    if (delta !== 0) {
        // 计算饱和度
        s = l > 0.5 ? delta / (2 - max - min) : delta / (max + min);

        // 计算色相
        switch (max) {
            case r:
                h = ((g - b) / delta + (g < b ? 6 : 0)) / 6;
                break;
            case g:
                h = ((b - r) / delta + 2) / 6;
                break;
            case b:
                h = ((r - g) / delta + 4) / 6;
                break;
        }
    }

    // 转换为标准格式
    h = Math.round(h * 360);
    s = Math.round(s * 100);
    l = Math.round(l * 100);

    return { h, s, l };
}

// 生成图片唯一 ID
function generateImageId(path) {
    // 使用路径的哈希值作为 ID
    let hash = 0;
    for (let i = 0; i < path.length; i++) {
        const char = path.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return `img-${Math.abs(hash)}`;
}

// 从文件名提取日期
function extractDateFromFilename(filename) {
    // 尝试匹配常见的日期格式：YYYY-MM-DD, YYYYMMDD, YYYY_MM_DD
    const datePatterns = [
        /(\d{4})-(\d{2})-(\d{2})/,  // YYYY-MM-DD
        /(\d{4})(\d{2})(\d{2})/,    // YYYYMMDD
        /(\d{4})_(\d{2})_(\d{2})/   // YYYY_MM_DD
    ];

    for (const pattern of datePatterns) {
        const match = filename.match(pattern);
        if (match) {
            const [, year, month, day] = match;
            try {
                const dateStr = `${year}-${month}-${day}`;
                const date = new Date(dateStr);
                // 验证日期是否有效
                if (!isNaN(date.getTime())) {
                    return date.toISOString();
                }
            } catch (e) {
                console.warn('[WaterfallPage] Invalid date extracted from filename:', filename);
            }
        }
    }

    return null;
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

                // 12.4 渲染 Markdown 描述内容
                // 解析 front-matter（如果有）
                let bodyContent = markdownContent;
                try {
                    const parsed = fm(markdownContent);
                    bodyContent = parsed.body;
                } catch (e) {
                    // 如果没有 front-matter，使用原始内容
                    console.log('[WaterfallPage] No front-matter found, using raw content');
                }

                // 使用 markdown-it 渲染为 HTML
                const renderedHtml = md.render(bodyContent);
                imageDescription.value = renderedHtml;

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
