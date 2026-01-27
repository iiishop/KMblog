<script setup>
import { ref, onMounted, computed, onUnmounted, watch } from 'vue';
import axios from 'axios';

const props = defineProps({
    videourl: String,
});

const videoData = ref(null);
const creatorStats = ref(null);
const loading = ref(true);
const error = ref(false);
const proxiedCover = ref('');
const proxiedAvatar = ref('');
const themeColor = ref('#FB7299');
const accentColor = ref('#FF8FB3');
const secondaryColor = ref('#23ADE5');

// Level color mapping (lv 0..6) and contrast helper
// lv index: 0,1,2,3,4,5,6
// 3 -> green, 4 -> yellow, 5 -> orange, 6 -> red
const _lvColors = ['#6B7280', '#4AA9FF', '#23BDB0', '#44D07A', '#FFD166', '#FF8B4B', '#FF4B4B'];

const hexToRgb = (hex) => {
    const raw = hex.replace('#', '');
    const bigint = parseInt(raw, 16);
    return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255];
};

const luminance = (r, g, b) => {
    // perceived brightness
    return (0.299 * r + 0.587 * g + 0.114 * b);
};

const lvBg = computed(() => {
    if (!creatorStats?.value) return _lvColors[0];
    const lv = Math.max(0, Math.min(6, Number(creatorStats.value.level || 0)));
    return _lvColors[lv];
});

const lvText = computed(() => {
    const [r, g, b] = hexToRgb(lvBg.value);
    return luminance(r, g, b) > 160 ? '#000000' : '#FFFFFF';
});

// Mouse interaction for parallax
const cardRef = ref(null);
const mouseX = ref(0);
const mouseY = ref(0);
const isHovering = ref(false);

const handleMouseMove = (e) => {
    if (!cardRef.value) return;
    const rect = cardRef.value.getBoundingClientRect();
    mouseX.value = (e.clientX - rect.left) / rect.width - 0.5;
    mouseY.value = (e.clientY - rect.top) / rect.height - 0.5;
};

const handleMouseEnter = () => { isHovering.value = true; };
const handleMouseLeave = () => {
    isHovering.value = false;
    mouseX.value = 0;
    mouseY.value = 0;
};

const cardStyle = computed(() => {
    const rotateX = isHovering.value ? mouseY.value * -5 : 0;
    const rotateY = isHovering.value ? mouseX.value * 5 : 0;
    return {
        transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
    };
});

// Extract BV号
const extractBvid = (url) => {
    const match = url.match(/BV[a-zA-Z0-9]+/);
    return match ? match[0] : null;
};

// Format large numbers
const formatStat = (num) => {
    if (!num && num !== 0) return { display: '0', raw: 0 };
    const raw = num;
    let display = '';
    if (num >= 100000000) display = (num / 100000000).toFixed(1) + '亿';
    else if (num >= 10000) display = (num / 10000).toFixed(1) + '万';
    else display = num.toString();
    return { display, raw };
};

// Format duration
const formatDuration = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    return `${m}:${String(s).padStart(2, '0')}`;
};

// Format date
const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '.');
};

const videoUrl = computed(() => props.videourl);

// Visual stats
const visualStats = computed(() => {
    if (!videoData.value?.stat) return [];
    const stat = videoData.value.stat;
    const maxView = stat.view || 1;
    return [
        { label: 'PLAYS', ...formatStat(stat.view), percent: 100 },
        { label: 'LIKES', ...formatStat(stat.like), percent: Math.min((stat.like / maxView) * 100, 100) },
        { label: 'COINS', ...formatStat(stat.coin), percent: Math.min((stat.coin / maxView) * 100, 100) },
        { label: 'FAVS', ...formatStat(stat.favorite), percent: Math.min((stat.favorite / maxView) * 100, 100) },
    ];
});

