<script setup>
import { ref, onMounted, computed, onUnmounted, watch } from 'vue';
import axios from 'axios';

const props = defineProps({
    repourl: String,
});

const repoData = ref(null);
const commitStats = ref([]);
const contributors = ref([]);
const contributorsHasMore = ref(false);
const contributorsExtraCount = ref(0);
const loading = ref(true);
const error = ref(false);
const isFromCache = ref(false);
const cacheTime = ref(null);

const extractRepoInfo = (url) => {
    try {
        const path = new URL(url).pathname.split('/').filter(Boolean);
        if (path.length >= 2) return { owner: path[0], repo: path[1] };
    } catch (e) { return null; }
    return null;
};

// 立即尝试从 URL 预填充基本信息
const info = extractRepoInfo(props.repourl);
if (info) {
    repoData.value = {
        name: info.repo,
        owner: { login: info.owner },
        description: 'Syncing repository metadata...',
        stargazers_count: 0,
        forks_count: 0,
        html_url: props.repourl,
        created_at: new Date().toISOString()
    };
}

const getCacheKey = (owner, repo) => `gh_cache_${owner}_${repo}`;

const saveToCache = (owner, repo, data) => {
    localStorage.setItem(getCacheKey(owner, repo), JSON.stringify({
        timestamp: new Date().getTime(),
        data
    }));
};

const loadFromCache = (owner, repo) => {
    const cached = localStorage.getItem(getCacheKey(owner, repo));
    if (!cached) return null;
    try {
        return JSON.parse(cached);
    } catch (e) { return null; }
};

const formatCount = (num) => {
    if (!num && num !== 0) return '0';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
    return num;
};

// 模拟 Star 趋势数据 (结合仓库创建时间模拟真实的 Star History 增长曲线)
const generateStarPath = computed(() => {
    if (!repoData.value) return '';
    const points = [];
    const width = 120;
    const height = 30;
    const seed = repoData.value.id || 0;

    const createdDate = new Date(repoData.value.created_at);
    const now = new Date();
    const ageInDays = Math.max((now - createdDate) / (1000 * 60 * 60 * 24), 30);

    const pseudoRandom = (i) => Math.abs(Math.sin(seed + i) * 1000) % 1;

    for (let i = 0; i <= 20; i++) {
        const x = (i / 20) * width;
        const progress = i / 20;
        const burstOffset = 0.3 + (pseudoRandom(1) * 0.4);
        const steepness = 8 + (pseudoRandom(2) * 10);
        let growth = 1 / (1 + Math.exp(-steepness * (progress - burstOffset)));
        growth = (growth * 0.85) + (progress * 0.15);
        const noise = (pseudoRandom(i) - 0.5) * 2;
        const y = height - (growth * (height - 10) + 5) + noise;
        points.push(`${x},${y}`);
    }
    return `M 0,${height} L ${points.join(' L ')} L ${width},${height} Z`;
});

const heartbeatPath = computed(() => {
    if (!commitStats.value.length) return 'M 0,15 L 100,15';
    const max = Math.max(...commitStats.value, 1);
    const points = commitStats.value.map((count, i) => {
        const x = (i / (commitStats.value.length - 1)) * 100;
        const y = 18 - (count / max * 16);
        return `${x.toFixed(2)},${y.toFixed(2)}`;
    });
    return `M ${points.join(' L ')}`;
});

