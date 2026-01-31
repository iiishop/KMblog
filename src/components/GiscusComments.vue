<template>
    <div class="giscus-wrapper" :class="wrapperClasses">
        <!-- 快捷反应按钮 -->
        <div v-if="showQuickReactions" class="quick-reactions">
            <div class="reactions-header">
                <span class="reactions-title">{{ componentType === 'image' ? '快速互动' : '快速反应' }}</span>
                <span class="reactions-subtitle">{{ componentType === 'image' ? '点击表达你的感受' : '一键表达你的想法' }}</span>
            </div>
            <div class="reactions-grid">
                <button v-for="reaction in quickReactions" :key="reaction.name" class="reaction-btn"
                    :class="{ 'active': reaction.active }" @click="handleQuickReaction(reaction)"
                    :title="reaction.label">
                    <div class="reaction-icon" v-html="reaction.svg"></div>
                    <span class="reaction-label">{{ reaction.label }}</span>
                    <span v-if="reaction.count > 0" class="reaction-count">{{ reaction.count }}</span>
                </button>
            </div>
        </div>

        <!-- Giscus 评论区 -->
        <div ref="giscusContainer" class="giscus-container"></div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, computed } from 'vue';
import config from '@/config';

const props = defineProps({
    // Component type: 'markdown' or 'image'
    componentType: {
        type: String,
        default: 'markdown',
        validator: (value) => ['markdown', 'image'].includes(value)
    },
    // Custom term for mapping (overrides default pathname)
    term: {
        type: String,
        default: ''
    },
    // Compact mode for smaller spaces
    compact: {
        type: Boolean,
        default: false
    },
    // Emphasize reactions (likes) over comments
    emphasizeReactions: {
        type: Boolean,
        default: false
    },
    // Custom theme override
    customTheme: {
        type: String,
        default: ''
    },
    // Show quick reactions (deprecated - Giscus has built-in reactions)
    showQuickReactions: {
        type: Boolean,
        default: false
    }
});

const giscusContainer = ref(null);
let giscusScript = null;

// 快捷反应数据（使用 SVG 图标代替 emoji）
const quickReactions = ref([
    {
        name: 'thumbsup',
        label: '赞',
        svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
        </svg>`,
        count: 0,
        active: false
    },
    {
        name: 'heart',
        label: '喜欢',
        svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
        </svg>`,
        count: 0,
        active: false
    },
    {
        name: 'rocket',
        label: '精彩',
        svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"></path>
            <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path>
            <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path>
            <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path>
        </svg>`,
        count: 0,
        active: false
    },
    {
        name: 'laugh',
        label: '有趣',
        svg: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
            <line x1="9" y1="9" x2="9.01" y2="9"></line>
            <line x1="15" y1="9" x2="15.01" y2="9"></line>
        </svg>`,
        count: 0,
        active: false
    }
]);

// 计算 wrapper 的 class
const wrapperClasses = computed(() => {
    return {
        'compact-mode': props.compact,
        'reactions-emphasized': props.emphasizeReactions,
        'markdown-style': props.componentType === 'markdown',
        'image-style': props.componentType === 'image'
    };
});

// Get component-specific config
const getComponentConfig = () => {
    const baseConfig = config.Giscus;
    if (props.componentType === 'image') {
        return { ...baseConfig, ...baseConfig.imageModal };
    }
    return { ...baseConfig, ...baseConfig.markdownPanel };
};

// 处理快捷反应点击
const handleQuickReaction = (reaction) => {
    // 切换激活状态
    reaction.active = !reaction.active;

    // 模拟计数变化（实际应该通过 Giscus API）
    if (reaction.active) {
        reaction.count++;
    } else {
        reaction.count = Math.max(0, reaction.count - 1);
    }

    // 发送消息到 Giscus iframe 触发反应
    const iframe = giscusContainer.value?.querySelector('iframe.giscus-frame');
    if (iframe) {
        // Giscus 支持通过 postMessage 触发反应
        const message = {
            setConfig: {
                reaction: reaction.name
            }
        };
        iframe.contentWindow?.postMessage({ giscus: message }, 'https://giscus.app');
    }
};