const fetchProxy = async (targetUrl) => {
    const proxyGenerators = [
        (url) => `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`,
        (url) => `https://corsproxy.io/?${encodeURIComponent(url)}`,
        (url) => `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(url)}`
    ];
    for (const getProxyUrl of proxyGenerators) {
        try {
            const proxyUrl = getProxyUrl(targetUrl);
            // 不发送自定义请求头（如 x-auth-token），避免 CORS 预检失败
            const response = await axios.get(proxyUrl, {
                headers: {}  // 清空自定义请求头
            });
            if (response.data) return response.data;
        } catch (e) {
            console.warn(`Proxy request failed for ${targetUrl}: ${e.message}`);
        }
    }
    return null;
};

const fetchVideoDetails = async () => {
    const bvid = extractBvid(props.videourl);
    if (!bvid) {
        error.value = true;
        loading.value = false;
        return;
    }

    try {
        const apiUrl = `https://api.bilibili.com/x/web-interface/view?bvid=${bvid}`;
        const data = await fetchProxy(apiUrl);

        if (data && data.code === 0 && data.data) {
            videoData.value = data.data;

            // Fetch Creator Stats (Fans, Level, Sign)
            const mid = data.data.owner.mid;
            const cardApi = `https://api.bilibili.com/x/web-interface/card?mid=${mid}`;
            const cardData = await fetchProxy(cardApi);
            if (cardData && cardData.code === 0) {
                creatorStats.value = {
                    follower: cardData.data.follower,
                    level: cardData.data.card.level_info.current_level,
                    sign: cardData.data.card.sign
                };
            }

            if (data.data.pic) {
                proxiedCover.value = `https://images.weserv.nl/?url=${encodeURIComponent(data.data.pic.replace(/^https?:\/\//, ''))}`;
            }
            if (data.data.owner?.face) {
                proxiedAvatar.value = `https://images.weserv.nl/?url=${encodeURIComponent(data.data.owner.face.replace(/^https?:\/\//, ''))}`;
            }
            extractThemeColor();
        } else {
            error.value = true;
        }
    } catch (err) {
        console.error('Bilibili API Error:', err);
        error.value = true;
    } finally {
        loading.value = false;
    }
};

const extractThemeColor = () => {
    if (!proxiedCover.value) return;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.src = proxiedCover.value;
    img.onload = () => {
        try {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = 50; canvas.height = 50;
            ctx.drawImage(img, 0, 0, 50, 50);
            const data = ctx.getImageData(0, 0, 50, 50).data;
            let r = 0, g = 0, b = 0;
            const sampleSize = 100;
            for (let i = 0; i < sampleSize; i++) {
                const idx = Math.floor(Math.random() * (data.length / 4)) * 4;
                r += data[idx]; g += data[idx + 1]; b += data[idx + 2];
            }
            r = Math.floor(r / sampleSize); g = Math.floor(g / sampleSize); b = Math.floor(b / sampleSize);
            const brightness = (r + g + b) / 3;
            if (brightness < 60) {
                const boost = 60 - brightness;
                r = Math.min(r + boost, 255); g = Math.min(g + boost, 255); b = Math.min(b + boost, 255);
            }
            themeColor.value = `rgb(${r}, ${g}, ${b})`;
            accentColor.value = `rgb(${Math.min(r + 60, 255)}, ${Math.min(g + 30, 255)}, ${Math.min(b + 90, 255)})`;
            secondaryColor.value = `rgb(${Math.max(r - 40, 0)}, ${Math.min(g + 80, 255)}, ${Math.max(b - 20, 0)})`;
        } catch (e) { console.warn(e); }
    };
};

onMounted(() => fetchVideoDetails());
</script>

