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
        else {
            const priceElement = doc.querySelector('.game_purchase_price');
            if (priceElement) {
                price.value = priceElement.outerHTML.trim();
            }
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
        <div class="simple-info">
            <h2 class="game-title">{{ title }}</h2>
            <div class="game-rating">
                <p>近期评价：{{ latest_rating }}</p>
                <p>全部评价：{{ all_rating }}</p>
            </div>
        </div>
        <div class="game-info">
            <img :src="imageUrl || '/assets/loading.gif'" alt="Game Image" class="game-image" />
            <p class="game-description">{{ description }}</p>
            <div class="detail-info">
                <div class="game-price" v-html="price"></div>
                <a :href="props.gameurl" target="_blank" class="game-button">查看详情</a>
            </div>
        </div>
    </div>
</template>

<style scoped>
@keyframes gradientBackground {
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

.steam-game-block {
    display: flex;
    flex-direction: column;
    background: linear-gradient(145deg, #1b2838, #f49a66, #33a6bb);
    justify-content: space-between;
    background-size: 600% 600%;
    animation: gradientBackground 10s ease infinite;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    transition: all 0.2s;
    width: 100%;
    height: 15rem;
    margin-bottom: 1rem;
}

.steam-game-block:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.simple-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 0 1rem;
    background-color: #ccd1d66b;
    backdrop-filter: blur(10px);
    border-radius: 10px 10px 0 0;
    color: whitesmoke;
}

.game-title {
    font-size: 1.5rem;
    font-weight: bold;
}

.game-image {
    margin: 0 0 0 -3rem;
    width: 324px;
    height: 151px;
    border-radius: 10px;
}

.game-info {
    display: flex;
    justify-content: space-between;
    padding: 0rem 1rem 1rem 1rem;
    color: #c7d5e0;
}

.game-title {
    font-size: 1.5rem;
}

.game-description {
    margin-left: 0.5rem;
    margin-right: 0.5rem;
    margin-top: 0.5rem;
    font-size: 0.8rem;
}

.game-info .game-description {
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 7;
    line-clamp: 7;
    -webkit-box-orient: vertical;
}

.game-rating {}

.game-price {
    font-size: 1.2rem;
    font-weight: bold;
}

.game-button {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: #66a4f4;
    color: #fff;
    text-decoration: none;
    text-align: center;
    border-radius: 5px;
    transition: background-color 0.2s;
}

.game-button:hover {
    padding: 0.5rem 1rem;
    background-color: #4a9fd1;
}

.discount_block {}

.game_purchase_discount {}

:deep(.discount_original_price) {
    text-decoration: line-through;
    color: #6f777c;
}

:deep(.discount_pct) {
    color: #1ac028;
}

:deep(.discount_prices) {
    display: flex;
    flex-direction: column;
    align-items: center;
}

:deep(.discount_final_price) {
    font-size: 1.3rem;
    font-weight: bold;
    color: #fff;
}

.discount_block:hover {
    background-color: #4a9fd1;
}

.game_purchase_price {}
</style>