const fetchRepoDetails = async () => {
    if (!info) { error.value = true; loading.value = false; return; }

    const { owner, repo } = info;
    const baseApi = `https://api.github.com/repos/${owner}/${repo}`;

    // 尝试加载缓存
    const cached = loadFromCache(owner, repo);
    if (cached) {
        repoData.value = cached.data.repoData;
        commitStats.value = cached.data.commitStats;
        contributors.value = cached.data.contributors;
        contributorsHasMore.value = cached.data.contributorsHasMore;
        contributorsExtraCount.value = cached.data.contributorsExtraCount;
        isFromCache.value = true;
        cacheTime.value = new Date(cached.timestamp).toLocaleString();
        // 如果有缓存，可以先结束 loading 让页面显示，后台慢慢刷
        loading.value = false;
    }

    const fetchStatsWithRetry = async (url, retries = 3) => {
        try {
            const resp = await axios.get(url);
            if (resp.status === 202 && retries > 0) {
                await new Promise(r => setTimeout(r, 2000));
                return fetchStatsWithRetry(url, retries - 1);
            }
            return resp.data;
        } catch (e) { throw e; }
    };

    try {
        // 合并请求逻辑
        const results = await Promise.allSettled([
            axios.get(baseApi),
            fetchStatsWithRetry(`${baseApi}/stats/commit_activity`),
            axios.get(`${baseApi}/contributors`, { params: { per_page: 6 } })
        ]);

        const [mainResult, commitResult, contribResult] = results;

        // 处理主数据
        if (mainResult.status === 'fulfilled') {
            repoData.value = mainResult.value.data;
        } else if (!isFromCache.value) {
            // 如果主数据失败且没缓存，才报错
            if (mainResult.reason?.response?.status === 403) {
                error.value = false; // 不直接报错显示 Error Slate
                repoData.value.description = "API Rate Limit Exceeded. Using static data.";
            } else {
                error.value = true;
            }
        }

        // 处理提交统计
        if (commitResult.status === 'fulfilled') {
            const recentWeeks = Array.isArray(commitResult.value) ? commitResult.value.slice(-12) : [];
            commitStats.value = recentWeeks.flatMap(w => w.days);
        }

        // 处理贡献者
        if (contribResult.status === 'fulfilled') {
            const contribResp = contribResult.value;
            const contribList = Array.isArray(contribResp.data) ? contribResp.data : [];
            contributors.value = contribList.slice(0, 6);

            // 探测总数
            let totalContribs = null;
            const link = contribResp.headers && contribResp.headers.link;
            if (link) {
                try {
                    const probe = await axios.get(`${baseApi}/contributors`, { params: { per_page: 1 } });
                    const probeLink = probe.headers && probe.headers.link;
                    if (probeLink) {
                        const m = probeLink.match(/[?&]page=(\d+)[^>]*>;\s*rel="last"/);
                        if (m) totalContribs = parseInt(m[1], 10);
                    }
                } catch (e) { }
            }

            if (totalContribs !== null) {
                contributorsHasMore.value = totalContribs > contributors.value.length;
                contributorsExtraCount.value = Math.max(0, totalContribs - contributors.value.length);
            } else {
                contributorsHasMore.value = contribList.length >= 6;
            }
        }

        // 如果获取成功，则更新缓存
        if (mainResult.status === 'fulfilled') {
            isFromCache.value = false;
            saveToCache(owner, repo, {
                repoData: repoData.value,
                commitStats: commitStats.value,
                contributors: contributors.value,
                contributorsHasMore: contributorsHasMore.value,
                contributorsExtraCount: contributorsExtraCount.value
            });
        }
    } catch (err) {
        console.error('GitHub API Error:', err);
        // 如果出错但我们有预填充或缓存的数据，不显示全屏错误
        if (!repoData.value) error.value = true;
    } finally {
        loading.value = false;
    }
};

onMounted(() => fetchRepoDetails());
</script>