<template>
    <article class="bili-embed-neo" :class="{ 'is-loading': loading, 'is-error': error, 'is-hovering': isHovering }"
        ref="cardRef" @mousemove="handleMouseMove" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave" :style="{
            '--theme-primary': themeColor,
            '--theme-accent': accentColor,
            '--theme-secondary': secondaryColor,
            '--mouse-x': mouseX,
            '--mouse-y': mouseY
        }">

        <div class="mood-bg">
            <div class="bg-layer base-blur" :style="{ backgroundImage: `url(${proxiedCover})` }"></div>
            <div class="bg-layer drift-blur" :style="{ backgroundImage: `url(${proxiedCover})` }"></div>
            <div class="noise-overlay"></div>
            <div class="overlay-gradient"></div>
        </div>

        <div v-if="loading" class="state-container">
            <div class="cyber-loader">
                <div class="glitch-box"></div>
            </div>
        </div>

        <div v-else-if="error" class="state-container error-state">
            <div class="error-content">
                <span class="error-code">404::SIGNAL_LOST</span>
                <a :href="props.videourl" target="_blank" class="error-link">MANUAL_OVERRIDE</a>
            </div>
        </div>

        <div v-else class="bili-card-glass" :style="cardStyle">
            <div class="glass-shine"></div>

            <div class="media-column">
                <a :href="videoUrl" target="_blank" class="cover-wrapper">
                    <div class="glitch-layer layer-r" :style="{ backgroundImage: `url(${proxiedCover})` }"></div>
                    <div class="glitch-layer layer-b" :style="{ backgroundImage: `url(${proxiedCover})` }"></div>
                    <div class="glitch-layer layer-main" :style="{ backgroundImage: `url(${proxiedCover})` }"></div>
                    <div class="play-overlay">
                        <div class="play-button-hex">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M8 5v14l11-7z" />
                            </svg>
                        </div>
                    </div>
                    <div class="duration-badge">
                        <span class="badge-blur"></span>
                        <span class="badge-text">{{ formatDuration(videoData.duration) }}</span>
                    </div>
                </a>
            </div>

            <div class="data-column">
                <header class="data-header">
                    <div class="platform-chip"><span class="dot"></span>BILIBILI.V2</div>
                    <time class="meta-date">{{ formatDate(videoData.pubdate) }}</time>
                </header>

                <h3 class="video-title">
                    <a :href="videoUrl" target="_blank">{{ videoData.title }}</a>
                </h3>

                <div v-if="videoData.desc" class="video-description-deck">
                    <div class="deck-bracket"></div>
                    <p class="deck-content">{{ videoData.desc }}</p>
                </div>

                <div class="stats-matrix">
                    <div class="stat-cell" v-for="stat in visualStats" :key="stat.label">
                        <div class="stat-track">
                            <div class="stat-bar" :style="{ width: stat.percent + '%' }"></div>
                        </div>
                        <div class="stat-info">
                            <span class="stat-val">{{ stat.display }}</span>
                            <span class="stat-key">{{ stat.label }}</span>
                        </div>
                    </div>
                </div>

                <footer class="data-footer">
                    <div class="creator-telemetry">
                        <div class="cyclotron-avatar">
                            <div class="orbit-ring"></div>
                            <div class="orbit-ring-outer"></div>
                            <img :src="proxiedAvatar" class="author-face" />
                            <div class="scan-line"></div>
                        </div>
                        <div class="creator-info">
                            <div class="author-row">
                                <span class="author-id">{{ videoData.owner.name }}</span>
                                <div class="fans-badge" v-if="creatorStats">
                                    <span class="fans-label" :style="{ background: lvBg, color: lvText }"
                                        :title="'Level ' + (creatorStats.level ?? 0)">LV.{{ creatorStats.level }}</span>
                                    <span class="fans-count">{{ formatStat(creatorStats.follower).display }} 粉丝</span>
                                </div>
                            </div>
                            <div class="creator-bio">{{ creatorStats?.sign || 'DATA_STREAM::STABILIZED' }}</div>
                        </div>
                    </div>

                    <div class="feedback-sector">
                        <div v-if="videoData.honor_reply?.honor" class="honor-rank">
                            <span class="rank-icon"></span> {{ videoData.honor_reply.honor[0].desc }}
                        </div>
                        <div v-else class="system-status">
                            <div class="status-pip ripple"></div>
                            <span class="status-msg">LINK_ESTABLISHED</span>
                        </div>
                        <div class="micro-tags">
                            <span v-for="tag in videoData.tags?.slice(0, 2)" :key="tag.tag_id" class="micro-tag">
                                {{ tag.tag_name }}
                            </span>
                        </div>
                    </div>
                </footer>
            </div>

            <div class="particle-field">
                <div v-for="n in 5" :key="n" class="particle" :style="{ '--delay': n + 's', '--pos': (n * 20) + '%' }">
                </div>
            </div>
        </div>
    </article>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

