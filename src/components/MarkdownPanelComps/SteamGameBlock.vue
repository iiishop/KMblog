<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({
    gameurl: String,
});

const imageUrl = ref('');
const title = ref('');
const description = ref('');
const latest_rating = ref('');
const all_rating = ref('');
const price = ref('');

const fetchGameDetails = async () => {
    try {
        console.log('Fetching game details...');
        const proxyUrl = 'https://api.allorigins.win/get?url=';
        const response = await axios.get(proxyUrl + encodeURIComponent(props.gameurl));
        console.log('Game details fetched successfully.');

        const parser = new DOMParser();
        const doc = parser.parseFromString(response.data.contents, 'text/html');

        // 获取游戏图片
        const imgElement = doc.querySelector('.game_header_image_full');
        if (imgElement) {
            imageUrl.value = imgElement.src;
        }

        // 获取游戏标题
        const titleElement = doc.querySelector('#appHubAppName');
        if (titleElement) {
            title.value = titleElement.textContent.trim();
        }

        // 获取游戏简介
        const descriptionElement = doc.querySelector('.game_description_snippet');
        if (descriptionElement) {
            description.value = descriptionElement.textContent.trim();
        }

        // 获取最新评分
        const latestRatingElement = doc.querySelector('.game_review_summary');
        if (latestRatingElement) {
            latest_rating.value = latestRatingElement.textContent.trim();
        }

        // 获取所有评分
        const allRatingElements = doc.querySelectorAll('.game_review_summary');
        if (allRatingElements.length > 1) {
            all_rating.value = allRatingElements[1].textContent.trim();
        }

        // 获取价格
        const priceElement = doc.querySelector('.game_purchase_discount');
        if (priceElement) {
            price.value = priceElement.outerHTML.trim();
        }
    } catch (error) {
        console.error('Error fetching game details:', error);
    }
};

onMounted(() => {
    fetchGameDetails();
});
</script>

<template>
    <div class="steam-game-block">
        <img :src="imageUrl" alt="Game Image" class="game-image" />
        <div class="game-info">
            <h2 class="game-title">{{ title }}</h2>
            <p class="game-description">{{ description }}</p>
            <div class="game-rating">
                <p>近期评价：{{ latest_rating }}</p>
                <p>全部评价：{{ all_rating }}</p>
            </div>
            <div class="game-price" v-html="price"></div>
            <a :href="props.gameUrl" target="_blank" class="game-button">查看详情</a>
        </div>
    </div>
</template>

<style scoped>
.steam-game-block {
    display: flex;
    flex-direction: column;
    align-items: center;
    background-color: #1b2838;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    transition: all 0.2s;
    width: 100%;
}

.steam-game-block:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.game-image {
    width: 100%;
    height: auto;
}

.game-info {
    padding: 1rem;
    text-align: center;
    color: #c7d5e0;
}

.game-title {
    font-size: 1.5rem;
    margin: 0.5rem 0;
}

.game-description {
    font-size: 1rem;
    margin: 0.5rem 0;
}

.game-rating {
    margin: 0.5rem 0;
}

.game-price {
    font-size: 1.2rem;
    font-weight: bold;
    margin: 0.5rem 0;
}

.game-button {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: #66c0f4;
    color: #fff;
    text-decoration: none;
    border-radius: 5px;
    transition: background-color 0.2s;
}

.game-button:hover {
    background-color: #4a9fd1;
}
</style>