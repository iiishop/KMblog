<script setup>
import { onMounted, ref, computed, defineAsyncComponent } from 'vue';
import { useRouter } from 'vue-router';
import globalVar from '../globalVar.js';

// 使用 Vite 的代码分割功能进行动态导入
const Collection = defineAsyncComponent(() => import('./CollectionPanelComps/Collection.vue'));

const router = useRouter();
const collections = ref({});

// 显示前4个collection（第4个会有渐隐效果）
const displayedCollections = computed(() => {
    const entries = Object.entries(collections.value);
    return entries.slice(0, 4).reduce((obj, [key, value]) => {
        obj[key] = value;
        return obj;
    }, {});
});

// 是否有更多内容
const hasMore = computed(() => Object.keys(collections.value).length > 3);

// 跳转到CollectionsPage
const goToCollections = () => {
    router.push('/collections');
};

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
                <div v-for="(collection, name, index) in displayedCollections" :key="name" class="collection-wrapper"
                    :class="{ 'last-item': index === 3 && hasMore }" :style="{ '--i': index }">
                    <Collection :name="name" :imageUrl="collection.image" :createDate="collection.date"
                        :count="collection.count" />
                </div>
            </TransitionGroup>

            <!-- 渐隐遮罩和查看全部按钮 -->
            <div v-if="hasMore" class="view-more-overlay" @click="goToCollections">
                <div class="fade-gradient"></div>
                <div class="view-more-content">
                    <span class="view-more-text">查看全部</span>
                    <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M5 12h14M12 5l7 7-7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                            stroke-linejoin="round" />
                    </svg>
                </div>
            </div>
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
    transition: transform 0.3s ease, box-shadow 0.3s ease, var(--theme-transition-colors);
    border: 1px solid var(--theme-border-light);
    backdrop-filter: blur(10px);
}

.CollectionPanel:hover {
    box-shadow: 0 20px 40px -12px var(--collectionpanel-shadow-color);
    border-color: var(--theme-border-medium);
}

.panel-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--theme-border-light);
    margin-bottom: 0.5rem;
    transition: var(--theme-transition-colors);
}

.icon-wrapper {
    background: var(--theme-gradient);
    padding: 10px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px var(--theme-primary);
}

.header-icon {
    width: 24px;
    height: 24px;
    color: var(--theme-button-text);
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
    background: var(--theme-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    transition: var(--theme-transition-colors);
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
    position: relative;
}

.collection-wrapper {
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* 最后一个条目（第4个）的样式 */
.collection-wrapper.last-item {
    position: relative;
    overflow: hidden;
    max-height: 150px;
    /* 只显示一半高度 */
}

/* 渐隐遮罩和查看全部按钮 */
.view-more-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 200px;
    cursor: pointer;
    z-index: 10;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 1.5rem;
    transition: all 0.3s ease;
}

.fade-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom,
            transparent 0%,
            color-mix(in srgb, var(--collectionpanel-background-color) 30%, transparent) 30%,
            color-mix(in srgb, var(--collectionpanel-background-color) 70%, transparent) 50%,
            var(--collectionpanel-background-color) 80%);
    backdrop-filter: blur(0px);
    transition: backdrop-filter 0.3s ease, background 0.3s ease;
    pointer-events: none;
}

.view-more-overlay:hover .fade-gradient {
    backdrop-filter: blur(2px);
}

.view-more-content {
    position: relative;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 1rem 2rem;
    background: var(--theme-gradient);
    color: var(--theme-button-text);
    border-radius: 50px;
    font-size: 1rem;
    font-weight: 700;
    box-shadow: 0 8px 24px var(--theme-shadow-lg);
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    z-index: 11;
}

.view-more-overlay:hover .view-more-content {
    transform: translateY(-5px) scale(1.05);
    box-shadow: 0 12px 32px var(--theme-shadow-xl);
}

.view-more-text {
    font-size: 1.1rem;
    letter-spacing: 0.5px;
}

.arrow-icon {
    width: 20px;
    height: 20px;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.view-more-overlay:hover .arrow-icon {
    transform: translateX(5px);
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