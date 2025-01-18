import { createRouter, createWebHashHistory } from 'vue-router';
import globalVar from '@/globalVar';

const Home = () => import('../views/Home.vue');
const TagPage = () => import('../views/TagPage.vue');
const PostPage = () => import('../views/PostPage.vue');
const ArchivePage = () => import('../views/ArchivePage.vue');

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
                markdownUrl = `/src/Posts/${collection}/${mdName}.md`;
            } else {
                markdownUrl = `/src/Posts/Markdowns/${mdName}.md`;
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
    }
];

const router = createRouter({
    history: createWebHashHistory(),
    routes
});

export default router;