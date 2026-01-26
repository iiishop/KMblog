import { createRouter, createWebHashHistory } from 'vue-router';
import globalVar from '@/globalVar';

const Home = () => import('../views/Home.vue');
const TagPage = () => import('../views/TagPage.vue');
const PostPage = () => import('../views/PostPage.vue');
const ArchivePage = () => import('../views/ArchivePage.vue');
const CategoryPage = () => import('../views/CategoryPage.vue');
const AboutPage = () => import('../views/AboutPage.vue');

const getMarkdownUrls = (categoryPath) => {
    console.log('categoryPath', categoryPath);
    const categories = globalVar.categories;
    const pathArray = Array.isArray(categoryPath) ? categoryPath : categoryPath.split('/');
    let currentCategory = categories;
    let markdownUrls = [];
    //取出pathArray的最后一个元素
    const lastPart = pathArray.pop();

    // 找到指定路径的目录
    for (const part of pathArray) {
        if (currentCategory[part]) {
            currentCategory = currentCategory[part].childCategories;
        }
    }
    currentCategory = currentCategory[lastPart];

    markdownUrls = markdownUrls.concat(currentCategory.files);
    // 写一个递归获取子目录中的markdown文件的方法
    const getMarkdownUrlsFromChildCategories = (childCategories) => {
        let md = []
        for (const [node, childCategory] of Object.entries(childCategories)) {
            md = md.concat(childCategory.files);
            if (childCategory.childCategories) {
                md = md.concat(getMarkdownUrlsFromChildCategories(childCategory.childCategories));
            }
        }
        return md;
    }
    // 如果有子目录，则递归获取子目录中的markdown文件
    if (currentCategory.childCategories) {
        markdownUrls = markdownUrls.concat(getMarkdownUrlsFromChildCategories(currentCategory.childCategories));
    }

    return markdownUrls;
};

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home
    },
    {
        path: '/tags',
        name: 'TagPage',
        component: TagPage
    },
    {
        path: '/posts/:collection?/:mdName',
        name: 'PostPage',
        component: PostPage,
        props: route => {
            const { collection, mdName } = route.params;
            let markdownUrl = '';
            if (collection) {
                markdownUrl = `/Posts/${collection}/${mdName}.md`;
            } else {
                markdownUrl = `/Posts/Markdowns/${mdName}.md`;
            }
            return { markdownUrl: markdownUrl };
        }
    },
    {
        path: '/archive',
        name: 'ArchivePage',
        component: ArchivePage,
        props: route => {
            const markdownUrls = globalVar.markdowns ? Object.keys(globalVar.markdowns) : [];
            return { markdownUrls };
        }
    },
    {
        path: '/archive/tags/:tagName',
        name: 'ArchivePageByTag',
        component: ArchivePage,
        props: route => {
            const { tagName } = route.params;
            const markdownUrls = globalVar.tags[tagName] || [];
            return { markdownUrls };
        }
    },
    {
        path: '/archive/categories/:categoryPath(.*)*',
        name: 'ArchivePageByCategory',
        component: ArchivePage,
        props: route => {
            const { categoryPath } = route.params;
            const markdownUrls = getMarkdownUrls(categoryPath);
            return { markdownUrls };
        }
    },
    {
        path: '/about',
        name: 'AboutPage',
        component: AboutPage
    },
    {
        path: '/category/:pathMatch(.*)*',
        name: 'CategoryPage',
        component: CategoryPage,
        props: route => {
            const { pathMatch } = route.params;
            const categoryPath = Array.isArray(pathMatch) ? pathMatch : pathMatch ? pathMatch.split('/') : [];
            return { categoryPath };
        }
    }
];

// Add editor route only in development environment
if (import.meta.env.DEV) {
    routes.push({
        path: '/editor',
        name: 'Editor',
        component: () => import('../views/EditorPage.vue')
    });
}

const router = createRouter({
    history: createWebHashHistory(),
    routes
});

export default router;