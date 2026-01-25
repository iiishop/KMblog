<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const props = defineProps({
    noteurl: String,
});

const noteData = ref(null);
const loading = ref(true);
const error = ref(false);
const proxiedCover = ref('');
const proxiedAvatar = ref('');
// Xiaohongshu Red Base
const themeColor = ref('#FF2442');
const accentColor = ref('#FF899E');
const secondaryColor = ref('#FFD1D9');

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
    const rotateX = isHovering.value ? mouseY.value * -3 : 0;
    const rotateY = isHovering.value ? mouseX.value * 3 : 0;
    return {
        transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
    };
});

// Format large numbers
const formatStat = (num) => {
    if (!num && num !== 0) return '0';
    if (num >= 10000) return (num / 10000).toFixed(1) + 'w';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num.toString();
};

const fetchProxy = async (targetUrl) => {
    const proxyGenerators = [
        (url) => `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`,
        (url) => `https://corsproxy.io/?${encodeURIComponent(url)}`,
        (url) => `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(url)}`
    ];
    for (const getProxyUrl of proxyGenerators) {
        try {
            const proxyUrl = getProxyUrl(targetUrl);
            const response = await axios.get(proxyUrl);
            if (response.data) return response.data;
        } catch (e) {
            console.warn(`Proxy request failed: ${e.message}`);
        }
    }
    return null;
};

const extractNoteId = (url) => {
    if (!url) return null;
    try {
        const u = new URL(url);
        // Supports /explore/ID or /discovery/item/ID
        const path = u.pathname.split('/').filter(Boolean);
        const last = path[path.length - 1];
        if (last && last.length >= 24) return last;
    } catch (e) { }
    // Fallback: regex for 24 hex chars or typical XHS ID format
    const match = url.match(/[a-f0-9]{24}/i);
    return match ? match[0] : null;
};

const parseHtmlData = (html) => {
    try {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // 1. Try to find the script tag containing __INITIAL_STATE__
        const scripts = doc.querySelectorAll('script');
        let initialData = null;
        for (const script of scripts) {
            const text = script.textContent;
            if (text.includes('__INITIAL_STATE__')) {
                // More flexible regex to catch various assignments
                const match = text.match(/window\.__INITIAL_STATE__\s*=\s*(\{.*?\})\s*(?:;|$)/s) ||
                    text.match(/__INITIAL_STATE__\s*=\s*(\{.*?\})\s*(?:;|$)/s);
                if (match && match[1]) {
                    try {
                        const cleanJson = match[1].replace(/undefined/g, 'null');
                        initialData = JSON.parse(cleanJson);
                        break;
                    } catch (e) { }
                }
            }
        }

        if (initialData && initialData.note) {
            // Check noteDetailMap or direct note field
            const noteMap = initialData.note.noteDetailMap;
            // Get note from map OR fallback to direct note property
            let noteObj = null;
            if (noteMap) {
                // Try to match current note via ID if possible, or just take first
                noteObj = Object.values(noteMap)[0]?.note;
            }
            if (!noteObj) noteObj = initialData.note.note;

            if (noteObj) {
                // Deep extraction of user info
                const user = noteObj.user || {};
                const nickname = user.nickname || user.nickName || user.name || 'RED.User';
                const avatar = user.avatar || user.avatarContent?.urlDefault || user.image || '';

                return {
                    title: noteObj.title || noteObj.desc?.slice(0, 24) || 'RED.Note',
                    desc: noteObj.desc || '',
                    type: noteObj.type || 'normal',
                    user: { nickname, avatar },
                    stats: {
                        likes: noteObj.interactInfo?.likedCount || noteObj.interactInfo?.likeCount || 0,
                        collects: noteObj.interactInfo?.collectedCount || noteObj.interactInfo?.collectCount || 0,
                        comments: noteObj.interactInfo?.commentCount || 0
                    },
                    cover: noteObj.imageList?.[0]?.urlDefault || noteObj.cover?.urlDefault || '',
                };
            }
        }

        // 2. Fallback: Meta Tags (OG)
        const ogTitle = doc.querySelector('meta[property="og:title"]')?.content ||
            doc.querySelector('meta[name="og:title"]')?.content ||
            doc.querySelector('title')?.innerText;

        const ogImage = doc.querySelector('meta[property="og:image"]')?.content ||
            doc.querySelector('meta[name="og:image"]')?.content;

        const ogDesc = doc.querySelector('meta[property="og:description"]')?.content ||
            doc.querySelector('meta[name="description"]')?.content;

        // Try to find user info from alternative sources in HTML
        const userNickname = doc.querySelector('.nickname')?.innerText ||
            doc.querySelector('.user-name')?.innerText ||
            doc.querySelector('meta[name="author"]')?.content || 'RED.User';

        if (ogTitle && ogImage) {
            return {
                title: ogTitle,
                desc: ogDesc,
                type: 'normal',
                user: { nickname: userNickname, avatar: '' },
                stats: { likes: 0, collects: 0 },
                cover: ogImage
            };
        }
    } catch (e) {
        console.error('Parse Error:', e);
    }
    return null;
};


