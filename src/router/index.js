import { createRouter, createWebHashHistory } from 'vue-router';

const Home = () => import('../views/Home.vue');
const TagPage = () => import('../views/TagPage.vue');
const PostPage = () => import('../views/PostPage.vue');

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
    }
];

const router = createRouter({
    history: createWebHashHistory(),
    routes
});

export default router;