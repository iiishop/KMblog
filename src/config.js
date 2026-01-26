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

    // Theme palette definitions
    themePalettes: {
        day: {
            name: 'day',
            displayName: 'Day Theme',
            colors: {
                // Core colors
                bodyBackground: '#ffffff',
                bodyText: '#000000',

                // Panel colors
                panelBackground: '#f9f9f9',
                panelShadow: 'rgba(0, 0, 0, 0.1)',
                panelText: '#000000',
                panelBorder: 'rgba(0, 0, 0, 0.05)',

                // Header colors
                headerBackground: 'rgba(255, 215, 231, 0.616)',
                headerBackgroundScrolled: 'rgba(200, 255, 255, 0.7)',
                headerShadow: 'rgba(0, 0, 0, 0.1)',

                // Interactive colors
                linkColor: '#667eea',
                linkHover: '#764ba2',
                buttonBackground: '#667eea',
                buttonText: '#ffffff',
                buttonHover: '#5568d3',
                buttonActive: '#4a5bc4',

                // Semantic accent colors
                primary: '#667eea',
                primaryHover: '#5568d3',
                primaryActive: '#4a5bc4',
                primaryDisabled: '#b8c5f2',

                secondary: '#764ba2',
                secondaryHover: '#654091',
                secondaryActive: '#543580',
                secondaryDisabled: '#c5b3d9',

                accent: '#f093fb',
                accentHover: '#e87bf7',
                accentActive: '#e063f3',
                accentDisabled: '#f8c9fc',

                // State colors
                success: '#10b981',
                successHover: '#059669',
                successActive: '#047857',
                successDisabled: '#a7f3d0',

                warning: '#f59e0b',
                warningHover: '#d97706',
                warningActive: '#b45309',
                warningDisabled: '#fde68a',

                error: '#ef4444',
                errorHover: '#dc2626',
                errorActive: '#b91c1c',
                errorDisabled: '#fecaca',

                info: '#3b82f6',
                infoHover: '#2563eb',
                infoActive: '#1d4ed8',
                infoDisabled: '#bfdbfe',

                // Input and form states
                inputBackground: '#ffffff',
                inputBorder: '#d1d5db',
                inputBorderHover: '#9ca3af',
                inputBorderFocus: '#667eea',
                inputText: '#000000',
                inputPlaceholder: '#9ca3af',
                inputDisabled: '#f3f4f6',

                // Surface colors
                surfaceDefault: '#ffffff',
                surfaceHover: '#f9fafb',
                surfaceActive: '#f3f4f6',
                surfaceDisabled: '#e5e7eb'
            },
            accessibility: {
                contrastRatio: 4.5,
                wcagLevel: 'AA'
            }
        },

        dark: {
            name: 'dark',
            displayName: 'Dark Theme',
            colors: {
                // Core colors
                bodyBackground: '#121212',
                bodyText: '#e0e0e0',

                // Panel colors
                panelBackground: '#1e1e1e',
                panelShadow: 'rgba(0, 0, 0, 0.5)',
                panelText: '#e0e0e0',
                panelBorder: 'rgba(255, 255, 255, 0.1)',

                // Header colors
                headerBackground: 'rgba(20, 20, 30, 0.9)',
                headerBackgroundScrolled: 'rgba(30, 30, 40, 0.95)',
                headerShadow: 'rgba(0, 0, 0, 0.5)',

                // Interactive colors
                linkColor: '#a78bfa',
                linkHover: '#c084fc',
                buttonBackground: '#a78bfa',
                buttonText: '#ffffff',
                buttonHover: '#9575e8',
                buttonActive: '#8360d6',

                // Semantic accent colors
                primary: '#a78bfa',
                primaryHover: '#9575e8',
                primaryActive: '#8360d6',
                primaryDisabled: '#4c3d6b',

                secondary: '#c084fc',
                secondaryHover: '#ae6fea',
                secondaryActive: '#9c5ad8',
                secondaryDisabled: '#5a4370',

                accent: '#f093fb',
                accentHover: '#de7ee9',
                accentActive: '#cc69d7',
                accentDisabled: '#6b4570',

                // State colors
                success: '#34d399',
                successHover: '#10b981',
                successActive: '#059669',
                successDisabled: '#1e5a42',

                warning: '#fbbf24',
                warningHover: '#f59e0b',
                warningActive: '#d97706',
                warningDisabled: '#6b4e0f',

                error: '#f87171',
                errorHover: '#ef4444',
                errorActive: '#dc2626',
                errorDisabled: '#6b2626',

                info: '#60a5fa',
                infoHover: '#3b82f6',
                infoActive: '#2563eb',
                infoDisabled: '#1e3a5f',

                // Input and form states
                inputBackground: '#2a2a2a',
                inputBorder: '#404040',
                inputBorderHover: '#525252',
                inputBorderFocus: '#a78bfa',
                inputText: '#e0e0e0',
                inputPlaceholder: '#737373',
                inputDisabled: '#1a1a1a',

                // Surface colors
                surfaceDefault: '#1e1e1e',
                surfaceHover: '#2a2a2a',
                surfaceActive: '#333333',
                surfaceDisabled: '#171717'
            },
            accessibility: {
                contrastRatio: 4.5,
                wcagLevel: 'AA'
            }
        },

        night: {
            name: 'night',
            displayName: 'Night Theme',
            colors: {
                // Core colors - deeper blacks with blue tint
                bodyBackground: '#0a0e1a',
                bodyText: '#d4d9e8',

                // Panel colors - dark blue-gray
                panelBackground: '#151b2e',
                panelShadow: 'rgba(0, 0, 0, 0.7)',
                panelText: '#d4d9e8',
                panelBorder: 'rgba(100, 120, 180, 0.15)',

                // Header colors - midnight blue
                headerBackground: 'rgba(10, 14, 26, 0.95)',
                headerBackgroundScrolled: 'rgba(15, 20, 35, 0.98)',
                headerShadow: 'rgba(0, 0, 0, 0.7)',

                // Interactive colors - cool blue-purple
                linkColor: '#7c9fff',
                linkHover: '#a5b8ff',
                buttonBackground: '#7c9fff',
                buttonText: '#ffffff',
                buttonHover: '#6a8eef',
                buttonActive: '#587ddf',

                // Semantic accent colors
                primary: '#7c9fff',
                primaryHover: '#6a8eef',
                primaryActive: '#587ddf',
                primaryDisabled: '#2a3d5f',

                secondary: '#a5b8ff',
                secondaryHover: '#93a6ef',
                secondaryActive: '#8194df',
                secondaryDisabled: '#3a4a6f',

                accent: '#6eb5ff',
                accentHover: '#5ca3ef',
                accentActive: '#4a91df',
                accentDisabled: '#2a4a6f',

                // State colors - adjusted for dark background
                success: '#4ade80',
                successHover: '#22c55e',
                successActive: '#16a34a',
                successDisabled: '#1e4d2f',

                warning: '#fcd34d',
                warningHover: '#fbbf24',
                warningActive: '#f59e0b',
                warningDisabled: '#6b5310',

                error: '#fb7185',
                errorHover: '#f43f5e',
                errorActive: '#e11d48',
                errorDisabled: '#6b2633',

                info: '#7dd3fc',
                infoHover: '#38bdf8',
                infoActive: '#0ea5e9',
                infoDisabled: '#1e3d5f',

                // Input and form states
                inputBackground: '#1a2035',
                inputBorder: '#2a3550',
                inputBorderHover: '#3a4560',
                inputBorderFocus: '#7c9fff',
                inputText: '#d4d9e8',
                inputPlaceholder: '#6b7a95',
                inputDisabled: '#0f1420',

                // Surface colors
                surfaceDefault: '#151b2e',
                surfaceHover: '#1a2035',
                surfaceActive: '#1f2540',
                surfaceDisabled: '#0f1420'
            },
            accessibility: {
                contrastRatio: 4.5,
                wcagLevel: 'AA'
            }
        },

        bright: {
            name: 'bright',
            displayName: 'Bright Theme',
            colors: {
                // Core colors - pure white with high contrast
                bodyBackground: '#ffffff',
                bodyText: '#1a1a1a',

                // Panel colors - subtle off-white
                panelBackground: '#fafafa',
                panelShadow: 'rgba(0, 0, 0, 0.08)',
                panelText: '#1a1a1a',
                panelBorder: 'rgba(0, 0, 0, 0.08)',

                // Header colors - vibrant gradient
                headerBackground: 'rgba(255, 240, 245, 0.9)',
                headerBackgroundScrolled: 'rgba(240, 248, 255, 0.95)',
                headerShadow: 'rgba(0, 0, 0, 0.08)',

                // Interactive colors - vibrant purple-pink
                linkColor: '#8b5cf6',
                linkHover: '#a855f7',
                buttonBackground: '#8b5cf6',
                buttonText: '#ffffff',
                buttonHover: '#7c3aed',
                buttonActive: '#6d28d9',

                // Semantic accent colors
                primary: '#8b5cf6',
                primaryHover: '#7c3aed',
                primaryActive: '#6d28d9',
                primaryDisabled: '#ddd6fe',

                secondary: '#a855f7',
                secondaryHover: '#9333ea',
                secondaryActive: '#7e22ce',
                secondaryDisabled: '#e9d5ff',

                accent: '#ec4899',
                accentHover: '#db2777',
                accentActive: '#be185d',
                accentDisabled: '#fce7f3',

                // State colors - vibrant and saturated
                success: '#22c55e',
                successHover: '#16a34a',
                successActive: '#15803d',
                successDisabled: '#bbf7d0',

                warning: '#f59e0b',
                warningHover: '#d97706',
                warningActive: '#b45309',
                warningDisabled: '#fde68a',

                error: '#ef4444',
                errorHover: '#dc2626',
                errorActive: '#b91c1c',
                errorDisabled: '#fecaca',

                info: '#3b82f6',
                infoHover: '#2563eb',
                infoActive: '#1d4ed8',
                infoDisabled: '#bfdbfe',

                // Input and form states
                inputBackground: '#ffffff',
                inputBorder: '#d1d5db',
                inputBorderHover: '#9ca3af',
                inputBorderFocus: '#8b5cf6',
                inputText: '#1a1a1a',
                inputPlaceholder: '#9ca3af',
                inputDisabled: '#f3f4f6',

                // Surface colors
                surfaceDefault: '#ffffff',
                surfaceHover: '#f9fafb',
                surfaceActive: '#f3f4f6',
                surfaceDisabled: '#e5e7eb'
            },
            accessibility: {
                contrastRatio: 4.5,
                wcagLevel: 'AA'
            }
        }
    },

    // === Legacy theme property for backward compatibility ===
    theme: 'day', // Deprecated: Use LightTheme and DarkTheme instead

    HeadImg: '/assets/head.png',//头像图片的URL
    Name: 'iiishop',//作者名称
    Description: 'A social network for finding love and making friends',//作者描述
    PostsPerPage: 5,//每页显示的文章数量
    ChangeInfoAndTipPosition: false,//是否调换Info和Tip的位置
    InfoListUp: [
        'SelfIntroductionPanel',
        'CollectionPanel',
    ],//Info列表，在页面默认添加的InfoList的上面出现
    InfoListDown: [
        'ClockPanel',
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