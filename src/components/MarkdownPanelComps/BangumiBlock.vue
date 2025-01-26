<template>
    <div class="bangumi-block">
        <div class="bangumi-info">
            <h2 class="bangumi-title">{{ title }} -- {{ fullRating }}</h2>
            <div class="bangumi-rating">
                <div class="rating-line">
                    <div v-for="(rating, index) in allRating" :key="index" class="rating-segment"
                        :style="{ flexBasis: rating.percent + '%', backgroundColor: getColor(index), borderRight: `2px solid ${secondaryColor}` }">
                        <span class="tooltip">{{ rating.numberOfPersons }} 人</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="bangumi-detail">
            <img :src="imageUrl || '/src/assets/loading.gif'" alt="Bangumi Cover" class="bangumi-cover" />
            <div class="bangumi-tags">
                <span v-for="tag in tags" :key="tag">{{ tag }}</span>
            </div>
            <div class="detail-info">
                <div class="bangumi-detail-info" v-html="info"></div>
                <a :href="props.bangumiurl" target="_blank" class="bangumi-link">查看详情</a>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import ColorThief from 'colorthief';

const props = defineProps({
    bangumiurl: String,
});

const imageUrl = ref('');
const title = ref('');
const tags = ref([]);
const fullRating = ref('');
const allRating = ref([]);
const info = ref('');
const primaryColor = ref('');
const secondaryColor = ref('');

const tooltip = ref({
    visible: false,
    numberOfPersons: 0,
    x: 0,
    y: 0
});

const fetchSubjectDetails = async () => {
    try {
        console.log(props.bangumiurl);
        console.log('Fetching bgm details...');
        const proxyUrl = 'https://api.allorigins.win/get?url=';
        const response = await axios.get(proxyUrl + encodeURIComponent(props.bangumiurl));
        console.log('bgm details fetched successfully.');

        const parser = new DOMParser();
        const doc = parser.parseFromString(response.data.contents, 'text/html');

        // 获取图片
        const imgElement = doc.querySelector('.cover img');
        console.log(imgElement);
        if (imgElement) {
            const originalUrl = imgElement.src;
            // 使用代理服务获取图片
            imageUrl.value = `https://api.allorigins.win/raw?url=${encodeURIComponent(originalUrl)}`;

            // 创建一个新的Image对象以获取颜色
            const img = new Image();
            img.crossOrigin = 'Anonymous';
            img.src = imageUrl.value;
            img.onload = () => {
                const colorThief = new ColorThief();
                const colors = colorThief.getPalette(img, 2);
                if (colors.length >= 2) {
                    primaryColor.value = `rgb(${colors[0].join(',')})`;
                    secondaryColor.value = `rgb(${colors[1].join(',')})`;
                }
            };
        }

        // 获取标题
        const titleElement = doc.querySelector('.nameSingle a');
        if (titleElement) {
            title.value = titleElement.title || titleElement.textContent.trim();
        }

        // 获取tag
        const tagElements = doc.querySelectorAll('.subject_tag_section .inner a.l:not([class*="meta"]) span');
        const tagArray = Array.from(tagElements).slice(0, 5).map(span => span.textContent.trim());
        tags.value = tagArray;

        // 获取总体评分
        const globalScoreElement = doc.querySelector('.global_score');
        if (globalScoreElement) {
            const numberElement = globalScoreElement.querySelector('.number');
            const descriptionElement = globalScoreElement.querySelector('.description');
            if (numberElement && descriptionElement) {
                fullRating.value = `${numberElement.textContent.trim()} ${descriptionElement.textContent.trim()}`;
            }
        }

        // 获取所有评分
        const allRatingElements = doc.querySelectorAll('.textTip');
        const ratings = Array.from(allRatingElements)
            .slice(0, 10)
            .map(element => {
                const title = element.getAttribute('title');
                const match = title.match(/(\d+(?:\.\d+)?)% \((\d+)人\)/);
                if (match) {
                    return {
                        percent: parseFloat(match[1]),
                        numberOfPersons: parseInt(match[2])
                    };
                }
                return null;
            })
            .filter(rating => rating !== null);
        allRating.value = ratings;

        // 获取详细信息
        const infoElement = doc.querySelector('#infobox');
        if (infoElement) {
            info.value = infoElement.outerHTML.trim();
        }

    } catch (error) {
        console.error('Error fetching game details:', error);
    }
};