// Load Giscus script
const loadGiscus = () => {
    if (!config.Giscus.enabled) return;
    if (!config.Giscus.repo || !config.Giscus.repoId) {
        console.warn('[Giscus] Missing required configuration: repo and repoId');
        return;
    }

    const componentConfig = getComponentConfig();
    if (!componentConfig.enabled) return;

    // Remove existing script if any
    if (giscusScript) {
        giscusScript.remove();
    }

    // Clear container
    if (giscusContainer.value) {
        giscusContainer.value.innerHTML = '';
    }

    // Create new script
    giscusScript = document.createElement('script');
    giscusScript.src = 'https://giscus.app/client.js';
    giscusScript.setAttribute('data-repo', config.Giscus.repo);
    giscusScript.setAttribute('data-repo-id', config.Giscus.repoId);
    giscusScript.setAttribute('data-category', config.Giscus.category);
    giscusScript.setAttribute('data-category-id', config.Giscus.categoryId);
    giscusScript.setAttribute('data-mapping', props.term ? 'specific' : config.Giscus.mapping);

    if (props.term) {
        giscusScript.setAttribute('data-term', props.term);
    }

    giscusScript.setAttribute('data-strict', config.Giscus.strict);
    giscusScript.setAttribute('data-reactions-enabled', config.Giscus.reactionsEnabled);
    giscusScript.setAttribute('data-emit-metadata', config.Giscus.emitMetadata);
    giscusScript.setAttribute('data-input-position', config.Giscus.inputPosition);
    // 使用默认主题或自定义主题
    giscusScript.setAttribute('data-theme', props.customTheme || config.Giscus.theme || 'preferred_color_scheme');
    giscusScript.setAttribute('data-lang', config.Giscus.lang);
    giscusScript.setAttribute('data-loading', config.Giscus.loading);
    giscusScript.crossOrigin = 'anonymous';
    giscusScript.async = true;

    if (giscusContainer.value) {
        giscusContainer.value.appendChild(giscusScript);
    }
};

// Update theme dynamically
const updateTheme = (newTheme) => {
    const iframe = giscusContainer.value?.querySelector('iframe.giscus-frame');
    if (iframe) {
        const message = {
            setConfig: {
                theme: newTheme
            }
        };
        iframe.contentWindow?.postMessage({ giscus: message }, 'https://giscus.app');
    }
};

// Watch for term changes (e.g., when navigating between images)
watch(() => props.term, () => {
    loadGiscus();
});

// Watch for theme changes
watch(() => props.customTheme, (newTheme) => {
    if (newTheme) {
        updateTheme(newTheme);
    }
});

onMounted(() => {
    loadGiscus();
});

onUnmounted(() => {
    if (giscusScript) {
        giscusScript.remove();
    }
});

// Expose method to reload comments
defineExpose({
    reload: loadGiscus,
    updateTheme
});
</script>

<style scoped>
/* ========================================
   基础样式
   ======================================== */
.giscus-wrapper {
    width: 100%;
    transition: var(--theme-transition-colors);
}

.giscus-container {
    width: 100%;
    min-height: 150px;
}

/* ========================================
   快捷反应区域
   ======================================== */
.quick-reactions {
    margin-bottom: 2rem;
    padding: 1.5rem;
    border-radius: 12px;
    transition: all 0.3s ease;
}

.reactions-header {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-bottom: 1rem;
}

.reactions-title {
    font-size: 1rem;
    font-weight: 600;
    transition: var(--theme-transition-colors);
}

.reactions-subtitle {
    font-size: 0.85rem;
    opacity: 0.7;
    transition: var(--theme-transition-colors);
}

.reactions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 0.75rem;
}