const convertToWeserv = (url) => {
    if (!url || url.length < 5) return '';
    // Handle protocol-relative URLs and strip http/https
    let clean = url.replace(/^(https?:)?\/\//, '');
    // Ensure we don't have double slashes at the start
    clean = clean.replace(/^\/+/, '');
    return `https://images.weserv.nl/?url=${encodeURIComponent(clean)}&w=800&output=webp`;
};

const fetchNote = async () => {
    // We assume props.noteurl contains the necessary tokens if required, 
    // but usually web scraping via proxy works for basic og-tags if URL is valid.
    if (!props.noteurl) return;

    // Note: If usage requires xsec_token for access even on public web, the user needs to provide full URL.
    try {
        const html = await fetchProxy(props.noteurl);
        if (html) {
            const data = parseHtmlData(html);
            if (data) {
                noteData.value = data;
                proxiedCover.value = convertToWeserv(data.cover);
                proxiedAvatar.value = convertToWeserv(data.user.avatar);
                extractThemeColor();
            } else {
                error.value = true;
            }
        } else {
            error.value = true;
        }
    } catch (err) {
        console.error(err);
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
            canvas.width = 1; canvas.height = 1;
            ctx.drawImage(img, 0, 0, 1, 1);
            const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data;
            themeColor.value = `rgb(${r}, ${g}, ${b})`;
            // Calculate complementary/accent
            accentColor.value = `rgb(${255 - r}, ${255 - b}, ${255 - g})`;
        } catch (e) { }
    };
};

const visualStats = computed(() => {
    if (!noteData.value) return [];
    return [
        { label: 'LIKES', val: formatStat(noteData.value.stats.likes), icon: '♥' },
        { label: 'FAVS', val: formatStat(noteData.value.stats.collects), icon: '★' },
    ]
});

onMounted(() => fetchNote());

</script>

<template>
    <article class="xhs-embed-container"
        :class="{ 'is-loading': loading, 'is-error': error, 'is-hovering': isHovering }" ref="cardRef"
        @mousemove="handleMouseMove" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave" :style="{
            '--theme-red': themeColor,
            '--theme-accent': accentColor
        }">

        <!-- Mood / Atmosphere Background -->
        <div class="atmosphere-bg">
            <div class="bg-blur"
                :style="{ backgroundImage: `url(${proxiedCover || 'https://images.weserv.nl/?url=ci.xiaohongshu.com/eb77b848-0c2d-4537-9755-667746404980'})` }">
            </div>
            <div class="noise-layer"></div>
            <div class="red-wash"></div>
        </div>

        <div v-if="loading" class="state-layer">
            <div class="red-loader">
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
        </div>

        <div v-else-if="error" class="state-layer error">
            <div class="error-msg">CONNECTION_REFUSED</div>
            <a :href="props.noteurl" target="_blank" class="manual-link">OPEN_MANUAL</a>
        </div>

        <div v-else class="xhs-card" :style="cardStyle">
            <div class="card-glass-reflection"></div>

            <a :href="props.noteurl" target="_blank" class="media-area">
                <!-- If video type, we rely on static cover (per request). 
                     If normal type, we rely on cover which might be animated webp if XHS served it, 
                     but weserv converts gif to webp usually. 
                     If original was gif, weserv output=webp keeps animation usually. -->
                <div class="media-container">
                    <div class="media-layer" :style="{ backgroundImage: `url(${proxiedCover})` }"></div>
                    <div class="media-vignette"></div>
                    <div class="type-badge" v-if="noteData.type === 'video'">
                        <svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor">
                            <path d="M8 5v14l11-7z" />
                        </svg>
                        VIDEO
                    </div>
                </div>
            </a>

            <div class="content-area">
                <div class="xhs-header">
                    <span class="brand-tag">RED.NOTE</span>
                    <span class="note-id">#{{ extractNoteId(props.noteurl)?.slice(-6) || 'UNK' }}</span>
                </div>

                <h3 class="note-title">
                    <a :href="props.noteurl" target="_blank">{{ noteData.title }}</a>
                </h3>

                <p class="note-abstract">{{ noteData.desc }}</p>

                <div class="meta-footer">
                    <div class="user-block">
                        <img :src="proxiedAvatar || 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 1 1\'%3E%3Crect width=\'1\' height=\'1\' fill=\'%23333\'/%3E%3C/svg%3E'"
                            class="user-avatar" crossorigin="anonymous" />
                        <span class="user-name">{{ noteData.user.nickname }}</span>
                    </div>

                    <div class="stats-row">
                        <div class="stat-pill" v-for="s in visualStats" :key="s.label">
                            <span class="icon">{{ s.icon }}</span>
                            <span class="val">{{ s.val }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </article>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@700&family=Inter:wght@400;600&display=swap');

.xhs-embed-container {
    --card-bg: rgba(255, 255, 255, 0.05);
    --card-border: rgba(255, 255, 255, 0.1);
    --text-primary: #fff;
    --text-dim: rgba(255, 255, 255, 0.7);

    width: 100%;
    margin: 2.5rem 0;
    position: relative;
    font-family: 'Inter', -apple-system, sans-serif;
    border-radius: 20px;
    perspective: 1000px;
    isolation: isolate;
    color: var(--text-primary);
}

.atmosphere-bg {
    position: absolute;
    inset: 0;
    z-index: -1;
    border-radius: 20px;
    overflow: hidden;
    background: #1a0505;
}

.bg-blur {
    position: absolute;
    inset: -20%;
    background-size: cover;
    background-position: center;
    filter: blur(40px) brightness(0.4) saturate(1.5);
    opacity: 0.6;
}

.noise-layer {
    position: absolute;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.08'/%3E%3C/svg%3E");
    opacity: 0.6;
}

.red-wash {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255, 36, 66, 0.1), transparent 80%);
}

