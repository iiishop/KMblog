<template>
    <div>
        <HeadMenu />
        <div class="Scene">
            <div v-if="showTipList && !isInfoLeftPosition" :class="['TipList', { hidden: isTipListHidden }]">
                <button class="toggle-btn right-btn" @click="toggleTipList">→</button>
                <div class="context">
                    <component v-for="(componentName, index) in tipListUpComponents" :is="componentName" :key="index" />
                    <slot name="tip"></slot>
                    <component v-for="(componentName, index) in tipListDownComponents" :is="componentName"
                        :key="index" />

                </div>
            </div>
            <div v-if="showInfoList && isInfoLeftPosition" :class="['InfoList', { hidden: isInfoListHidden }]">
                <button class="toggle-btn right-btn" @click="toggleInfoList">←</button>
                <div class="context">

                    <component v-for="(componentName, index) in infoListUpComponents" :is="componentName"
                        :key="index" />
                    <slot name="info"></slot>
                    <component v-for="(componentName, index) in infoListDownComponents" :is="componentName"
                        :key="index" />
                </div>
            </div>
            <div :class="['MainList', { expanded: isTipListHidden || isInfoListHidden }]">
                <component v-for="(componentName, index) in mainListUpComponents" :is="componentName" :key="index" />
                <slot name="main"></slot>
                <component v-for="(componentName, index) in mainListDownComponents" :is="componentName" :key="index" />
            </div>
            <div v-if="showInfoList && !isInfoLeftPosition" :class="['InfoList', { hidden: isInfoListHidden }]">
                <button class="toggle-btn left-btn" @click="toggleInfoList">→</button>
                <div class="context">

                    <component v-for="(componentName, index) in infoListUpComponents" :is="componentName"
                        :key="index" />
                    <slot name="info"></slot>
                    <component v-for="(componentName, index) in infoListDownComponents" :is="componentName"
                        :key="index" />
                </div>
            </div>
            <div v-if="showTipList && isInfoLeftPosition" :class="['TipList', { hidden: isTipListHidden }]">
                <button class="toggle-btn left-btn" @click="toggleTipList">←</button>
                <div class="context">

                    <component v-for="(componentName, index) in tipListUpComponents" :is="componentName" :key="index" />
                    <slot name="tip"></slot>
                    <component v-for="(componentName, index) in tipListDownComponents" :is="componentName"
                        :key="index" />
                </div>
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

const isTipListHidden = ref(false);
const isInfoListHidden = ref(false);

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

const toggleTipList = () => {
    isTipListHidden.value = !isTipListHidden.value;
};

const toggleInfoList = () => {
    isInfoListHidden.value = !isInfoListHidden.value;
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
    padding-top: 6rem;
    transition: all 0.3s ease-in-out;
}

.InfoList,
.TipList {
    width: 25rem;
    color: var(--rightlist-text-color);
    position: relative;
    transition: all 0.3s ease-in-out;
    margin-left: 2rem;
    margin-right: 2rem;
}

.InfoList.hidden {
    transform: translateX(100%);
    width: 0;
    margin-right: 0;
    margin-left: 0;
}

.TipList.hidden {
    transform: translateX(-100%);
    width: 0;
    margin-right: 0;
    margin-left: 0;
}

.context {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    width: 100%;
    transition: all 0.3s ease-in-out;
}

.TipList.hidden .context {
    width: 0;
    overflow: hidden;
}

.InfoList.hidden .context {
    width: 0;
    overflow: hidden;
}

.MainList {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    align-items: center;
    max-width: calc(100% - 45rem - 8rem);
    min-width: 30rem;
    transition: all 0.3s ease-in-out;
}

.MainList.expanded {
    min-width: calc(100% - 4rem);
}

.toggle-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background-color: #ddd;
    border: none;
    padding: 0.2rem;
    height: 5rem;
    cursor: pointer;
    z-index: 1000;
}
.toggle-btn:hover {
    background-color: #ccc;
}

.right-btn {
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    right: -0.6rem;
    transition: all 0.5s ease-in-out;
}

.left-btn {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
    left: -0.6rem;
    transition: all 0.5s ease-in-out;
}

.InfoList.hidden .right-btn,
.TipList.hidden .right-btn {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
    border-top-right-radius: 0px;
    border-bottom-right-radius: 0px;
    transform: rotate(180deg) translateY(100%);
    right: 0.6rem;
}

.InfoList.hidden .left-btn,
.TipList.hidden .left-btn {
    border-top-left-radius: 0px;
    border-bottom-left-radius: 0px;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    transform: rotate(180deg) translateY(100%);
    left: 0.6rem;
}
</style>