import fm from 'front-matter';

export function hasGalleryDescription(content) {
    if (!content || !content.trim()) return false;
    const trimmed = content.trim().toLowerCase();
    return !trimmed.startsWith('<!doctype') && !trimmed.startsWith('<html') && !trimmed.includes('<!doctype html>');
}

// Shared by gallery loading and editor previews; defaults must not diverge.
export async function loadGalleryImage(file) {
    const img = await loadImage(file.path);
    const name = file.name.replace(/\.[^.]+$/, '');
    return {
        id: generateImageId(file.path), src: file.path, alt: name, title: name,
        width: img.naturalWidth, height: img.naturalHeight,
        aspectRatio: img.naturalWidth / img.naturalHeight,
        dominantColor: await extractDominantColor(img),
        date: extractDateFromFilename(file.name) || new Date().toISOString(),
        tags: [], mdPath: file.path.replace(/\.[^.]+$/, '.md'), hasDescription: false,
        directory: file.directory, fileName: file.name
    };
}

export function applyGalleryMetadata(image, content) {
    const { attributes: metadata } = fm(content);
    return {
        ...image,
        title: metadata.title || image.title,
        date: metadata.date || image.date,
        aspectRatio: metadata.aspectRatio || image.aspectRatio,
        dominantColor: metadata.dominantColor || image.dominantColor,
        _originalTitle: image.title, _originalDate: image.date, _hasMetadata: true
    };
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
        // 无图片取色时回退到主题中性色
        return 'var(--theme-index)';
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