const getColor = (index) => {
    if (!primaryColor.value) {
        return 'rgba(0, 0, 0, 0.1)'; // 默认颜色
    }
    const opacity = 1 - (index * 0.05);
    const [r, g, b] = primaryColor.value.match(/\d+/g).map(Number);
    const factor = 1 + index * 0.2; // 增加区分度
    const adjustedColor = `rgba(${Math.min(r * factor, 255)}, ${Math.min(g * factor, 255)}, ${Math.min(b * factor, 255)}, ${opacity})`;
    return adjustedColor;
};

const showTooltip = (numberOfPersons, event) => {
    tooltip.value.visible = true;
    tooltip.value.numberOfPersons = numberOfPersons;
    tooltip.value.x = event.screenX + 10;
    tooltip.value.y = event.screenY + 10;
    console.log(tooltip.value.x, tooltip.value.y);
    console.log(event.pageX, event.pageY);

};

const hideTooltip = () => {
    tooltip.value.visible = false;
};

onMounted(() => {
    fetchSubjectDetails();
});
</script>

<style scoped>
@keyframes gradient {
    0% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }

    100% {
        background-position: 0% 50%;
    }
}

.bangumi-block {
    background-size: 200% 200%;
    background-color: var(--tag-panel-background-color);
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
    animation: gradient 1s ease infinite;
    backdrop-filter: blur(10px);
}

.bangumi-info,
.bangumi-detail,
.bangumi-cover,
.bangumi-tags span,
.bangumi-detail-info,
.bangumi-link,
.rating-bars {
    backdrop-filter: blur(50px);
}

.bangumi-block:hover {
    transform: translateY(-2px);
}

.bangumi-title {
    font-size: 1.5rem;
    color: var(--tag-panel-text-color);
    margin: 0;
}

.bangumi-rating {
    color: var(--tag-panel-text-color);
    opacity: 0.8;
    font-size: 0.9rem;
}

.bangumi-detail {
    display: flex;
    gap: 1.5rem;
    align-items: flex-start;
}

.bangumi-cover {
    width: 180px;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.bangumi-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 1rem 0;
}

.bangumi-tags span {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    background-color: var(--tag-panel-box-shadow);
    color: var(--tag-panel-text-color);
    border-radius: 15px;
    font-size: 0.85rem;
    transition: all 0.3s ease;
    cursor: pointer;
}

.bangumi-tags span:hover {
    transform: translateY(-2px);
    background-color: var(--tag-panel-text-color);
    color: var(--tag-panel-background-color);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.detail-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.bangumi-detail-info {
    color: var(--tag-panel-text-color);
    font-size: 0.9rem;
    max-height: 10rem;
    overflow-y: scroll;
    border-radius: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    background-color: rgba(190, 190, 190, 0.1);
}

.bangumi-link {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: var(--tag-panel-box-shadow);
    color: var(--tag-panel-text-color);
    text-decoration: none;
    border-radius: 6px;
    transition: background-color 0.3s ease;
    width: fit-content;
}

.bangumi-link:hover {
    padding: 0.5rem 1rem;
    background-color: var(--tag-panel-text-color);
    color: var(--tag-panel-background-color);
}

.rating-line {
    display: flex;
    height: 9px;
    margin: 20px 0;
}

.rating-segment {
    height: 100%;
    transition: flex-basis 0.3s ease;
    position: relative;
}

.rating-segment:hover .tooltip {
    opacity: 1;
    transform: translateY(-10px);
}

.tooltip {
    position: absolute;
    background-color: #333;
    color: #fff;
    padding: 5px;
    border-radius: 5px;
    pointer-events: none;
    white-space: nowrap;
    opacity: 0;
    transform: translateY(0);
    transition: opacity 0.3s ease, transform 0.3s ease;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
}
</style>