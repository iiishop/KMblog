import './assets/main.css'

import { loadMarkdownLinks, loadTags, loadCategories } from "./utils";
import globalVar from './globalVar';
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App);

async function initGlobalVars() {
    globalVar.markdowns = await loadMarkdownLinks();
    globalVar.tags = await loadTags();
    globalVar.categories = await loadCategories();

    console.log(globalVar);
}

initGlobalVars().then(() => {
    app.mount('#app');
})