.bili-embed-neo {
    --glass-surface: rgba(255, 255, 255, 0.08);
    --glass-border: rgba(255, 255, 255, 0.15);
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.7);
    --ease-elastic: cubic-bezier(0.34, 1.56, 0.64, 1);
    width: 100%;
    margin: 2.5rem 0;
    position: relative;
    border-radius: 16px;
    isolation: isolate;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--text-primary);
    perspective: 1000px;
}

.mood-bg {
    position: absolute;
    inset: 0;
    border-radius: 16px;
    overflow: hidden;
    z-index: -1;
    background: #0f0f0f;
}

.bg-layer {
    position: absolute;
    inset: -20%;
    background-size: cover;
    background-position: center;
    transition: opacity 0.5s ease;
}

.base-blur {
    filter: blur(50px) brightness(0.5) saturate(1.2);
    opacity: 0.8;
    transform: scale(1.2);
}

.drift-blur {
    filter: blur(30px) brightness(0.7) contrast(1.2);
    opacity: 0.4;
    mix-blend-mode: hard-light;
    animation: drift 20s infinite alternate linear;
}

.noise-overlay {
    position: absolute;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
    z-index: 1;
    opacity: 0.7;
}

.overlay-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.4) 100%);
    z-index: 2;
}

@keyframes drift {
    0% {
        transform: translate(0, 0) scale(1.1);
    }

    100% {
        transform: translate(2%, 2%) scale(1.2);
    }
}

.bili-card-glass {
    display: flex;
    gap: 1.5rem;
    padding: 1.25rem;
    background: var(--glass-surface);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    backdrop-filter: blur(20px) saturate(180%);
    transform-style: preserve-3d;
    transition: transform 0.1s linear;
    overflow: hidden;
}

.media-column {
    flex: 0 0 280px;
    position: relative;
    z-index: 2;
}

.cover-wrapper {
    display: block;
    position: relative;
    width: 100%;
    aspect-ratio: 16/10;
    border-radius: 10px;
    overflow: hidden;
}

.glitch-layer {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center;
    transition: all 0.3s ease;
}

.layer-r {
    opacity: 0;
    mix-blend-mode: color-dodge;
}

.layer-b {
    opacity: 0;
    mix-blend-mode: exclusion;
}

.cover-wrapper:hover .layer-r {
    opacity: 0.6;
    transform: translate(2px, 0);
}

.cover-wrapper:hover .layer-b {
    opacity: 0.6;
    transform: translate(-2px, 0);
}

.play-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s;
    background: rgba(0, 0, 0, 0.2);
}

.cover-wrapper:hover .play-overlay {
    opacity: 1;
}

.play-button-hex {
    width: 48px;
    height: 48px;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(4px);
    clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
}

.duration-badge {
    position: absolute;
    bottom: 8px;
    right: 8px;
    padding: 2px 6px;
    border-radius: 4px;
    overflow: hidden;
    font-size: 10px;
    font-weight: bold;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
}

.data-column {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.data-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
}

.platform-chip {
    color: var(--theme-primary);
    display: flex;
    align-items: center;
    gap: 4px;
}

.dot {
    width: 4px;
    height: 4px;
    background: currentColor;
    border-radius: 50%;
    box-shadow: 0 0 8px currentColor;
}

.video-title {
    margin-bottom: 12px;
    font-size: 18px;
    font-weight: 700;
    line-height: 1.3;
}