<template>
    <div class="repo-embed-container" :class="{ 'is-loading': loading, 'is-error': error }">
        <div v-if="loading" class="terminal-loader">
            <div class="cursor"></div>
            <span>ANALYZING_CORE_REPOSITORY...</span>
        </div>

        <div v-else-if="error" class="error-slate">
            <div class="error-icon">!</div>
            <div class="error-text">REPOSITORY_ACCESS_DENIED</div>
            <a :href="props.repourl" target="_blank" class="emergency-link">MANUAL_ACCESS</a>
        </div>

        <div v-else class="repo-card">
            <div class="card-accent-line"></div>

            <div v-if="isFromCache" class="cache-indicator" :title="'Last updated: ' + cacheTime">
                <span class="cache-label">OFFLINE_CACHE</span>
                <span class="cache-time">{{ cacheTime }}</span>
            </div>

            <div class="flex-layout">
                <div class="main-info">
                    <header class="repo-header">
                        <div class="owner-chip"><span class="prefix">@</span>{{ repoData.owner.login }}</div>
                        <h3 class="repo-name">
                            <a :href="repoData.html_url" target="_blank">{{ repoData.name }}</a>
                        </h3>
                    </header>

                    <p class="repo-bio">{{ repoData.description || 'No description provided for this stream.' }}</p>

                    <div class="repo-meta-strip">
                        <div class="meta-item star">
                            <svg class="icon" viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
                                <path
                                    d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z">
                                </path>
                            </svg>
                            <span>{{ formatCount(repoData.stargazers_count) }}</span>
                        </div>
                        <div class="meta-item fork">
                            <svg class="icon" viewBox="0 0 16 16" width="14" height="14" fill="currentColor">
                                <path
                                    d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 10a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z">
                                </path>
                            </svg>
                            <span>{{ formatCount(repoData.forks_count) }}</span>
                        </div>
                        <div class="meta-item language" v-if="repoData.language">
                            <span class="lang-dot"></span>
                            <span>{{ repoData.language }}</span>
                        </div>
                    </div>
                </div>

                <div class="visual-panel">
                    <div class="activity-section">
                        <div class="section-label">COMMIT_PULSE (84D)</div>
                        <div class="heartbeat-container">
                            <svg viewBox="0 0 100 20" preserveAspectRatio="none" class="heartbeat-svg">
                                <defs>
                                    <linearGradient id="line-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stop-color="#44d07a" />
                                        <stop offset="100%" stop-color="#4aa9ff" />
                                    </linearGradient>
                                    <linearGradient id="area-grad" x1="0%" y1="0%" x2="0%" y2="100%">
                                        <stop offset="0%" stop-color="#44d07a" stop-opacity="0.45" />
                                        <stop offset="100%" stop-color="#44d07a" stop-opacity="0" />
                                    </linearGradient>
                                    <mask id="scan-mask">
                                        <rect width="30%" height="100%" x="-30%" fill="white" class="mask-rect" />
                                    </mask>
                                </defs>
                                <path :d="heartbeatPath + ' L 100,20 L 0,20 Z'" fill="url(#area-grad)"
                                    class="heartbeat-area" />
                                <path :d="heartbeatPath" fill="none" class="heartbeat-bg-line" />
                                <path :d="heartbeatPath" fill="none" class="heartbeat-line" stroke="url(#line-grad)" />
                                <path :d="heartbeatPath" fill="none" class="heartbeat-scan" stroke="#fff"
                                    mask="url(#scan-mask)" />
                            </svg>
                        </div>
                    </div>

                    <div class="growth-section">
                        <div class="section-label">STAR_MOMENTUM</div>
                        <div class="sparkline">
                            <svg viewBox="0 0 120 30" class="spark-svg">
                                <defs>
                                    <linearGradient id="star-grad" x1="0%" y1="0%" x2="0%" y2="100%">
                                        <stop offset="0%" stop-color="#4aa9ff" stop-opacity="0.35" />
                                        <stop offset="100%" stop-color="#4aa9ff" stop-opacity="0" />
                                    </linearGradient>
                                </defs>
                                <path :d="generateStarPath" fill="url(#star-grad)" class="star-area" />
                                <path :d="generateStarPath.replace(' L 0,30', '').replace(' L 120,30 Z', '')"
                                    fill="none" class="path-curve" />
                                <circle :cx="120" :cy="12" r="2.5" class="glow-point" />
                            </svg>
                        </div>
                    </div>
                </div>
            </div>

            <footer class="repo-footer">
                <div class="contributors">
                    <div class="contributor-stack">
                        <img v-for="c in contributors" :key="c.id" :src="c.avatar_url" :title="c.login"
                            class="contributor-avatar" />
                        <div v-if="contributorsHasMore" class="contributor-extra"
                            :title="contributorsExtraCount ? '+' + contributorsExtraCount + ' more contributors' : 'more contributors'"
                            :aria-label="contributorsExtraCount ? ('+' + contributorsExtraCount + ' more contributors') : 'more contributors'"
                            role="img">{{ contributorsExtraCount ? '+' + contributorsExtraCount : '…' }}</div>
                    </div>
                </div>
                <div class="system-tag">
                    <span class="status-dot"></span>
                    <span class="tag-code">DATA_STREAM::ALIVE</span>
                </div>
            </footer>
        </div>
    </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Mono&display=swap');

.repo-embed-container {
    --bg-dark: linear-gradient(180deg, #071126 0%, #0b1220 100%);
    --border-color: rgba(255, 255, 255, 0.06);
    --repo-green: #44d07a;
    --repo-blue: #4aa9ff;
    --text-main: #e7f3ff;
    --text-dim: #9fb0bf;
    margin: 1.5rem 0;
    position: relative;
    border-radius: 12px;
    background: var(--bg-dark);
    font-family: 'JetBrains Mono', monospace;
    overflow: hidden;
}

.repo-card {
    padding: 1.25rem;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.02) 0%, transparent 100%);
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 200px;
    box-sizing: border-box;
    gap: 0.75rem;
    box-shadow: 0 8px 24px rgba(2, 8, 20, 0.55);
}

