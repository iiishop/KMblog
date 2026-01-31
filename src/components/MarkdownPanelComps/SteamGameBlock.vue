<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import ColorThief from 'colorthief';

const props = defineProps({
    gameurl: String,
});

const gameData = ref(null);
const reviewData = ref(null); // Separate ref for review summary
const loading = ref(true);
const error = ref(false);
const primaryColor = ref('');
const secondaryColor = ref('');
// Computed for reviews
const allReviewText = computed(() => reviewData.value?.all?.query_summary?.review_score_desc || '');
const allReviewCount = computed(() => reviewData.value?.all?.query_summary?.total_reviews || 0);

// Computed properties for easy access
const bgStyle = computed(() => {
    if (primaryColor.value) {
        return {
            background: `linear-gradient(135deg, ${primaryColor.value} 0%, rgba(27, 40, 56, 1) 80%)`
        };
    }
    return {}; // Default fallbacks in CSS
});

const gamePrice = computed(() => {
    if (!gameData.value || !gameData.value.price_overview) {
        if (gameData.value?.is_free) return '免费开玩';
        return '';
    }
    return gameData.value.price_overview.final_formatted;
});

const discount = computed(() => {
    if (!gameData.value?.price_overview) return 0;
    return gameData.value.price_overview.discount_percent;
});

