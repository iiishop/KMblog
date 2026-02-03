/**
 * Hero Section 示例配置
 * 
 * 将以下配置复制到 src/config.js 中使用
 */

// 示例 1: 简约风格
const heroConfig1 = {
    HeroBackgroundImg: '/assets/background.png',
    HeroTitle: 'Hello World',
    HeroSubtitles: ['Coding with passion'],
    HeroPanels: []
};

// 示例 2: 多行打字机效果
const heroConfig2 = {
    HeroBackgroundImg: '/assets/background.png',
    HeroTitle: '代码改变世界',
    HeroSubtitles: [
        '写优雅的代码',
        '创造有价值的产品',
        '享受编程的乐趣'
    ],
    HeroPanels: ['CategoryPanel', 'TagPanel']
};

// 示例 3: 完整配置
const heroConfig3 = {
    HeroBackgroundImg: '/assets/hero-background.jpg',
    HeroTitle: 'iiishop的博客',
    HeroSubtitles: [
        '探索技术的边界',
        '记录成长的足迹',
        '分享知识的力量',
        '构建美好的未来'
    ],
    HeroPanels: [
        'CategoryPanel',
        'TagPanel',
        'ClockPanel'
    ]
};

// 示例 4: 个人品牌
const heroConfig4 = {
    HeroBackgroundImg: '/assets/personal-bg.jpg',
    HeroTitle: 'Your Name',
    HeroSubtitles: [
        'Full Stack Developer',
        'Open Source Contributor',
        'Tech Blogger'
    ],
    HeroPanels: ['SelfIntroductionPanel', 'CollectionPanel']
};

export { heroConfig1, heroConfig2, heroConfig3, heroConfig4 };
