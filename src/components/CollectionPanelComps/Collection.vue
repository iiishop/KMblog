<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import gsap from 'gsap';

const props = defineProps({
    name: String,
    imageUrl: String,
    createDate: String,
    count: Number,
});

const router = useRouter();
const collectionStyle = ref({});
const isAnimating = ref(false);
const cardRef = ref(null);

// 点击跳转到合集页面（使用 GSAP 实现流畅动画）
const navigateToCollection = (event) => {
    if (isAnimating.value) return;
    isAnimating.value = true;

    console.log('[Collection] Navigating to CollectionsPage with:', props.name);

    const card = event.currentTarget;
    const rect = card.getBoundingClientRect();

    // 创建过渡元素
    const transitionEl = document.createElement('div');
    transitionEl.className = 'collection-transition';
    Object.assign(transitionEl.style, {
        position: 'fixed',
        top: `${rect.top}px`,
        left: `${rect.left}px`,
        width: `${rect.width}px`,
        height: `${rect.height}px`,
        background: collectionStyle.value.backgroundColor || 'rgba(102, 126, 234, 0.4)',
        borderRadius: '1rem',
        zIndex: '9999',
        pointerEvents: 'none',
        transformOrigin: 'center center',
        overflow: 'hidden',
        perspective: '2000px'
    });

    // 克隆卡片内容
    const clone = card.cloneNode(true);
    clone.style.cssText = 'width: 100%; height: 100%; transform: none; box-shadow: none;';
    transitionEl.appendChild(clone);
    document.body.appendChild(transitionEl);

    // 使用 GSAP 时间线创建流畅动画
    const tl = gsap.timeline({
        onComplete: () => {
            // 导航到 Collections 页面，并传递要打开的 Collection 名称
            router.push({
                name: 'Collections',
                query: { open: props.name }
            }).then(() => {
                console.log('[Collection] Navigation successful');
                // 延迟清理，让 CollectionsPage 的入场动画先开始
                gsap.to(transitionEl, {
                    opacity: 0,
                    duration: 0.3,
                    onComplete: () => {
                        if (transitionEl.parentNode) {
                            transitionEl.parentNode.removeChild(transitionEl);
                        }
                        isAnimating.value = false;
                    }
                });
            }).catch(err => {
                console.error('[Collection] Navigation failed:', err);
                if (transitionEl.parentNode) {
                    transitionEl.parentNode.removeChild(transitionEl);
                }
                isAnimating.value = false;
            });
        }
    });

    // 计算目标位置
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    const scale = Math.min(window.innerWidth / rect.width, window.innerHeight / rect.height) * 0.8;

    // 第一阶段：放大到屏幕中心 (0-0.5s)
    tl.to(transitionEl, {
        x: centerX - rect.left - rect.width / 2,
        y: centerY - rect.top - rect.height / 2,
        scale: scale,
        opacity: 0.95,
        duration: 0.5,
        ease: 'power2.out'
    });

    // 第二阶段：3D 翻转并填充全屏 (0.5-1.1s)
    tl.to(transitionEl, {
        rotationY: 90,
        duration: 0.4,
        ease: 'power2.inOut'
    }, '+=0.1');

    tl.to(transitionEl, {
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        borderRadius: 0,
        x: 0,
        y: 0,
        scale: 1,
        duration: 0.2,
        ease: 'none'
    }, '-=0.2');
};

const getImageAverageColor = (image) => {
    return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        image.onload = () => {
            try {
                canvas.width = image.width;
                canvas.height = image.height;
                context.drawImage(image, 0, 0, image.width, image.height);
                const imageData = context.getImageData(0, 0, image.width, image.height).data;
                const colors = [];
                let ignoredPixelCount = 0;
                for (let i = 0; i < imageData.length; i += 4) {
                    const r = imageData[i];
                    const g = imageData[i + 1];
                    const b = imageData[i + 2];
                    // 忽略从 #cccccc 到 #ffffff 范围内的颜色
                    if (r >= 204 && g >= 204 && b >= 204) {
                        ignoredPixelCount++;
                    } else {
                        colors.push([r, g, b]);
                    }
                }
                const totalPixels = image.width * image.height;
                if (ignoredPixelCount < totalPixels / 2) {
                    const avgColor = colors.reduce((prev, curr) => {
                        return [prev[0] + curr[0], prev[1] + curr[1], prev[2] + curr[2]];
                    }, [0, 0, 0]).map(c => Math.round(c / colors.length));
                    resolve(`rgba(${avgColor[0]}, ${avgColor[1]}, ${avgColor[2]}, 0.4)`); // 设置透明度为40%
                } else {
                    const avgColor = colors.concat(Array(ignoredPixelCount).fill([255, 255, 255])).reduce((prev, curr) => {
                        return [prev[0] + curr[0], prev[1] + curr[1], prev[2] + curr[2]];
                    }, [0, 0, 0]).map(c => Math.round(c / totalPixels));
                    resolve(`rgba(${avgColor[0]}, ${avgColor[1]}, ${avgColor[2]}, 0.4)`); // 设置透明度为40%
                }
            } catch (error) {
                // 如果 canvas 操作失败（CORS 问题），使用默认颜色
                console.warn('Cannot extract color from image (CORS):', error);
                resolve('rgba(102, 126, 234, 0.4)');
            }
        };

        image.onerror = () => {
            console.warn('Error loading image for color extraction');
            resolve('rgba(102, 126, 234, 0.4)');
        };

        // 不设置 crossOrigin，避免 CORS 问题
        image.src = props.imageUrl;
    });
};

onMounted(async () => {
    const image = new Image();
    try {
        const color = await getImageAverageColor(image);
        collectionStyle.value = { backgroundColor: color };
    } catch (error) {
        console.error('Error loading image:', error);
    }
});

watch(() => props.imageUrl, async (newUrl) => {
    const image = new Image();
    try {
        const color = await getImageAverageColor(image);
        collectionStyle.value = { backgroundColor: color };
    } catch (error) {
        console.error('Error loading image:', error);
    }
});
</script>

<template>
    <div class="collection" :style="collectionStyle" @click="navigateToCollection">
        <img :src="imageUrl" />
        <div class="info">
            <h2>{{ name }}</h2>
            <p>{{ createDate }}</p>
            <p>内有{{ count }}篇文章</p>
        </div>
    </div>
</template>

<style scoped>
.collection {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
    border-radius: 1rem;
    overflow: hidden;
    transition: all 0.2s ease-in-out;
    cursor: pointer;
}

.collection:hover {
    transform: scale(1.02);
    box-shadow: 0px 0px 10px var(--collection-box-shadow);
}

.info {
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 100%;
}

img {
    width: auto;
    max-width: 50%;
    height: 8rem;
    object-fit: cover;
    /* 使用 -webkit-mask-image 和 mask-image 实现从左向右的透明渐变 */
    -webkit-mask-image: linear-gradient(to right, rgba(0, 0, 0, 1) 20%, rgba(0, 0, 0, 0));
    mask-image: linear-gradient(to right, rgba(0, 0, 0, 1) 20%, rgba(0, 0, 0, 0));
    -webkit-mask-size: 100% 100%;
    mask-size: 100% 100%;
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    transition: transform 0.2s ease;
}

p {
    color: var(--text-color);
    margin: 0.5rem 0 0;
}

.collection:hover img {
    transform: scale(1.05);
}
</style>