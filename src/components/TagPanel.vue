<script setup>
import { ref, onMounted, defineAsyncComponent, nextTick } from 'vue';
import { gsap } from 'gsap';
import globalVar from '@/globalVar';

// 使用 Vite 的代码分割功能进行动态导入
const Tag = defineAsyncComponent(() => import('./PostPanelComps/Tag.vue'));

const tags = ref({});

onMounted(async () => {
    tags.value = globalVar.tags

    // Animate Panel Entry
    gsap.from('.TagPanel', {
        y: 30,
        opacity: 0,
        duration: 0.8,
        ease: 'power3.out'
    });

    await nextTick();

    // Staggered Animation for Tags
    gsap.fromTo('.tag-item-wrapper',
        {
            scale: 0.5,
            opacity: 0,
            y: 20
        },
        {
            scale: 1,
            opacity: 1,
            y: 0,
            duration: 0.6,
            stagger: 0.05,
            ease: 'back.out(1.7)',
            delay: 0.2
        }
    );
})
</script>
<template>
    <div class="TagPanel">
        <div class="panel-header">
            <div class="icon-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="header-icon">
                    <path fill-rule="evenodd"
                        d="M5.25 2.25a3 3 0 0 0-3 3v4.318a3 3 0 0 0 .879 2.121l9.58 9.581c.92.92 2.39 1.186 3.548.428a18.849 18.849 0 0 0 5.441-5.44c.758-1.16.492-2.629-.428-3.548l-9.58-9.581a3 3 0 0 0-2.122-.879H5.25ZM6.375 7.5a1.125 1.125 0 1 0 0-2.25 1.125 1.125 0 0 0 0 2.25Z"
                        clip-rule="evenodd" />
                </svg>
            </div>
            <div class="header-text">
                <h1>Tags</h1>
                <span class="subtitle">标签云与索引</span>
            </div>
        </div>

        <div class="TagList">
            <div v-for="(tag, tagname) in tags" :key="tagname" class="tag-item-wrapper">
                <Tag :tagname="tagname" :count="tag.length" />
            </div>
        </div>
    </div>
</template>
<style scoped>
.TagPanel {
    padding: 1.5rem;
    width: 100%;
    border-radius: 24px;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    box-shadow: 0 10px 30px -10px var(--tag-panel-box-shadow);
    background: var(--tag-panel-background-color);
    border: 1px solid var(--theme-border-light);
    backdrop-filter: blur(10px);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease, var(--theme-transition-colors);
}

.TagPanel:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 40px -12px var(--tag-panel-box-shadow);
    border-color: var(--theme-border-medium);
}

.panel-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding-bottom: 0.8rem;
    border-bottom: 2px solid var(--theme-border-light);
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
    width: 22px;
    height: 22px;
    color: var(--theme-button-text);
}

.header-text {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

.TagPanel h1 {
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
    color: var(--tag-panel-text-color);
}

.TagList {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    flex-wrap: wrap;
    gap: 0.8rem;
    width: 100%;
}

.tag-item-wrapper {
    display: inline-flex;
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.tag-item-wrapper:hover {
    transform: scale(1.1) rotate(2deg);
    z-index: 2;
}
</style>