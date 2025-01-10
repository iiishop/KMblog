import { createRouter, createWebHashHistory } from 'vue-router';

const Home = () => import('../views/Home.vue');
// const BlogPost = () => import('../views/BlogPost.vue');

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home
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