const headerImage = computed(() => {
    const url = gameData.value?.header_image || '';
    if (!url) return '';
    const clean = url.replace(/^https?:\/\//, '');
    return `https://images.weserv.nl/?url=${encodeURIComponent(clean)}&w=800&output=webp`;
});

const extractAppId = (url) => {
    const match = url.match(/\/app\/(\d+)/);
    return match ? match[1] : null;
};

const fetchProxy = async (targetUrl) => {
    const proxyGenerators = [
        (url) => `https://corsproxy.io/?${encodeURIComponent(url)}`,
        (url) => `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`
    ];
    for (const getProxyUrl of proxyGenerators) {
        try {
            const proxyUrl = getProxyUrl(targetUrl);
            // Create a clean axios instance without any default headers
            const response = await axios.get(proxyUrl, {
                headers: {
                    'X-Auth-Token': undefined  // Explicitly remove the auth token header
                }
            });
            if (response.data) return response.data;
        } catch (e) {
            console.warn(`Proxy request failed: ${e.message}`);
        }
    }
    return null;
}

const fetchGameDetails = async () => {
    const appId = extractAppId(props.gameurl);
    if (!appId) {
        error.value = true;
        loading.value = false;
        return;
    }

    try {
        console.log(`Fetching Steam data for AppID: ${appId}`);
        const storeUrl = `https://store.steampowered.com/api/appdetails?appids=${appId}&cc=cn&l=schinese`;
        const reviewUrl = `https://store.steampowered.com/appreviews/${appId}?json=1&l=schinese&purchase_type=all`;

        const [storeData, reviewResp] = await Promise.all([
            fetchProxy(storeUrl),
            fetchProxy(reviewUrl)
        ]);

        if (storeData && storeData[appId] && storeData[appId].success) {
            gameData.value = storeData[appId].data;
            if (reviewResp && reviewResp.success) {
                reviewData.value = { all: reviewResp };
            }

            // Extract Colors if header image is available
            if (headerImage.value) {
                const img = new Image();
                img.crossOrigin = 'Anonymous';
                img.src = headerImage.value;
                img.onload = () => {
                    try {
                        const colorThief = new ColorThief();
                        const palette = colorThief.getPalette(img, 2);
                        if (palette && palette.length >= 2) {
                            primaryColor.value = `rgb(${palette[0].join(',')})`;
                            secondaryColor.value = `rgb(${palette[1].join(',')})`;
                        }
                    } catch (e) {
                        console.warn("ColorThief failed", e);
                    }
                };
            }
        } else {
            error.value = true;
        }
    } catch (err) {
        console.error('Steam API Error:', err);
        error.value = true;
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchGameDetails();
});
</script>

<template>
    <div class="steam-card" :class="{ 'loading': loading, 'error': error }" :style="bgStyle">
        <div v-if="loading" class="state-msg">
            <span class="loader"></span> Loading Steam Info...
        </div>
        <div v-else-if="error" class="state-msg error-msg">
            Failed to load Steam info. <a :href="props.gameurl" target="_blank">Click to open store</a>
        </div>
        <div v-else class="card-content">
            <!-- Background Decoration -->
            <div class="bg-blur" :style="{ backgroundImage: `url(${headerImage})` }"></div>

            <div class="left-col">
                <div class="img-wrapper">
                    <img :src="headerImage" alt="Header" class="header-img" crossorigin="anonymous" />
                    <div class="discount-badge" v-if="discount > 0">-{{ discount }}%</div>
                </div>
            </div>

            <div class="right-col">
                <h2 class="game-title">
                    <a :href="props.gameurl" target="_blank">{{ gameData.name }}</a>
                </h2>

                <div class="meta-row">
                    <span class="release-date" v-if="gameData.release_date">
                        {{ gameData.release_date.date }}
                    </span>
                    <span class="review-summary" v-if="gameData.metacritic">
                        <span class="mc-score" :class="{ 'high': gameData.metacritic.score >= 80 }">{{
                            gameData.metacritic.score }}</span>
                    </span>
                    <span class="review-text" v-if="allReviewText">
                        {{ allReviewText }} ({{ allReviewCount }})
                    </span>
                </div>

                <div class="tags-row" v-if="gameData.genres && gameData.genres.length">
                    <span v-for="genre in gameData.genres.slice(0, 4)" :key="genre.id" class="tag">
                        {{ genre.description }}
                    </span>
                </div>

                <div class="game-desc" v-html="gameData.short_description"></div>

                <div class="action-row">
                    <div class="price-block">
                        <span class="original-price" v-if="discount > 0 && gameData.price_overview">
                            {{ gameData.price_overview.initial_formatted }}
                        </span>
                        <span class="final-price" :class="{ 'discounted': discount > 0 }">{{ gamePrice || '免费' }}</span>
                    </div>

                    <a :href="props.gameurl" target="_blank" class="store-btn">
                        <span class="steam-icon">
                            <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
                                <path
                                    d="M12 0C5.373 0 0 5.373 0 12c0 3.12 1.18 5.968 3.13 8.146l3.65-5.323c-.16-.628-.242-1.287-.242-1.966 0-4.322 3.504-7.826 7.826-7.826s7.826 3.504 7.826 7.826-3.504 7.826-7.826 7.826c-1.637 0-3.158-.5-4.432-1.353l-3.23 4.706C8.803 23.36 10.347 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm2.365 14.887c-1.595 0-2.887-1.292-2.887-2.887s1.292-2.887 2.887-2.887 2.887 1.292 2.887 2.887-1.292 2.887-2.887 2.887zm0-4.226c-.74 0-1.34.6-1.34 1.34s.6 1.34 1.34 1.34 1.34-.6 1.34-1.34-.6-1.34-1.34-1.34zm-7.79 6.208l1.69-2.464c1.17.48 2.45.626 3.65.348l-2.07 3.018c-1.127-.14-2.203-.455-3.27-.902z" />
                            </svg>
                        </span>
                        访问商店
                    </a>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.steam-card {
    position: relative;
    width: 100%;
    min-height: 180px;
    background: #171a21;
    /* Steam Dark Blue */
    color: #c7d5e0;
    border-radius: 8px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    font-family: Arial, Helvetica, sans-serif;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.steam-card:hover {
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
}

.state-msg {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 180px;
    gap: 10px;
    color: #8f98a0;
}

.loader {
    width: 20px;
    height: 20px;
    border: 3px solid rgba(255, 255, 255, 0.1);
    border-top-color: #66c0f4;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.card-content {
    display: flex;
    padding: 16px;
    gap: 20px;
    position: relative;
    z-index: 2;
}

/* Background Blur */
.bg-blur {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-size: cover;
    background-position: center;
    filter: blur(50px) brightness(0.4);
    z-index: 0;
    mask-image: linear-gradient(to right, rgba(0, 0, 0, 0.8), transparent);
    -webkit-mask-image: linear-gradient(to right, rgba(0, 0, 0, 0.8), transparent);
    opacity: 0.5;
}

/* Layout */
.left-col {
    flex-shrink: 0;
    width: 280px;
    position: relative;
}

.img-wrapper {
    position: relative;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.header-img {
    display: block;
    width: 100%;
    height: auto;
}

.discount-badge {
    position: absolute;
    bottom: 0;
    right: 0;
    background: #4c6b22;
    color: #beee11;
    font-weight: bold;
    font-size: 1.2rem;
    padding: 4px 8px;
    box-shadow: -2px -2px 5px rgba(0, 0, 0, 0.2);
}

.right-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    gap: 8px;
}

.game-title {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 500;
    line-height: 1.2;
}

.game-title a {
    color: #fff;
    text-decoration: none;
    transition: color 0.2s;
}

.game-title a:hover {
    color: #66c0f4;
}

.meta-row {
    font-size: 0.85rem;
    color: #8f98a0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.mc-score {
    background: #666;
    color: white;
    padding: 0 4px;
    border-radius: 2px;
    font-weight: bold;
}

.mc-score.high {
    background: #66c0f4;
    /* Steam Blue for high score, strictly usually green but sticking to theme */
}

.review-count {
    background: rgba(255, 255, 255, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.8rem;
}

.review-text {
    color: #66c0f4;
    font-weight: bold;
    font-size: 0.85rem;
}

.tags-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.tag {
    background: rgba(103, 193, 245, 0.2);
    color: #67c1f5;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    white-space: nowrap;
}

.game-desc {
    font-size: 0.9rem;
    line-height: 1.5;
    color: #acb2b8;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    -webkit-box-orient: vertical;
    flex: 1;
}

.action-row {
    margin-top: auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(0, 0, 0, 0.2);
    padding: 8px 12px;
    border-radius: 4px;
}

.price-block {
    display: flex;
    align-items: center;
    gap: 8px;
}

.original-price {
    color: #738895;
    text-decoration: line-through;
    font-size: 0.85rem;
}

.final-price {
    color: #66c0f4;
    font-size: 1.1rem;
    font-weight: bold;
}

.final-price.discounted {
    color: #beee11;
}

.store-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(90deg, #47bfff 0%, #1a44c2 100%);
    color: white !important;
    padding: 6px 16px;
    border-radius: 2px;
    font-size: 0.9rem;
    font-weight: 500;
    text-decoration: none !important;
    transition: box-shadow 0.2s ease, filter 0.2s ease;
    text-shadow: 1px 1px 0 rgba(0, 0, 0, 0.3);
}

.store-btn:hover {
    filter: brightness(1.2);
    box-shadow: 0 0 15px rgba(71, 191, 255, 0.6) !important;
}

/* 响应式设计 */
@media (max-width: 968px) {
    .card-content {
        flex-direction: column;
        padding: 12px;
    }

    .left-col {
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
    }

    .right-col {
        width: 100%;
    }

    .game-title {
        font-size: 1.3rem;
    }

    .meta-row {
        flex-wrap: wrap;
        gap: 8px;
    }

    .tags-row {
        gap: 5px;
    }

    .tag {
        font-size: 0.7rem;
        padding: 2px 6px;
    }

    .game-desc {
        font-size: 0.85rem;
        -webkit-line-clamp: 4;
    }

    .action-row {
        flex-direction: column;
        align-items: stretch;
        gap: 10px;
    }

    .price-block {
        justify-content: center;
    }

    .store-btn {
        width: 100%;
        justify-content: center;
    }
}

@media (max-width: 640px) {
    .steam-card {
        min-height: 150px;
    }

    .card-content {
        padding: 10px;
        gap: 12px;
    }

    .left-col {
        max-width: 100%;
    }

    .game-title {
        font-size: 1.2rem;
    }

    .meta-row {
        font-size: 0.8rem;
        gap: 6px;
    }

    .mc-score {
        font-size: 0.75rem;
    }

    .review-text {
        font-size: 0.8rem;
    }

    .game-desc {
        font-size: 0.8rem;
        -webkit-line-clamp: 3;
    }

    .action-row {
        padding: 6px 10px;
    }

    .final-price {
        font-size: 1rem;
    }

    .store-btn {
        padding: 8px 14px;
        font-size: 0.85rem;
    }
}

@media (max-width: 480px) {
    .card-content {
        padding: 8px;
        gap: 10px;
    }

    .game-title {
        font-size: 1.1rem;
    }

    .meta-row {
        font-size: 0.75rem;
    }

    .tags-row {
        gap: 4px;
    }

    .tag {
        font-size: 0.65rem;
        padding: 1px 5px;
    }

    .game-desc {
        font-size: 0.75rem;
    }

    .discount-badge {
        font-size: 1rem;
        padding: 3px 6px;
    }
}
</style>