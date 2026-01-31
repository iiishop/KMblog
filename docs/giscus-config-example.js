// Giscus 配置示例
// 复制此配置到 src/config.js 的 Giscus 部分

// 示例 1: 基础配置（最小化配置）
const basicConfig = {
    enabled: true,
    repo: 'username/repo',                  // 替换为你的仓库
    repoId: 'R_kgDOxxxxxxx',               // 从 giscus.app 获取
    category: 'Announcements',
    categoryId: 'DIC_kwDOxxxxxxx',         // 从 giscus.app 获取
    mapping: 'pathname',
    strict: '0',
    reactionsEnabled: '1',
    emitMetadata: '0',
    inputPosition: 'bottom',
    theme: 'preferred_color_scheme',
    lang: 'zh-CN',
    loading: 'lazy',

    markdownPanel: {
        enabled: true,
        showReactions: true,
        position: 'bottom',
    },
    imageModal: {
        enabled: true,
        showReactions: true,
        compact: true,
    }
};

// 示例 2: 仅文章页面启用评论
const articleOnlyConfig = {
    enabled: true,
    repo: 'username/repo',
    repoId: 'R_kgDOxxxxxxx',
    category: 'Announcements',
    categoryId: 'DIC_kwDOxxxxxxx',
    mapping: 'pathname',
    strict: '0',
    reactionsEnabled: '1',
    emitMetadata: '0',
    inputPosition: 'bottom',
    theme: 'preferred_color_scheme',
    lang: 'zh-CN',
    loading: 'lazy',

    markdownPanel: {
        enabled: true,          // 文章页面启用
        showReactions: true,
        position: 'bottom',
    },
    imageModal: {
        enabled: false,         // 图片模态框禁用
        showReactions: true,
        compact: true,
    }
};

// 示例 3: 英文博客配置
const englishBlogConfig = {
    enabled: true,
    repo: 'username/repo',
    repoId: 'R_kgDOxxxxxxx',
    category: 'General',
    categoryId: 'DIC_kwDOxxxxxxx',
    mapping: 'url',             // 使用 URL 映射
    strict: '1',                // 严格匹配
    reactionsEnabled: '1',
    emitMetadata: '0',
    inputPosition: 'top',       // 输入框在顶部
    theme: 'light',             // 固定浅色主题
    lang: 'en',                 // 英文
    loading: 'eager',           // 立即加载

    markdownPanel: {
        enabled: true,
        showReactions: true,
        position: 'bottom',
    },
    imageModal: {
        enabled: true,
        showReactions: true,
        compact: true,
    }
};

// 示例 4: 完全禁用评论
const disabledConfig = {
    enabled: false,             // 全局禁用
    repo: '',
    repoId: '',
    category: '',
    categoryId: '',
    mapping: 'pathname',
    strict: '0',
    reactionsEnabled: '1',
    emitMetadata: '0',
    inputPosition: 'bottom',
    theme: 'preferred_color_scheme',
    lang: 'zh-CN',
    loading: 'lazy',

    markdownPanel: {
        enabled: false,
        showReactions: true,
        position: 'bottom',
    },
    imageModal: {
        enabled: false,
        showReactions: true,
        compact: true,
    }
};

// 示例 5: 自定义主题配置
const customThemeConfig = {
    enabled: true,
    repo: 'username/repo',
    repoId: 'R_kgDOxxxxxxx',
    category: 'Announcements',
    categoryId: 'DIC_kwDOxxxxxxx',
    mapping: 'pathname',
    strict: '0',
    reactionsEnabled: '1',
    emitMetadata: '0',
    inputPosition: 'bottom',
    // 使用自定义主题 CSS URL
    theme: 'https://example.com/custom-giscus-theme.css',
    lang: 'zh-CN',
    loading: 'lazy',

    markdownPanel: {
        enabled: true,
        showReactions: true,
        position: 'bottom',
    },
    imageModal: {
        enabled: true,
        showReactions: true,
        compact: true,
    }
};

// 可用的语言选项
const availableLanguages = [
    'ar',      // Arabic
    'de',      // German
    'en',      // English
    'es',      // Spanish
    'fr',      // French
    'id',      // Indonesian
    'it',      // Italian
    'ja',      // Japanese
    'ko',      // Korean
    'pl',      // Polish
    'pt',      // Portuguese
    'ro',      // Romanian
    'ru',      // Russian
    'tr',      // Turkish
    'vi',      // Vietnamese
    'zh-CN',   // Simplified Chinese
    'zh-TW',   // Traditional Chinese
];

// 可用的主题选项
const availableThemes = [
    'light',                        // 浅色
    'light_high_contrast',          // 浅色高对比度
    'light_protanopia',             // 浅色（红色盲）
    'light_tritanopia',             // 浅色（蓝色盲）
    'dark',                         // 深色
    'dark_high_contrast',           // 深色高对比度
    'dark_protanopia',              // 深色（红色盲）
    'dark_tritanopia',              // 深色（蓝色盲）
    'dark_dimmed',                  // 深色（柔和）
    'preferred_color_scheme',       // 跟随系统
    'transparent_dark',             // 透明深色
    'noborder_light',               // 无边框浅色
    'noborder_dark',                // 无边框深色
    'noborder_gray',                // 无边框灰色
    'cobalt',                       // 钴蓝
    'purple_dark',                  // 紫色深色
    // 或自定义 CSS URL
];

// 可用的映射方式
const availableMappings = [
    'pathname',     // 路径名（推荐）
    'url',          // 完整 URL
    'title',        // 页面标题
    'og:title',     // Open Graph 标题
    'specific',     // 特定术语（需要设置 term）
    'number',       // Discussion 编号
];

export {
    basicConfig,
    articleOnlyConfig,
    englishBlogConfig,
    disabledConfig,
    customThemeConfig,
    availableLanguages,
    availableThemes,
    availableMappings
};
