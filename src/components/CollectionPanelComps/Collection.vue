<script setup>
import { ref, onMounted, watch } from 'vue';

const props = defineProps({
    name: String,
    imageUrl: String,
    createDate: String,
    count: Number,
});

const collectionStyle = ref({});

const getImageAverageColor = (image) => {
    return new Promise((resolve, reject) => {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        image.crossOrigin = 'Anonymous';
        image.onload = () => {
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
        };
        image.onerror = reject;
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
    <div class="collection" :style="collectionStyle">
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