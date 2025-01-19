const config = {
    ProjectUrl: 'https://localhost:5173',//博客的基础URL
    BlogName: 'iiishop的博客',//博客名称
    ShortDesc: "XXXXDESC",//博客的简短描述
    BackgroundImg: '/src/assets/background.png',//博客背景图片的URL
    BackgroundImgOpacity: 0.5,//覆盖在背景图片上的白色层的透明度
    BackgroundImgBlur: 20,//覆盖在背景图片上的白色层的模糊度
    theme: "day",//主题，可以是day，其他的待续
    HeadImg: '/src/assets/head.png',//头像图片的URL
    Name: 'iiishop',//作者名称
    Description: 'A social network for finding love and making friends',//作者描述
    PostsPerPage: 10,//每页显示的文章数量
    ChangeInfoAndTipPosition: false,//是否调换Info和Tip的位置
    InfoListUp: [
        'SelfIntroductionPanel',
        'CollectionPanel',
    ],//Info列表，在页面默认添加的InfoList的上面出现
    InfoListDown: [
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

    // Social Links. Maximum 10， 社交链接，最多10个
    Links: [
        {
            name: 'GitHub',
            url: 'https://github.com/',
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