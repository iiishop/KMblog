<script setup>
import { ref, computed, watch, onUnmounted } from 'vue';
import { fetchBlockData } from '../../utils/blockProxy';
import { parseHtmlData, extractNoteId } from '../../utils/xiaohongshuData';

const props = defineProps({
    noteurl: String,
});

const noteData = ref(null);
const loading = ref(true);
const error = ref(false);
const errorMessage = ref('');
let controller;
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

const convertToWeserv = (url) => {
    if (!url || url.length < 5) return '';
    // Handle protocol-relative URLs and strip http/https
    let clean = url.replace(/^(https?:)?\/\//, '');
    // Ensure we don't have double slashes at the start
    clean = clean.replace(/^\/+/, '');
    return `https://images.weserv.nl/?url=${encodeURIComponent(clean)}&w=800&output=webp`;
};

const fetchNote = async () => {
    controller?.abort();
    const request = controller = new AbortController();
    loading.value = true;
    error.value = false;
    errorMessage.value = '';
    noteData.value = null;
    proxiedCover.value = '';
    proxiedAvatar.value = '';
    try {
        const url = new URL(props.noteurl?.trim());
        if (!/^https?:$/.test(url.protocol) || !/(^|\.)(xiaohongshu\.com|xhslink\.com)$/.test(url.hostname)) {
            throw new Error('请输入完整的小红书分享链接（保留链接中的验证参数）');
        }
        const data = await fetchBlockData(url.href, {
            signal: request.signal,
            parse: html => {
                const note = parseHtmlData(html, url.href);
                if (!note) throw new Error('未找到笔记内容，可能是验证页、失效链接或代理错误页面');
                return note;
            },
        });
        if (request.signal.aborted) return;
        noteData.value = data;
        proxiedCover.value = convertToWeserv(data.cover);
        proxiedAvatar.value = convertToWeserv(data.user.avatar);
        extractThemeColor();
    } catch (err) {
        if (request.signal.aborted) return;
        error.value = true;
        errorMessage.value = err instanceof TypeError ? '请输入完整的小红书分享链接' : err.message;
    } finally {
        if (!request.signal.aborted) loading.value = false;
    }
};

const extractThemeColor = () => {
    if (!proxiedCover.value) return;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    const request = controller;
    img.onload = () => {
        if (request?.signal.aborted) return;
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
    img.src = proxiedCover.value;
};

// ---- Mention & Tag parsing + rendering helpers ----
const escapeHtml = (str) => {
    if (str == null) return '';
    return String(str).replace(/[&<>\"'`]/g, (s) => {
        return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": "&#39;", "`": "&#96;" })[s];
    });
};

const extractMentionsAndTags = (text) => {
    const mentions = new Set();
    const tags = new Set();
    if (!text) return { mentions: [], tags: [] };
    // Mentions: @username (stop at whitespace or punctuation)
    text.replace(/@([A-Za-z0-9_\.\-\u4e00-\u9fff]{1,64})/g, (m, name) => {
        mentions.add(name);
        return m;
    });
    // Tags: #标签  (allow unicode letters and CJK)
    text.replace(/#([\p{L}0-9_\-\u4e00-\u9fff]{1,64})/gu, (m, tag) => {
        tags.add(tag);
        return m;
    });
    return { mentions: Array.from(mentions), tags: Array.from(tags) };
};

const parseDescToHtml = (text) => {
    if (!text) return '';
    let s = escapeHtml(text);
    // preserve paragraphs / line breaks
    s = s.replace(/\r\n|\r|\n/g, '<br>');

    // Replace mentions with non-link spans (keep in-text, no href)
    // Use the same conservative charset used in extraction so we don't consume <br> or other markup
    s = s.replace(/@([A-Za-z0-9_\.\-\u4e00-\u9fff]{1,64})/g, (m, name) => {
        const esc = escapeHtml(name);
        return `<span class="mention-link">@${esc}</span>`;
    });

    // Remove display-only marker "[话题]#" sequences (strict match) so they don't show in description
    s = s.replace(/\[话题\]#/g, '');

    // Remove tags from text flow (Don't render #tag in description)
    s = s.replace(/#([\p{L}0-9_\-\u4e00-\u9fff]{1,64})/gu, '');

    // Cleanup excessive line breaks if tags were removed
    s = s.replace(/(<br>\s*){3,}/g, '<br><br>');

    return s;
};

const parsedDescHtml = computed(() => parseDescToHtml(noteData.value?.desc || ''));
const extractedMeta = computed(() => extractMentionsAndTags(noteData.value?.desc || ''));


const visualStats = computed(() => {
    if (!noteData.value) return [];
    return [
        { label: 'LIKES', val: formatStat(noteData.value.stats.likes), icon: '♥' },
        { label: 'FAVS', val: formatStat(noteData.value.stats.collects), icon: '★' },
    ]
});

watch(() => props.noteurl, fetchNote, { immediate: true });
onUnmounted(() => controller?.abort());

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

        <div v-if="loading" class="state-layer skeleton">
            <div class="skeleton-card" role="status" aria-label="loading">
                <div class="skeleton-media" aria-hidden="true"></div>
                <div class="skeleton-content">
                    <div class="skeleton-header">
                        <div class="skeleton-brand"></div>
                        <div class="skeleton-id"></div>
                    </div>
                    <div class="skeleton-title"></div>
                    <div class="skeleton-lines">
                        <div class="line short"></div>
                        <div class="line"></div>
                        <div class="line long"></div>
                    </div>
                    <div class="skeleton-chips">
                        <div class="chip"></div>
                        <div class="chip small"></div>
                        <div class="chip"></div>
                    </div>
                    <div class="skeleton-footer">
                        <div class="avatar"></div>
                        <div class="meta-lines">
                            <div class="line tiny"></div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="red-loader small" aria-hidden="true">
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
        </div>

        <div v-else-if="error" class="state-layer error">
            <div class="error-msg">{{ errorMessage }}</div>
            <a :href="props.noteurl" target="_blank" class="manual-link" rel="noopener noreferrer">打开原文</a>
            <button type="button" class="manual-link" @click="fetchNote">重试</button>
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

                <p class="note-abstract" v-html="parsedDescHtml" :aria-label="noteData.desc"></p>

                <div class="chips-row" v-if="extractedMeta.tags.length">
                    <div class="chips-left">
                        <a v-for="t in extractedMeta.tags" :key="'t-' + t" class="tag-chip"
                            :href="`https://www.xiaohongshu.com/search/result?keyword=${encodeURIComponent('#' + t)}`"
                            target="_blank" rel="noopener noreferrer" aria-label="tag">#{{ t }}</a>
                    </div>
                </div>

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
.error-content, .error-msg { max-width: 100%; overflow-wrap: anywhere; white-space: normal; }
.error-content { display: flex; flex-direction: column; gap: 12px; padding: 20px; }
button.error-link, button.manual-link { cursor: pointer; font: inherit; }

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,700&family=DM+Sans:wght@400;500;700&family=JetBrains+Mono&display=swap');

.xhs-embed-container {
    --card-bg: #0a0a0a;
    --card-border: rgba(255, 255, 255, 0.08);
    --text-primary: #fff;
    --text-dim: #999;
    --theme-red-deep: #D31027;

    width: 100%;
    margin: 3.5rem 0;
    position: relative;
    font-family: 'DM Sans', sans-serif;
    border-radius: 4px;
    /* Brutalist sharp corners */
    perspective: 2000px;
    isolation: isolate;
    color: var(--text-primary);
}

.atmosphere-bg {
    position: absolute;
    inset: 0;
    z-index: -1;
    border-radius: 4px;
    overflow: hidden;
    background: #000;
}

.bg-blur {
    position: absolute;
    inset: -10%;
    background-size: cover;
    background-position: center;
    filter: grayscale(1) brightness(0.2);
    /* High fashion muted bg */
    opacity: 0.4;
    transition: opacity 0.8s ease;
}

.noise-layer {
    position: absolute;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.12'/%3E%3C/svg%3E");
    opacity: 0.8;
}

.red-wash {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 0% 0%, rgba(211, 16, 39, 0.15), transparent 70%);
}

.xhs-card {
    position: relative;
    display: flex;
    gap: 2.5rem;
    padding: 2.5rem;
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 4px;
    box-shadow: 0 40px 100px rgba(0, 0, 0, 0.8);
    overflow: hidden;
}

/* Media Area: Fashion Layout */
.media-area {
    flex: 0 0 280px;
    position: relative;
    aspect-ratio: 3/4.2;
    overflow: hidden;
    box-shadow: 20px 20px 0px var(--theme-red-deep);
    /* Offset background shape */
}

.media-container {
    width: 100%;
    height: 100%;
}

.media-layer {
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
    filter: saturate(1.1) contrast(1.1);
}

.type-badge {
    position: absolute;
    bottom: 0px;
    left: 0px;
    background: var(--theme-red-deep);
    padding: 6px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: #fff;
    letter-spacing: 2px;
}

/* Content Area: Editorial Typography */
.content-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.xhs-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.5rem;
}

.brand-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 3px;
    color: var(--theme-red-deep);
    border: 1px solid var(--theme-red-deep);
    padding: 2px 8px;
}