.reaction-btn {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 0.75rem;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

.reaction-btn::before {
    content: '';
    position: absolute;
    inset: 0;
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

.reaction-icon {
    width: 28px;
    height: 28px;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.reaction-icon :deep(svg) {
    width: 100%;
    height: 100%;
    transition: all 0.3s ease;
}

.reaction-label {
    font-size: 0.8rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.reaction-count {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    min-width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 0.4rem;
    border-radius: 10px;
    font-size: 0.7rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.reaction-btn:hover {
    transform: translateY(-2px);
}

.reaction-btn:hover .reaction-icon {
    transform: scale(1.15);
}

.reaction-btn:active {
    transform: translateY(0) scale(0.95);
}

/* ========================================
   Markdown 风格 - 专业长文
   ======================================== */
.giscus-wrapper.markdown-style .quick-reactions {
    background: linear-gradient(135deg,
            var(--theme-content-bg) 0%,
            var(--theme-panel-bg) 100%);
    border: 1px solid var(--theme-content-border);
    box-shadow: 0 2px 8px var(--theme-shadow-sm);
}

.giscus-wrapper.markdown-style .reactions-title {
    color: var(--theme-content-text);
    font-family: 'Noto Serif SC', 'Merriweather', Georgia, serif;
}

.giscus-wrapper.markdown-style .reactions-subtitle {
    color: var(--theme-meta-text);
}

.giscus-wrapper.markdown-style .reaction-btn {
    background: var(--theme-content-bg);
    border: 1.5px solid var(--theme-border-light);
    color: var(--theme-content-text);
}

.giscus-wrapper.markdown-style .reaction-btn::before {
    background: var(--theme-gradient);
}

.giscus-wrapper.markdown-style .reaction-btn:hover {
    border-color: var(--theme-primary);
    box-shadow: 0 4px 12px var(--theme-shadow-md);
}

.giscus-wrapper.markdown-style .reaction-btn:hover::before {
    opacity: 0.1;
}

.giscus-wrapper.markdown-style .reaction-btn.active {
    background: var(--theme-gradient);
    border-color: transparent;
    color: var(--theme-button-text);
    box-shadow: 0 4px 16px var(--theme-primary);
}

.giscus-wrapper.markdown-style .reaction-btn.active .reaction-icon :deep(svg) {
    stroke: var(--theme-button-text);
    fill: var(--theme-button-text);
    fill-opacity: 0.2;
}

.giscus-wrapper.markdown-style .reaction-count {
    background: var(--theme-primary);
    color: var(--theme-button-text);
}

.giscus-wrapper.markdown-style .giscus-container {
    padding: 2rem;
    background: var(--theme-content-bg);
    border-radius: 12px;
    border: 1px solid var(--theme-content-border);
    box-shadow: 0 2px 8px var(--theme-shadow-sm);
}

/* ========================================
   Image 风格 - 小红书互动
   ======================================== */
.giscus-wrapper.image-style .quick-reactions {
    background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
    border: 2px solid #ffcdd2;
}

.giscus-wrapper.image-style .reactions-title {
    color: #d32f2f;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.giscus-wrapper.image-style .reactions-subtitle {
    color: #e57373;
}

.giscus-wrapper.image-style .reaction-btn {
    background: #fff;
    border: 2px solid #ffebee;
    color: #d32f2f;
}

.giscus-wrapper.image-style .reaction-btn:hover {
    border-color: #ff2442;
    background: #fff5f5;
    box-shadow: 0 4px 16px rgba(255, 36, 66, 0.15);
}

.giscus-wrapper.image-style .reaction-btn.active {
    background: linear-gradient(135deg, #ff2442 0%, #ff6b6b 100%);
    border-color: #ff2442;
    color: #fff;
    box-shadow: 0 6px 20px rgba(255, 36, 66, 0.3);
}

.giscus-wrapper.image-style .reaction-btn.active .reaction-icon :deep(svg) {
    stroke: #fff;
    fill: #fff;
    fill-opacity: 0.3;
}

.giscus-wrapper.image-style .reaction-count {
    background: #ff2442;
    color: #fff;
    font-weight: 700;
}

.giscus-wrapper.image-style .giscus-container {
    padding: 1.5rem;
    background: #fff;
    border-radius: 12px;
    border: 2px solid #ffebee;
}

/* ========================================
   Compact 模式
   ======================================== */
.giscus-wrapper.compact-mode {
    margin: 1rem 0;
}

.giscus-wrapper.compact-mode .quick-reactions {
    padding: 1rem;
    margin-bottom: 1rem;
}

.giscus-wrapper.compact-mode .reactions-grid {
    grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
    gap: 0.5rem;
}

.giscus-wrapper.compact-mode .reaction-btn {
    padding: 0.75rem 0.5rem;
}

.giscus-wrapper.compact-mode .reaction-icon {
    width: 24px;
    height: 24px;
}

.giscus-wrapper.compact-mode .reaction-label {
    font-size: 0.75rem;
}

.giscus-wrapper.compact-mode .giscus-container {
    min-height: 100px;
    padding: 1rem;
}

/* ========================================
   响应式设计
   ======================================== */
@media (max-width: 768px) {
    .reactions-grid {
        grid-template-columns: repeat(3, 1fr);
    }

    .reaction-btn {
        padding: 0.75rem 0.5rem;
    }

    .reaction-icon {
        width: 24px;
        height: 24px;
    }

    .reaction-label {
        font-size: 0.75rem;
    }
}

@media (max-width: 480px) {
    .quick-reactions {
        padding: 1rem;
    }

    .reactions-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
    }

    .reaction-btn {
        padding: 0.6rem 0.4rem;
    }

    .reaction-icon {
        width: 20px;
        height: 20px;
    }

    .reaction-label {
        font-size: 0.7rem;
    }

    .reaction-count {
        min-width: 18px;
        height: 18px;
        font-size: 0.65rem;
    }
}

/* ========================================
   Giscus iframe 样式覆盖
   ======================================== */
.giscus-wrapper :deep(.giscus-frame) {
    border-radius: 8px;
}

/* Markdown 风格的 iframe */
.giscus-wrapper.markdown-style :deep(.giscus-frame) {
    border: 1px solid var(--theme-border-light);
}

/* Image 风格的 iframe */
.giscus-wrapper.image-style :deep(.giscus-frame) {
    border: 2px solid #ffebee;
}
</style>