.xhs-card {
    position: relative;
    display: flex;
    gap: 1.5rem;
    padding: 1.25rem;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    backdrop-filter: blur(24px);
    border-radius: 20px;
    transform-style: preserve-3d;
    transition: transform 0.1s linear;
    overflow: hidden;
}

.card-glass-reflection {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 100%;
    background: linear-gradient(110deg, transparent 40%, rgba(255, 255, 255, 0.05) 45%, transparent 50%);
    pointer-events: none;
    z-index: 10;
}

/* Media Setup */
.media-area {
    flex: 0 0 220px;
    position: relative;
    aspect-ratio: 3/4;
    border-radius: 12px;
    overflow: hidden;
    transform: translateZ(20px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.media-container {
    width: 100%;
    height: 100%;
    position: relative;
}

.media-layer {
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
    transition: transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

.media-area:hover .media-layer {
    transform: scale(1.05);
}

.media-vignette {
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, transparent 60%, rgba(0, 0, 0, 0.6));
}

.type-badge {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(0, 0, 0, 0.6);
    padding: 4px 8px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 700;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 4px;
    backdrop-filter: blur(4px);
}

/* Content Setup */
.content-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    position: relative;
    z-index: 2;
    transform: translateZ(0);
}

.xhs-header {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 0.75rem;
    color: var(--theme-red);
}

.brand-tag {
    background: rgba(255, 36, 66, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
}

.note-id {
    color: var(--text-dim);
    font-family: monospace;
}

.note-title {
    margin: 0 0 1rem 0;
    font-family: 'Noto Serif SC', serif;
    font-size: 1.25rem;
    line-height: 1.4;
    font-weight: 700;
}

.note-title a {
    color: white;
    text-decoration: none;
    background: linear-gradient(to right, #fff, #ffccc7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    transition: all 0.3s ease;
}

.note-abstract {
    font-size: 0.85rem;
    line-height: 1.6;
    color: var(--text-dim);
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: auto;
}

.meta-footer {
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px dashed var(--card-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.user-block {
    display: flex;
    align-items: center;
    gap: 8px;
}

.user-avatar {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 1px solid var(--theme-red);
}

.user-name {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-primary);
}

.stats-row {
    display: flex;
    gap: 8px;
}

.stat-pill {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    padding: 4px 8px;
    border-radius: 12px;
    color: var(--text-dim);
}

.stat-pill .icon {
    font-size: 10px;
    color: var(--theme-red);
}

/* Response States */
.state-layer {
    height: 250px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    gap: 1rem;
}

.red-loader .dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: var(--theme-red);
    border-radius: 50%;
    margin: 0 2px;
    animation: bounce 0.6s infinite alternate;
}

.red-loader .dot:nth-child(2) {
    animation-delay: 0.2s;
}

.red-loader .dot:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes bounce {
    to {
        transform: translateY(-8px);
        opacity: 0.5;
    }
}

.manual-link {
    color: var(--theme-red);
    font-size: 0.8rem;
    text-decoration: none;
    border-bottom: 1px dotted currentColor;
}

@media (max-width: 600px) {
    .xhs-card {
        flex-direction: column;
    }

    .media-area {
        flex: none;
        width: 100%;
        aspect-ratio: 16/9;
    }
}
</style>