.note-id {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #444;
}

.note-title {
    margin: 0 0 1.5rem 0;
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.5rem;
    font-style: italic;
    line-height: 1.1;
    font-weight: 700;
}

.note-title a {
    color: #fff;
    text-decoration: none;
    transition: color 0.3s ease;
}

.note-abstract {
    font-size: 0.95rem;
    line-height: 1.8;
    color: var(--text-dim);
    margin-bottom: 2rem;
    font-weight: 400;
    max-height: 100px;
    /* limit height */
    overflow: hidden;
    position: relative;
}

.note-abstract::after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 20px;
    pointer-events: none;
    /* gradient fade + subtle blur to mask overflowed text */
    background: linear-gradient(to bottom, rgba(10, 10, 10, 0), var(--card-bg));
    backdrop-filter: blur(1px);
}

/* Mentions In-Text: No Hover */
.note-abstract :deep(.mention-link) {
    color: var(--theme-red-deep);
    text-decoration: none;
    font-weight: 700;
    cursor: default;
    /* No hover logic */
}

/* Chips: No Hover */
.chips-row {
    margin-top: auto;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.chips-left {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.tag-chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    padding: 4px 12px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #fff;
    text-decoration: none;
    text-transform: uppercase;
    letter-spacing: 1px;
    cursor: default;
    /* No hover logic */
}

.meta-footer {
    margin-top: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.user-block {
    display: flex;
    align-items: center;
    gap: 12px;
}

.user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 0;
    /* Square minimalist avatar */
    border: 1px solid #333;
}

.user-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 1px;
}

