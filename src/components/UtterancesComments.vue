<template>
    <div class="utterances-comments" ref="commentsContainer">
        <div v-if="!isEnabled" class="comments-disabled">
            <p>评论功能未启用</p>
        </div>
        <div v-else-if="!isConfigured" class="comments-not-configured">
            <p>评论系统未配置，请在设置中配置 Utterances</p>
        </div>
        <div v-else ref="utterancesContainer" class="utterances-container"></div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue';
import config from '@/config';

const props = defineProps({
    // 用于标识不同页面的评论，通常是文章路径或标题
    issueTitle: {
        type: String,
        default: ''
    },
    // 可选：覆盖配置中的仓库设置
    repo: {
        type: String,
        default: ''
    },
    // 可选：覆盖配置中的主题设置
    theme: {
        type: String,
        default: ''
    }
});

const commentsContainer = ref(null);
const utterancesContainer = ref(null);
const scriptElement = ref(null);

// 检查是否启用评论
const isEnabled = ref(false);
const isConfigured = ref(false);

// 获取当前主题
const getCurrentTheme = () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'day';
    const isDark = currentTheme === 'dark' || currentTheme === 'night';

    // 如果配置中指定了主题映射
    if (config.UtterancesConfig?.themeMapping) {
        return config.UtterancesConfig.themeMapping[currentTheme] ||
            (isDark ? 'github-dark' : 'github-light');
    }

    // 默认映射
    return isDark ? 'github-dark' : 'github-light';
};

// 加载 Utterances
const loadUtterances = () => {
    // 检查配置
    if (!config.UtterancesConfig?.enabled) {
        isEnabled.value = false;
        return;
    }

    isEnabled.value = true;

    const repo = props.repo || config.UtterancesConfig.repo;
    if (!repo) {
        isConfigured.value = false;
        console.warn('[Utterances] Repository not configured');
        return;
    }

    isConfigured.value = true;

    // 清除已存在的 utterances
    if (utterancesContainer.value) {
        utterancesContainer.value.innerHTML = '';
    }

    // 移除旧的 script 标签
    if (scriptElement.value) {
        scriptElement.value.remove();
        scriptElement.value = null;
    }

    // 创建新的 script 标签
    nextTick(() => {
        if (!utterancesContainer.value) return;

        const script = document.createElement('script');
        script.src = 'https://utteranc.es/client.js';
        script.setAttribute('repo', repo);

        // Issue 映射方式
        const issueMapping = config.UtterancesConfig.issueMapping || 'pathname';
        if (issueMapping === 'title' && props.issueTitle) {
            script.setAttribute('issue-term', 'title');
            script.setAttribute('label', props.issueTitle);
        } else {
            script.setAttribute('issue-term', issueMapping);
        }

        // 标签
        const label = config.UtterancesConfig.label || 'comment';
        script.setAttribute('label', label);

        // 主题
        const theme = props.theme || config.UtterancesConfig.theme || getCurrentTheme();
        script.setAttribute('theme', theme);

        // 跨域
        script.setAttribute('crossorigin', 'anonymous');

        // 异步加载
        script.async = true;

        scriptElement.value = script;
        utterancesContainer.value.appendChild(script);
    });
};

// 更新主题
const updateTheme = () => {
    if (!isEnabled.value || !isConfigured.value) return;

    const theme = props.theme || config.UtterancesConfig.theme || getCurrentTheme();

    // 使用 postMessage 更新主题
    const iframe = utterancesContainer.value?.querySelector('iframe.utterances-frame');
    if (iframe) {
        const message = {
            type: 'set-theme',
            theme: theme
        };
        iframe.contentWindow?.postMessage(message, 'https://utteranc.es');
    }
};

// 监听主题变化
const themeObserver = ref(null);

onMounted(() => {
    loadUtterances();

    // 监听主题变化
    themeObserver.value = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                console.log('[Utterances] Theme changed, updating...');
                updateTheme();
            }
        });
    });

    themeObserver.value.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
    });
});

onUnmounted(() => {
    if (themeObserver.value) {
        themeObserver.value.disconnect();
    }

    if (scriptElement.value) {
        scriptElement.value.remove();
    }
});

// 监听配置变化
watch(() => [props.repo, props.theme, props.issueTitle], () => {
    if (isEnabled.value && isConfigured.value) {
        loadUtterances();
    }
}, { deep: true });
</script>

<style scoped>
.utterances-comments {
    width: 100%;
    margin: 2rem 0;
    padding: 2rem;
    background: var(--theme-content-bg);
    border-radius: 12px;
    box-shadow: 0 2px 8px var(--theme-shadow-sm);
    transition: var(--theme-transition-colors);
}

.utterances-container {
    width: 100%;
    min-height: 200px;
}

.comments-disabled,
.comments-not-configured {
    text-align: center;
    padding: 3rem 2rem;
    color: var(--theme-meta-text);
    background: var(--theme-surface-hover);
    border-radius: 8px;
    border: 2px dashed var(--theme-border-light);
}

.comments-disabled p,
.comments-not-configured p {
    margin: 0;
    font-size: 1rem;
    font-weight: 500;
}

/* Utterances iframe 样式调整 */
.utterances-container :deep(.utterances) {
    max-width: 100%;
}

.utterances-container :deep(.utterances-frame) {
    width: 100%;
    border: none;
    background: transparent;
}

/* 响应式 */
@media (max-width: 768px) {
    .utterances-comments {
        padding: 1.5rem;
        margin: 1.5rem 0;
    }
}

@media (max-width: 640px) {
    .utterances-comments {
        padding: 1rem;
        margin: 1rem 0;
    }

    .comments-disabled,
    .comments-not-configured {
        padding: 2rem 1rem;
    }
}
</style>
