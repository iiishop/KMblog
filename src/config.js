const config = {
    ProjectUrl: 'https://iiishop.github.io',//博客的基础URL
    BlogName: 'iiishop的博客',//博客名称
    ShortDesc: 'XXXXDESC',//博客的简短描述
    CryptoTag: '暂未公开',//加密文章标签，包含此标签的文章将被收集到Crypto.json
    BackgroundImg: '/assets/background.png',//博客背景图片的URL
    BackgroundImgOpacity: 0.5,//覆盖在背景图片上的白色层的透明度
    BackgroundImgBlur: 20.0,//覆盖在背景图片上的白色层的模糊度

    // === New Theme Configuration System ===
    LightTheme: 'day',        // Theme palette to use for light mode
    DarkTheme: 'dark',        // Theme palette to use for dark mode

    // Theme behavior settings
    defaultMode: 'system',    // 'light', 'dark', or 'system' (follows OS preference)
    transitionDuration: 300,  // Theme transition duration in milliseconds
    enableTransitions: true,  // Enable smooth theme transitions
    enableSystemDetection: true, // Enable automatic system theme detection

    // Available theme names (must match [data-theme] values in color.css)
    availableThemes: ['day', 'dark', 'night', 'bright'],


    HeadImg: '/assets/head.png',//头像图片的URL
    Name: 'iiishop',//作者名称
    Description: 'A social network for finding love and making friends',//作者描述
    PostsPerPage: 5,//每页显示的文章数量（最小值，实际会根据侧边栏高度动态调整）
    EnableDynamicPostsPerPage: true,//是否启用动态文章数量（根据侧边栏高度自动调整）
    ChangeInfoAndTipPosition: false,//是否调换Info和Tip的位置
    InfoListUp: [
        'SelfIntroductionPanel',
        'CollectionPanel',
    ],//Info列表，在页面默认添加的InfoList的上面出现
    InfoListDown: [
        'ClockPanel',
        'CalendarPanel',
    ],//Info列表，在页面默认添加的InfoList的下面出现
    TipListUp: [
    ],//Tip列表，在页面默认添加的TipList的上面出现
    TipListDown: [
    ],//Tip列表，在页面默认添加的TipList的下面出现
    MainListUp: [
    ],//Main列表，在页面默认添加的MainList的上面出现
    MainListDown: [
    ],//Main列表，在页面默认添加的MainList的下面出现
    InfoListFloat: [

    ],//Info浮动列表，开始时显示在InfoList的最下方，之后根据页面滚动位置自动调整位置
    TipListFloat: [
    ],//Tip浮动列表，开始时显示在TipList的最下方，之后根据页面滚动位置自动调整位置

    // GitHub API Configuration
    // Get a token from: https://github.com/settings/tokens (no scopes needed for public repos)
    // Increases rate limit from 60 to 5000 requests/hour
    GitHubToken: '', // Leave empty for unauthenticated requests (60/hour limit)

    // Utterances Comments Configuration
    // Learn more: https://utteranc.es/
    UtterancesConfig: {
        enabled: false,                    // Enable/disable comments
        repo: '',                          // GitHub repository (format: 'username/repo')
        issueMapping: 'pathname',          // How to map pages to issues: 'pathname', 'url', 'title', 'og:title'
        label: 'comment',                  // Label for GitHub issues
        theme: '',                         // Leave empty to auto-match blog theme, or specify: 'github-light', 'github-dark', 'preferred-color-scheme', etc.

        // Advanced: Custom theme mapping for different blog themes
        // Maps blog themes to Utterances themes
        themeMapping: {
            'day': 'github-light',
            'dark': 'github-dark',
            'night': 'github-dark',
            'bright': 'github-light'
        }
    },

    // Social Links. 社交链接
    Links: [
        {
            name: 'GitHub',
            url: 'https://github.com/iiishop',
        },
        {
            name: 'LinkedIn',
            url: 'https://www.linkedin.com/in/',
        },
        {
            name: 'Twitter',
            url: 'https://twitter.com/',
        },
        {
            name: 'Instagram',
            url: 'https://www.instagram.com/',
        },
        {
            name: 'Facebook',
            url: 'https://www.facebook.com/',
        },
        {
            name: 'YouTube',
            url: 'https://www.youtube.com/',
        },
        {
            name: 'Pinterest',
            url: 'https://www.pinterest.com/',
        },
        {
            name: 'Steam',
            url: 'https://steamcommunity.com/',
        },
        {
            name: 'Twitch',
            url: 'https://www.twitch.tv/',
        },
        {
            name: 'Reddit',
            url: 'https://www.reddit.com/',
        },
    ]
};
export default config;