.stats-row {
    display: flex;
    gap: 20px;
}

.stat-pill {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #666;
}

.stat-pill .icon {
    font-size: 12px;
    color: var(--theme-red-deep);
}

/* Skeleton placeholders */
.skeleton-card {
    display: flex;
    gap: 1.5rem;
    width: 100%;
    align-items: stretch;
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.01), rgba(255, 255, 255, 0.005));
    border-radius: 4px;
    padding: 18px;
    box-sizing: border-box;
}

.skeleton-media {
    width: 280px;
    height: 200px;
    border-radius: 4px;
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.01));
    position: relative;
    overflow: hidden;
    flex-shrink: 0;
}

.skeleton-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.skeleton-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
}

.skeleton-brand,
.skeleton-id,
.skeleton-title,
.line,
.chip,
.avatar {
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.01));
    border-radius: 4px;
    position: relative;
    overflow: hidden;
}

.skeleton-brand {
    width: 68px;
    height: 18px;
}

.skeleton-id {
    width: 48px;
    height: 14px;
    opacity: 0.6;
}

.skeleton-title {
    width: 60%;
    height: 34px;
    border-radius: 6px;
}

.skeleton-lines {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.line {
    height: 12px;
    width: 90%;
    border-radius: 6px;
}

.line.short {
    width: 40%;
}

.line.long {
    width: 100%;
}

.line.tiny {
    width: 36px;
    height: 10px;
}

.skeleton-chips {
    display: flex;
    gap: 10px;
    align-items: center;
}

.chip {
    width: 64px;
    height: 26px;
    border-radius: 999px;
}

.chip.small {
    width: 44px;
}

.skeleton-footer {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: auto;
}

.avatar {
    width: 32px;
    height: 32px;
    border-radius: 4px;
}

/* shimmer animation */
.skeleton-card::before,
.skeleton-media::before,
.skeleton-brand::before,
.skeleton-title::before,
.line::before,
.chip::before,
.avatar::before,
.skeleton-id::before {
    content: '';
    position: absolute;
    inset: 0;
    transform: translateX(-100%);
    background: linear-gradient(90deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0));
    animation: shimmer 1.6s infinite;
    pointer-events: none;
}

