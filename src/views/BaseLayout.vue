<!-- BaseLayout.vue -->
<template>
    <div>
        <HeadMenu />
        <div class="Scene">
            <div v-if="showTipList && !isInfoLeftPosition" class="TipList">
                <component v-for="(componentName, index) in tipListUpComponents" :is="componentName" :key="index" />
                <slot name="tip"></slot>
                <component v-for="(componentName, index) in tipListDownComponents" :is="componentName" :key="index" />
            </div>
            <div v-if="showInfoList && isInfoLeftPosition" class="InfoList">
                <component v-for="(componentName, index) in infoListUpComponents" :is="componentName" :key="index" />
                <slot name="info"></slot>
                <component v-for="(componentName, index) in infoListDownComponents" :is="componentName" :key="index" />
            </div>
            <div class="MainList">
                <component v-for="(componentName, index) in mainListUpComponents" :is="componentName" :key="index" />
                <slot name="main"></slot>
                <component v-for="(componentName, index) in mainListDownComponents" :is="componentName" :key="index" />
            </div>
            <div v-if="showInfoList && !isInfoLeftPosition" class="InfoList">
                <component v-for="(componentName, index) in infoListUpComponents" :is="componentName" :key="index" />
                <slot name="info"></slot>
                <component v-for="(componentName, index) in infoListDownComponents" :is="componentName" :key="index" />
            </div>
            <div v-if="showTipList && isInfoLeftPosition" class="TipList">
                <component v-for="(componentName, index) in tipListUpComponents" :is="componentName" :key="index" />
                <slot name="tip"></slot>
                <component v-for="(componentName, index) in tipListDownComponents" :is="componentName" :key="index" />
            </div>
        </div>
    </div>
</template>

<script setup>
import { defineProps, ref, onMounted } from 'vue';
import HeadMenu from '@/components/HeadMenu.vue';
import config from '@/config';

const props = defineProps({
    showTipList: {
        type: Boolean,
        default: true
    },
    showInfoList: {
        type: Boolean,
        default: true
    }
});

const isInfoLeftPosition = config.ChangeInfoAndTipPosition;

const tipListUpComponents = ref([]);
const tipListDownComponents = ref([]);
const mainListUpComponents = ref([]);
const mainListDownComponents = ref([]);
const infoListUpComponents = ref([]);
const infoListDownComponents = ref([]);

const loadComponents = async (list, components) => {
    for (const componentName of list) {
        try {
            const component = await import(`@/components/${componentName}.vue`);
            components.value.push(component.default);
        } catch (error) {
            console.error(`Failed to load component: ${componentName}`, error);
        }
    }
};

onMounted(async () => {
    await loadComponents(config.TipListUp, tipListUpComponents);
    await loadComponents(config.TipListDown, tipListDownComponents);
    await loadComponents(config.MainListUp, mainListUpComponents);
    await loadComponents(config.MainListDown, mainListDownComponents);
    await loadComponents(config.InfoListUp, infoListUpComponents);
    await loadComponents(config.InfoListDown, infoListDownComponents);
});
</script>

<style>
body {
    margin: 0;
    padding: 0;
    font-family: 'Noto Sans SC', sans-serif;
    background: var(--body-background-color);
    color: var(--body-text-color);
    overflow: auto;
}

.Scene {
    display: flex;
    flex-direction: row;
    justify-content: center;
    gap: 2rem;
    padding: 2rem;
    padding-top: 6rem;
}

.InfoList,
.TipList {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    align-items: center;
    width: 25rem;
    color: var(--rightlist-text-color);
}

.MainList {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    align-items: center;
    max-width: calc(100% - 45rem - 8rem);
    min-width: 30rem;
}
</style>