import './assets/main.css'

import { loadMarkdownLinks, loadTags } from "./utils";
import globalVar from './globalVar';
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App);

async function initGlobalVars() {
    globalVar.markdowns = await loadMarkdownLinks();
    globalVar.tags = await loadTags();
    
    console.log(globalVar);
}

initGlobalVars().then(() => {
    app.mount('#app');
})