.video-title a {
    color: white;
    text-decoration: none;
    background: linear-gradient(90deg, var(--theme-primary), var(--theme-accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.video-description-deck {
    position: relative;
    padding: 8px 12px;
    background: rgba(0, 0, 0, 0.2);
    border-left: 2px solid var(--theme-primary);
    border-radius: 4px;
    margin-bottom: 12px;
}

.deck-content {
    font-size: 13px;
    line-height: 1.5;
    color: rgba(255, 255, 255, 0.8);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin: 0;
}

.stats-matrix {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px 20px;
    margin-bottom: 16px;
}

.stat-track {
    height: 2px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 1px;
    overflow: hidden;
    margin-bottom: 4px;
}

.stat-bar {
    height: 100%;
    background: var(--theme-primary);
    box-shadow: 0 0 8px var(--theme-primary);
}

.stat-info {
    display: flex;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
}

.stat-val {
    color: white;
    font-weight: bold;
}

.stat-key {
    color: var(--theme-secondary);
}

.data-footer {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 12px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.creator-telemetry {
    display: flex;
    align-items: center;
    gap: 12px;
}

.cyclotron-avatar {
    position: relative;
    width: 48px;
    height: 48px;
    flex-shrink: 0;
}

.author-face {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 2px solid #000;
}

.orbit-ring {
    position: absolute;
    inset: -3px;
    border: 1px dashed var(--theme-primary);
    border-radius: 50%;
    animation: rotate 10s linear infinite;
}

.scan-line {
    position: absolute;
    width: 100%;
    height: 1px;
    background: rgba(0, 255, 65, 0.5);
    top: 50%;
    animation: scan 2s infinite ease-in-out;
}

.creator-info {
    flex: 1;
    min-width: 0;
}

.author-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 2px;
}

.author-id {
    font-size: 14px;
    font-weight: 700;
    color: white;
}

.fans-badge {
    display: flex;
    font-size: 9px;
    font-family: 'JetBrains Mono', monospace;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
}

.fans-label {
    background: var(--theme-primary);
    color: black;
    padding: 0 4px;
    font-weight: 800;
}

.fans-count {
    padding: 0 4px;
}

.creator-bio {
    font-size: 10px;
    color: var(--text-secondary);
    font-family: 'JetBrains Mono', monospace;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 250px;
}

.feedback-sector {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(0, 0, 0, 0.2);
    padding: 4px 8px;
    border-radius: 4px;
}

.honor-rank {
    font-size: 10px;
    color: #ffd700;
}

.system-status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: #00FF41;
}

.status-pip {
    width: 5px;
    height: 5px;
    background: #00FF41;
    border-radius: 50%;
    box-shadow: 0 0 5px #00FF41;
}

.ripple {
    animation: ripple 1.5s infinite;
}

.micro-tags {
    display: flex;
    gap: 6px;
}

.micro-tag {
    font-size: 9px;
    color: var(--text-secondary);
    background: rgba(255, 255, 255, 0.05);
    padding: 1px 4px;
    border-radius: 2px;
}

@keyframes rotate {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

@keyframes scan {

    0%,
    100% {
        transform: translateY(-20px);
        opacity: 0;
    }

    50% {
        transform: translateY(20px);
        opacity: 1;
    }
}

@keyframes ripple {
    0% {
        box-shadow: 0 0 0 0 rgba(0, 255, 65, 0.4);
    }

    100% {
        box-shadow: 0 0 0 8px rgba(0, 255, 65, 0);
    }
}

@media (max-width: 768px) {
    .bili-card-glass {
        flex-direction: column;
    }

    .media-column {
        flex: none;
        width: 100%;
    }
}

.state-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 200px;
}

.cyber-loader .glitch-box {
    width: 40px;
    height: 40px;
    border: 2px solid var(--theme-primary);
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0% {
        transform: scale(0.8);
        opacity: 0.5;
    }

    100% {
        transform: scale(1.2);
        opacity: 0;
    }
}
</style>
