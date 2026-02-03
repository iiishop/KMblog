<template>
    <div class="bangumi-card" :class="{ 'loaded': imageUrl }" :style="cardStyles">
        <!-- Background Blur Layer -->
        <div class="bg-blur" :style="{ backgroundImage: `url(${imageUrl})` }"></div>

        <div class="card-content">
            <!-- Left: Cover & Actions -->
            <div class="cover-column">
                <div class="cover-wrapper">
                    <img :src="imageUrl || '/assets/loading.gif'" alt="Cover" class="cover-img" crossorigin="anonymous"
                        @load="onImageLoad" />
                    <div class="cover-shadow" :style="{ backgroundImage: `url(${imageUrl})` }"></div>
                </div>
                <a :href="props.bangumiurl" target="_blank" class="action-btn">
                    <span class="btn-icon">
                        <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                            <path
                                d="M14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3m-2 16H5V5h7V3H5c-1.11 0-2 .89-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7z" />
                        </svg>
                    </span>
                    <span>前往 Bangumi</span>
                </a>
            </div>

            <!-- Right: Details -->
            <div class="info-column">
                <div class="header-section">
                    <h2 class="title">{{ title || 'Loading...' }}</h2>
                    <div class="rating-badge" v-if="ratingData.total > 0">
                        <div class="score-box">
                            <span class="score-val">{{ ratingData.score }}</span>
                            <span class="score-suffix">/ 10</span>
                        </div>
                        <span class="score-count">{{ ratingData.total }} 人评分</span>
                    </div>
                </div>

                <!-- Rating Distribution Bar -->
                <div class="distribution-bar" v-if="allRating.length > 0">
                    <div v-for="(rating, index) in allRating" :key="index" class="dist-segment"
                        :style="{ width: rating.percent + '%', backgroundColor: getSegmentColor(index) }"
                        :title="`${rating.score}分: ${rating.numberOfPersons}人 (${rating.percent.toFixed(1)}%)`">
                    </div>
                </div>

                <!-- Tags -->
                <div class="tags-container" v-if="tags.length">
                    <span v-for="tag in tags" :key="tag" class="tag-pill">{{ tag }}</span>
                </div>

                <!-- Warning/Summary -->
                <div class="summary-section" v-if="summary">
                    <div class="summary-text" :class="{ collapsed: isSummaryCollapsed }" @click="toggleSummary">
                        {{ summary }}
                    </div>
                </div>

                <!-- Info Grid -->
                <div class="infobox-grid">
                    <div v-for="(item, idx) in infobox" :key="idx" class="info-item">
                        <span class="info-key">{{ item.key }}</span>
                        <span class="info-val">{{ item.value }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import axios from 'axios';
import ColorThief from 'colorthief';

const props = defineProps({
    bangumiurl: String,
});

const imageUrl = ref('');
const title = ref('');
const tags = ref([]);
const ratingData = ref({ score: 0, total: 0 });
const allRating = ref([]);
const infobox = ref([]);
const summary = ref('');
const primaryColor = ref('');
const secondaryColor = ref('');
const isSummaryCollapsed = ref(true);

const toggleSummary = () => {
    isSummaryCollapsed.value = !isSummaryCollapsed.value;
};

const cardStyles = computed(() => {
    return {
        '--theme-color': primaryColor.value || '#3b82f6',
        '--theme-secondary': secondaryColor.value || '#06b6d4',
        '--theme-bg-opacity': primaryColor.value ? '0.1' : '0.05'
    };
});

const onImageLoad = (e) => {
    const img = e.target;
    if (img.src.includes('loading.gif')) return;

    try {
        const colorThief = new ColorThief();
        const colors = colorThief.getPalette(img, 3);
        if (colors && colors.length >= 2) {
            primaryColor.value = `rgb(${colors[0].join(',')})`;
            secondaryColor.value = `rgb(${colors[1].join(',')})`;
        }
    } catch (err) {
        console.warn('Color thief error', err);
    }
};

const getSegmentColor = (index) => {
    // index 0 = 10 points, index 9 = 1 point
    // Distinct colors for each rating level
    const colors = [
        '#22c55e', // 10: Green
        '#84cc16', // 9: Lime
        '#a3e635', // 8: Light Lime
        '#facc15', // 7: Yellow
        '#fcd34d', // 6: Light Yellow
        '#fbbf24', // 5: Amber
        '#fb923c', // 4: Orange
        '#f87171', // 3: Red-Orange
        '#ef4444', // 2: Red
        '#dc2626'  // 1: Dark Red
    ];
    return colors[index] || '#ccc';
};

const convertToWeserv = (url) => {
    if (!url) return '';
    const clean = url.replace(/^https?:\/\//, '');
    return `https://images.weserv.nl/?url=${encodeURIComponent(clean)}&w=800&output=webp`;
};

const fetchSubjectDetails = async () => {
    try {
        const subjectIdMatch = props.bangumiurl.match(/\/subject\/(\d+)/);
        if (!subjectIdMatch) {
            throw new Error("Invalid Bangumi URL");
        }
        const subjectId = subjectIdMatch[1];

        // API call - 清空自定义请求头避免 CORS 预检失败
        const apiUrl = `https://api.bgm.tv/v0/subjects/${subjectId}`;
        const response = await axios.get(apiUrl, {
            headers: {
                'X-Auth-Token': undefined  // Explicitly remove the auth token header
            }
        });
        const data = response.data;

        // Image - Use weserv proxy to avoid CORS
        if (data.images && data.images.large) {
            imageUrl.value = convertToWeserv(data.images.large);
        }

        // Basic Info
        title.value = data.name_cn || data.name;
        summary.value = data.summary || '';

        // Tags
        if (data.tags) {
            tags.value = data.tags.slice(0, 6).map(t => t.name);
        }

        // Rating
        if (data.rating) {
            ratingData.value = {
                score: data.rating.score,
                total: data.rating.total,
                count: data.rating.count
            };

            // Calc distribution
            const total = data.rating.total || 1;
            allRating.value = Array.from({ length: 10 }, (_, i) => {
                const score = 10 - i;
                const count = data.rating.count ? (data.rating.count[score] || 0) : 0;
                return {
                    score,
                    numberOfPersons: count,
                    percent: (count / total) * 100
                };
            });
        }

        // Infobox
        if (data.infobox) {
            // Filter some common useful keys
            infobox.value = data.infobox
                .filter(item => ['放送开始', '又名', '导演', '制作', '开发'].includes(item.key) || item.key.length < 5) // Simple heuristic to keep tidy
                .slice(0, 8)
                .map(item => {
                    let val = '';
                    if (Array.isArray(item.value)) {
                        val = item.value.map(v => v.v).join('、');
                    } else {
                        val = item.value;
                    }
                    return { key: item.key, value: val };
                });
        }

    } catch (error) {
        console.error('Error fetching bgm details:', error);
        title.value = 'Failed to load info';
    }
};

onMounted(() => {
    fetchSubjectDetails();
});
</script>

<style scoped>
.bangumi-card {
    position: relative;
    width: 100%;
    overflow: hidden;
    border-radius: 16px;
    background: #fff;
    /* Fallback */
    /* Dynamic Theme applied via inline styles */
    box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.1);
    /* Removed translate/scale transitions */
    transition: box-shadow 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    color: #333;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    isolation: isolate;
}

.bangumi-card:hover {
    /* Removed transform/scale */
    /* transform: translateY(-4px) scale(1.005); */
    box-shadow: 0 5px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Background Layers */
.bg-blur {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-size: cover;
    background-position: center;
    filter: blur(60px) saturate(1.8);
    opacity: 0.5;
    z-index: -2;
    transition: opacity 1s ease;
}

/* Dark mode support check (if global var exists, otherwise default) */
@media (prefers-color-scheme: dark) {
    .bangumi-card {
        color: #f0f0f0;
    }
}

.card-content {
    display: flex;
    padding: 1.5rem;
    gap: 1.5rem;
    position: relative;
    z-index: 1;
    border-radius: 1rem;
}

/* Left Column */
.cover-column {
    display: flex;
    flex-direction: column;
    width: 160px;
    /* Slightly larger for better detail */
    gap: 1rem;
    flex-shrink: 0;
}

.cover-wrapper {
    position: relative;
    width: 100%;
    /* Remove fixed aspect-ratio to respect original image dimensions */
    border-radius: 12px;
    perspective: 1000px;
    /* Ensure container takes height of image */
    display: flex;
}

.cover-img {
    width: 100%;
    height: auto;
    /* Maintain aspect ratio */
    min-height: 200px;
    /* Prevent layout collapse before load */
    object-fit: contain;
    /* Ensure full image is visible */
    border-radius: 12px;
    position: relative;
    z-index: 2;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    /* Removed transform transition */
    background-color: rgba(255, 255, 255, 0.1);
    /* Placeholder bg */
}

.cover-shadow {
    position: absolute;
    top: 8%;
    left: 0;
    width: 100%;
    height: 95%;
    /* Adjust to sit behind the image cleanly */
    background-size: cover;
    background-position: center;
    filter: blur(15px);
    opacity: 0.6;
    z-index: 1;
    transition: opacity 0.5s;
    transform: scale(0.95) translateY(5px);
    border-radius: 12px;
}


.action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    /* Force full width to prevent shrinking */
    box-sizing: border-box;
    gap: 6px;
    background: var(--theme-color);
    color: white !important;
    /* Override .markdown a color */
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    text-decoration: none;
    transition: filter 0.2s ease;
    box-shadow: 0 4px 10px -2px var(--theme-bg-opacity);
    /* Hacky use of opacity var for shadow hue needs rgb */
}

.action-btn:hover {
    filter: brightness(1.1);
    /* Explicitly reset properties to prevent global .markdown a:hover interference */
    padding: 8px 12px !important;
    text-decoration: none !important;
    box-shadow: 0 4px 10px -2px var(--theme-bg-opacity) !important;
}


/* Right Column */
.info-column {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    min-width: 0;
    /* Prevent flex overflow */
}

.header-section {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
}

.title {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 800;
    line-height: 1.3;
    background: linear-gradient(90deg, #333, #666);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

@media (prefers-color-scheme: dark) {
    .title {
        background: linear-gradient(90deg, #fff, #bbb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
}

.rating-badge {
    text-align: right;
    flex-shrink: 0;
}

.score-box {
    display: flex;
    align-items: baseline;
    justify-content: flex-end;
    gap: 2px;
    color: var(--theme-color);
}

.score-val {
    font-size: 2rem;
    font-weight: 900;
    line-height: 1;
}

.score-suffix {
    font-size: 0.9rem;
    font-weight: 600;
    opacity: 0.6;
}

.score-count {
    display: block;
    font-size: 0.75rem;
    opacity: 0.5;
    margin-top: 2px;
}

/* Distribution Bar */
.distribution-bar {
    display: flex;
    height: 6px;
    width: 100%;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 3px;
    overflow: hidden;
    margin-top: 0.2rem;
}

.dist-segment {
    height: 100%;
    transition: width 1s cubic-bezier(0.22, 1, 0.36, 1);
}

/* Tags */
.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.tag-pill {
    font-size: 0.75rem;
    padding: 4px 10px;
    background: var(--theme-bg-opacity);
    /* this variable returns e.g. 0.1, need rgba trick ideally but let's use background color with opacity if possible. Actually it is being reused. */
    background: rgba(128, 128, 128, 0.1);
    border-radius: 12px;
    transition: all 0.2s;
    cursor: default;
}

.tag-pill:hover {
    background: var(--theme-color);
    color: white;
}

/* Summary */
.summary-text {
    font-size: 0.9rem;
    line-height: 1.6;
    margin: 0;
    opacity: 0.8;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s;
}

.summary-text.collapsed {
    -webkit-line-clamp: 3;
    line-clamp: 3;
}

.summary-text:hover {
    opacity: 1;
}

/* Infobox Grid */
.infobox-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 8px 16px;
    margin-top: auto;
    padding-top: 1rem;
    border-top: 1px dashed rgba(0, 0, 0, 0.1);
}

.info-item {
    font-size: 0.8rem;
    display: flex;
    flex-direction: column;
}

.info-key {
    opacity: 0.5;
    font-size: 0.7rem;
    margin-bottom: 2px;
}

.info-val {
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* 响应式设计 */
@media (max-width: 968px) {
    .card-content {
        flex-direction: column;
        padding: 1.25rem;
        gap: 1.25rem;
    }

    .cover-column {
        width: 100%;
        max-width: 280px;
        margin: 0 auto;
    }

    .info-column {
        width: 100%;
    }

    .header-section {
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 0.75rem;
    }

    .title {
        font-size: 1.3rem;
    }

    .rating-badge {
        text-align: center;
        width: 100%;
    }

    .score-box {
        justify-content: center;
    }

    .tags-container {
        justify-content: center;
    }

    .summary-text {
        text-align: left;
    }

    .infobox-grid {
        grid-template-columns: 1fr 1fr;
        text-align: left;
    }
}

@media (max-width: 640px) {
    .bangumi-card {
        border-radius: 12px;
    }

    .card-content {
        padding: 1rem;
        gap: 1rem;
    }

    .cover-column {
        width: 100%;
        max-width: 200px;
        gap: 0.75rem;
    }

    .cover-wrapper {
        border-radius: 10px;
    }

    .cover-img {
        min-height: 150px;
        border-radius: 10px;
    }

    .action-btn {
        padding: 7px 10px;
        font-size: 0.8rem;
    }

    .btn-icon svg {
        width: 14px;
        height: 14px;
    }

    .title {
        font-size: 1.2rem;
    }

    .score-val {
        font-size: 1.75rem;
    }

    .score-suffix {
        font-size: 0.85rem;
    }

    .score-count {
        font-size: 0.7rem;
    }

    .distribution-bar {
        height: 5px;
    }

    .tags-container {
        gap: 5px;
    }

    .tag-pill {
        font-size: 0.7rem;
        padding: 3px 8px;
    }

    .summary-text {
        font-size: 0.85rem;
    }

    .summary-text.collapsed {
        -webkit-line-clamp: 2;
        line-clamp: 2;
    }

    .infobox-grid {
        gap: 6px 12px;
        padding-top: 0.75rem;
    }

    .info-item {
        font-size: 0.75rem;
    }

    .info-key {
        font-size: 0.65rem;
    }
}

@media (max-width: 480px) {
    .card-content {
        padding: 0.75rem;
        gap: 0.75rem;
    }

    .cover-column {
        max-width: 160px;
    }

    .cover-img {
        min-height: 120px;
    }

    .action-btn {
        padding: 6px 8px;
        font-size: 0.75rem;
        gap: 4px;
    }

    .btn-icon svg {
        width: 12px;
        height: 12px;
    }

    .title {
        font-size: 1.1rem;
    }

    .score-val {
        font-size: 1.5rem;
    }

    .score-suffix {
        font-size: 0.8rem;
    }

    .score-count {
        font-size: 0.65rem;
    }

    .distribution-bar {
        height: 4px;
    }

    .tag-pill {
        font-size: 0.65rem;
        padding: 2px 6px;
    }

    .summary-text {
        font-size: 0.8rem;
    }

    .infobox-grid {
        grid-template-columns: 1fr;
        gap: 6px;
    }

    .info-item {
        font-size: 0.7rem;
    }
}

/* 平板横屏优化 */
@media (min-width: 641px) and (max-width: 968px) and (orientation: landscape) {
    .card-content {
        flex-direction: row;
    }

    .cover-column {
        width: 200px;
        max-width: 200px;
    }

    .header-section {
        flex-direction: row;
        align-items: flex-start;
        text-align: left;
    }

    .rating-badge {
        text-align: right;
    }

    .tags-container {
        justify-content: flex-start;
    }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
    .action-btn {
        min-height: 44px;
        /* iOS 推荐的最小触摸目标 */
    }

    .tag-pill {
        min-height: 32px;
        display: inline-flex;
        align-items: center;
    }

    .summary-text {
        cursor: pointer;
        -webkit-tap-highlight-color: rgba(0, 0, 0, 0.1);
    }
}
</style>