.cache-indicator {
    position: absolute;
    top: 10px;
    left: 10px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    z-index: 20;
    pointer-events: none;
}

.cache-label {
    background: rgba(255, 193, 7, 0.9);
    color: #000;
    font-size: 0.6rem;
    font-weight: 800;
    padding: 1px 4px;
    border-radius: 3px;
    letter-spacing: 0.05em;
    box-shadow: 0 0 10px rgba(255, 193, 7, 0.2);
}

.cache-time {
    font-size: 0.5rem;
    color: var(--text-dim);
    opacity: 0.7;
    white-space: nowrap;
}

.card-accent-line {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--repo-blue), var(--repo-green), transparent);
    z-index: 5;
}

.flex-layout {
    display: flex;
    gap: 1.5rem;
    align-items: flex-start;
    flex: 1;
    min-height: 0;
}

.main-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    height: 100%;
}

.repo-name {
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    font-weight: 700;
}

.repo-name a {
    color: var(--text-main);
    text-decoration: none;
}

.repo-bio {
    font-size: 0.85rem;
    color: var(--text-dim);
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 0.5rem;
    flex: 1;
}

.repo-meta-strip {
    display: flex;
    gap: 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-dim);
    flex-shrink: 0;
    margin-top: auto;
}

.repo-meta-strip .meta-item span {
    color: var(--text-main);
}

.visual-panel {
    flex: 0 0 160px;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    border-left: 1px solid var(--border-color);
    padding-left: 1rem;
    flex-shrink: 0;
}

.heartbeat-container {
    height: 28px;
    position: relative;
    background: rgba(63, 185, 80, 0.03);
    border-radius: 4px;
    padding: 2px;
}

.heartbeat-svg {
    width: 100%;
    height: 100%;
    overflow: visible;
}

.heartbeat-line {
    stroke-width: 1.5;
    filter: drop-shadow(0 0 3px var(--repo-green));
}

.mask-rect {
    animation: scan-move 4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

@keyframes scan-move {
    0% {
        x: -30%;
    }

    100% {
        x: 100%;
    }
}

.sparkline {
    height: 34px;
    width: 100%;
    overflow: visible;
    background: rgba(33, 139, 255, 0.03);
    border-radius: 4px;
}

.path-curve {
    stroke: var(--repo-blue);
    stroke-width: 2;
    filter: drop-shadow(0 0 4px var(--repo-blue));
}

.glow-point {
    fill: #fff;
    animation: point-pulse 2s infinite;
}

@keyframes point-pulse {

    0%,
    100% {
        r: 1.5;
        opacity: 0.5;
    }

    50% {
        r: 2.5;
        opacity: 1;
    }
}

.repo-footer {
    border-top: 1px dashed var(--border-color);
    padding-top: 0.75rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
}

.contributor-stack {
    gap: calc(0.5rem);
    display: flex;
}

.contributor-avatar {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid var(--bg-dark);
    margin-left: -8px;
}

.contributor-avatar:hover {
    transform: scale(1.2);
    z-index: 10;
}

.contributor-avatar:first-child {
    margin-left: 0;
}

.system-tag {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.65rem;
    color: var(--repo-green);
}

.status-dot {
    width: 6px;
    height: 6px;
    background: var(--repo-green);
    border-radius: 50%;
    box-shadow: 0 0 8px var(--repo-green);
}

.section-label {
    font-size: 0.68rem;
    color: var(--text-main);
    opacity: 0.95;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.owner-chip {
    color: var(--text-dim);
    font-size: 0.85rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.owner-chip .prefix {
    color: var(--text-main);
    background: rgba(74, 169, 255, 0.06);
    padding: 0.06rem 0.28rem;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.8rem;
}

.contributor-extra {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    margin-left: -8px;
    border: 2px solid var(--bg-dark);
    background: rgba(255, 255, 255, 0.04);
    color: var(--text-main);
    font-size: 0.72rem;
    font-weight: 700;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.45);
}

@media (max-width: 600px) {
    .visual-panel {
        display: none;
    }

    .repo-embed-container {
        max-height: none;
    }
}
</style>
