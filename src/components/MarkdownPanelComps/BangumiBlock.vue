<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({
    bangumiurl: String,
});

const imageUrl = ref('');
const title = ref('');
const tags = ref([]);
const fullRating = ref('');
const allRating = ref([]);
const info = ref('');

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

onMounted(() => {
    fetchSubjectDetails();
});
</script>

<template>
    <div class="bangumi-block">
        <div class="bangumi-info">
            <h2 class="bangumi-title">{{ title }} -- {{ fullRating }}</h2>
            <div class="bangumi-rating">
                <ul class="rating-bars">
                    <li v-for="(rating, index) in allRating" :key="index" class="rating-bar">
                        <div class="bar-container">
                            <div class="bar" :style="{ height: rating.percent + '%' }">
                                <span class="bar-tooltip">{{ rating.numberOfPersons }}人</span>
                            </div>
                        </div>
                        <span class="bar-label">{{ rating.percent }}%</span>
                        <span class="bar-star">{{ 10 - index}}⭐</span>
                    </li>
                </ul>
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

<style scoped>
.bangumi-block {
    background-color: var(--tag-panel-background-color);
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
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

.rating-bars {
    list-style: none;
    padding: 0 0.4rem;
    margin: 1rem 0;
    width: 100%;
    height: 100px;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    background-color: rgba(0, 0, 0, 0.1);
    box-shadow: 1px 1px 10px 1px rgba(0, 0, 0, 0.1);
    border-radius: 1rem;
}

.rating-bar {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.bar-container {
    flex-grow: 1;
    background-color: rgba(136, 136, 136, 0.5);
    width: 16px;
    border-radius: 6px 6px 0 0px;
    position: relative;
}

.bar {
    width: 100%;
    bottom: 0px;
    border-radius: 50% 50% 0 0px;
    background-color: var(--tag-panel-text-color);
    transition: width 0.3s ease;
    position: absolute;
}

.bar-tooltip {
    position: absolute;
    top: -30px;
    right: 0;
    width: auto;
    background-color: var(--tag-panel-text-color);
    color: var(--tag-panel-background-color);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: auto;
    opacity: 0;
    transform: translateY(5px);
    transition: opacity 0.3s ease, transform 0.3s ease;
    pointer-events: none;
    white-space: nowrap;
}

.bar-container:hover .bar-tooltip {
    opacity: 1;
    transform: translateY(0);
}

.bar-label {
    min-width: 40px;
    text-align: right;
    font-size: 0.8rem;
    color: var(--tag-panel-text-color);
}

.bar-star {
    font-size: 0.8rem;
    color: var(--tag-panel-text-color);
    margin: 0;

}

/* @media (max-width: 768px) {
    .bangumi-detail {
        flex-direction: column;
    }

    .bangumi-cover {
        width: 100%;
        max-width: 300px;
        margin: 0 auto;
    }
} */
</style>