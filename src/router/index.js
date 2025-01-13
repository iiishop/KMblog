import { createRouter, createWebHashHistory } from 'vue-router';

const Home = () => import('../views/Home.vue');
const TagPage = () => import('../views/TagPage.vue');
const PostPage = () => import('../views/PostPage.vue');
// const BlogPost = () => import('../views/BlogPost.vue');

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
        path: '/mdtest',
        name: 'mdtest',
        component: PostPage
    },
    // {
    //   path: '/post/:id',
    //   name: 'BlogPost',
    //   component: BlogPost,
    //   props: true
    // }
];

const router = createRouter({
    history: createWebHashHistory(),
    routes
});

export default router;