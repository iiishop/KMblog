import './assets/main.css'

import { loadMarkdownLinks, loadTags, loadCategories, loadCollections } from "./utils";
import globalVar from './globalVar';
import { createApp } from 'vue'
import App from './App.vue'
import router from './router';
import config from './config';

const app = createApp(App);

async function initGlobalVars() {
  globalVar.markdowns = await loadMarkdownLinks();
  globalVar.tags = await loadTags();
  globalVar.categories = await loadCategories();
  globalVar.collections = await loadCollections();

  console.log(globalVar);
}

// 设置全局背景样式
const backgroundStyle = document.createElement('style');
backgroundStyle.innerHTML = `
  body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url(${config.BackgroundImg});
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    z-index: -2;
  }
  body::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    /* 修改后的代码 */
    background: color-mix(in srgb, var(--theme-body-bg), transparent 30%);
    backdrop-filter: blur(${config.BackgroundImgBlur}px);
    z-index: -1;
    transition: background var(--theme-transition-duration) var(--theme-transition-easing),
                opacity var(--theme-transition-duration) var(--theme-transition-easing);
  }
`;
document.head.appendChild(backgroundStyle);

initGlobalVars().then(() => {
  app.use(router).mount('#app');
});