.skeleton-media::before,
.skeleton-brand::before,
.skeleton-title::before,
.line::before,
.chip::before,
.avatar::before,
.skeleton-id::before {
    position: absolute;
}

@keyframes shimmer {
    0% {
        transform: translateX(-100%);
    }

    100% {
        transform: translateX(200%);
    }
}

.red-loader.small .dot {
    width: 6px;
    height: 6px;
}

/* 响应式设计 */
@media (max-width: 968px) {
    .xhs-card {
        flex-direction: column;
        padding: 1.5rem;
        gap: 1.5rem;
    }

    .media-area {
        flex: none;
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
        box-shadow: 15px 15px 0 var(--theme-red-deep);
    }

    .content-area {
        width: 100%;
    }

    .note-title {
        font-size: 2rem;
    }

    .note-abstract {
        font-size: 0.9rem;
        max-height: 120px;
    }

    .chips-left {
        gap: 10px;
    }

    .meta-footer {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }

    .stats-row {
        width: 100%;
        justify-content: flex-start;
    }
}

@media (max-width: 640px) {
    .xhs-embed-container {
        margin: 2.5rem 0;
    }

    .xhs-card {
        padding: 1rem;
        gap: 1rem;
    }

    .media-area {
        max-width: 100%;
        box-shadow: 10px 10px 0 var(--theme-red-deep);
    }

    .xhs-header {
        gap: 8px;
        margin-bottom: 1rem;
    }

    .brand-tag {
        font-size: 9px;
        letter-spacing: 2px;
        padding: 2px 6px;
    }

    .note-id {
        font-size: 9px;
    }

    .note-title {
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    .note-abstract {
        font-size: 0.85rem;
        max-height: 100px;
        margin-bottom: 1.5rem;
    }

    .chips-row {
        padding-top: 1rem;
    }

    .chips-left {
        gap: 8px;
    }

    .tag-chip {
        font-size: 9px;
        padding: 3px 10px;
    }

    .meta-footer {
        margin-top: 1rem;
    }

    .user-avatar {
        width: 28px;
        height: 28px;
    }

    .user-name {
        font-size: 0.8rem;
    }

    .stats-row {
        gap: 15px;
    }

    .stat-pill {
        font-size: 10px;
    }
}

@media (max-width: 480px) {
    .xhs-card {
        padding: 0.75rem;
    }

    .media-area {
        box-shadow: 8px 8px 0 var(--theme-red-deep);
    }

    .note-title {
        font-size: 1.3rem;
    }

    .note-abstract {
        font-size: 0.8rem;
        max-height: 80px;
    }

    .tag-chip {
        font-size: 8px;
        padding: 2px 8px;
    }

    .user-block {
        gap: 8px;
    }

    .user-avatar {
        width: 24px;
        height: 24px;
    }

    .user-name {
        font-size: 0.75rem;
    }

    .stat-pill {
        font-size: 9px;
        gap: 4px;
    }

    /* Skeleton 响应式 */
    .skeleton-card {
        padding: 12px;
        gap: 1rem;
    }

    .skeleton-media {
        width: 100%;
        height: 150px;
    }

    .skeleton-title {
        height: 28px;
    }
}

@media (max-width: 900px) {
    .xhs-card {
        flex-direction: column;
        padding: 1.5rem;
    }

    .media-area {
        flex: none;
        width: 100%;
        box-shadow: 10px 10px 0 var(--theme-red-deep);
    }

    .note-title {
        font-size: 1.75rem;
    }
}
</style>
