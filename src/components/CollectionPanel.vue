<script setup>
import { onMounted, ref, defineAsyncComponent } from 'vue';
import globalVar from '../globalVar.js';

// 使用 Vite 的代码分割功能进行动态导入
const Collection = defineAsyncComponent(() => import('./CollectionPanelComps/Collection.vue'));

const collections = ref({});
onMounted(() => {
    collections.value = globalVar.collections;
});
</script>
<template>
    <div class="CollectionPanel">
        <div class="panel-header">
            <div class="icon-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="header-icon">
                    <path
                        d="M11.25 4.533A9.707 9.707 0 0 0 6 3a9.735 9.735 0 0 0-3.25.555.75.75 0 0 0-.5.707v14.25a.75.75 0 0 0 1 .707A8.237 8.237 0 0 1 6 18.75c1.995 0 3.823.707 5.25 1.886V4.533ZM12.75 20.636A8.214 8.214 0 0 1 18 18.75c.966 0 1.89.166 2.75.47v-14.25a.75.75 0 0 0-1-.708A9.735 9.735 0 0 0 18 3a9.707 9.707 0 0 0-5.25 1.533v16.103Z" />
                </svg>
            </div>
            <div class="header-text">
                <h1>Collections</h1>
                <span class="subtitle">精选系列与专题</span>
            </div>
        </div>

        <div class="collection-list">
            <TransitionGroup name="list" appear>
                <div v-for="(collection, name, index) in collections" :key="name" class="collection-wrapper"
                    :style="{ '--i': index }">
                    <Collection :name="name" :imageUrl="collection.image" :createDate="collection.date"
                        :count="collection.count" />
                </div>
            </TransitionGroup>
        </div>
    </div>
</template>
<style scoped>
.CollectionPanel {
    display: flex;
    flex-direction: column;
    background: var(--collectionpanel-background-color);
    padding: 1.5rem;
    width: 100%;
    border-radius: 20px;
    box-shadow: 0 10px 30px -10px var(--collectionpanel-shadow-color);
    height: auto;
    gap: 1.5rem;
    color: var(--collectionpanel-text-color);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
}

.CollectionPanel:hover {
    box-shadow: 0 20px 40px -12px var(--collectionpanel-shadow-color);
    border-color: rgba(255, 255, 255, 0.1);
}

.panel-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid rgba(128, 128, 128, 0.1);
    margin-bottom: 0.5rem;
}

.icon-wrapper {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    padding: 10px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
}

.header-icon {
    width: 24px;
    height: 24px;
    color: white;
}

.header-text {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

h1 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
    background: linear-gradient(to right, var(--collectionpanel-text-color), var(--text-color-light, #888));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.subtitle {
    font-size: 0.85rem;
    opacity: 0.7;
    font-weight: 500;
    letter-spacing: 0.5px;
}

.collection-list {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
}

.collection-wrapper {
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* List Transitions */
.list-enter-active,
.list-leave-active {
    transition: all 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.list-enter-from {
    opacity: 0;
    transform: translateY(20px);
}

/* Staggered Delay Simulation using :nth-child if CSS vars not supported, but here we use var(--i) */
.list-enter-active {
    transition-delay: calc(var(--i) * 0.1s);
}

@media (max-width: 600px) {
    .CollectionPanel {
        padding: 1rem;
    }
}
</style>