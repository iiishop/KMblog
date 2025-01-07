import './assets/main.css'

import { loadMarkdownLinks } from "./utils";
import globalVar from './globalVar';
import { createApp } from 'vue'
import App from './App.vue'

const app = createApp(App);

async function initGlobalVars() {
    globalVar.markdowns = await loadMarkdownLinks();
}

initGlobalVars().then(() => {
    app.mount('#app');
})