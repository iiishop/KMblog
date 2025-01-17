<template>
    <div>
        <HeadMenu />
        <div class="Scene">
            <button v-if="showTipList && !isInfoLeftPosition" :class="['toggle-btn', 'right-btn', { hidden: isTipListHidden }]" @click="toggleTipList">→</button>
            <div v-if="showTipList && !isInfoLeftPosition" :class="['TipList', 'LeftList', { hidden: isTipListHidden }]"
                ref="tipListRef">
                <div class="context">
                    <component v-for="(componentName, index) in tipListUpComponents" :is="componentName" :key="index" />
                    <slot name="tip"></slot>
                    <component v-for="(componentName, index) in tipListDownComponents" :is="componentName"
                        :key="index" />
                </div>
                <div class="FloatList" :style="{ top: floatListStyle.topTip }">
                    <div class="float-list">
                        <component v-for="(componentName, index) in infoListFloatComponents" :is="componentName"
                            :key="index" />
                    </div>
                </div>
            </div>
            <button v-if="showInfoList && isInfoLeftPosition" :class="['toggle-btn', 'right-btn', { hidden: isInfoListHidden }]" @click="toggleInfoList">→</button>
            <div v-if="showInfoList && isInfoLeftPosition" :class="['InfoList', 'LeftList', { hidden: isInfoListHidden }]"
                ref="infoListRef">
                <div class="context">
                    <component v-for="(componentName, index) in infoListUpComponents" :is="componentName"
                        :key="index" />
                    <slot name="info"></slot>
                    <component v-for="(componentName, index) in infoListDownComponents" :is="componentName"
                        :key="index" />
                </div>
                <div class="FloatList" :style="{ top: floatListStyle.topInfo }">
                    <div class="float-list">
                        <component v-for="(componentName, index) in infoListFloatComponents" :is="componentName"
                            :key="index" />
                    </div>
                </div>
            </div>
            <div class="MainList" :style="mainListStyle">
                <component v-for="(componentName, index) in mainListUpComponents" :is="componentName" :key="index" />
                <slot name="main"></slot>
                <component v-for="(componentName, index) in mainListDownComponents" :is="componentName" :key="index" />
            </div>
            <button v-if="showInfoList && !isInfoLeftPosition" :class="['toggle-btn', 'left-btn', { hidden: isInfoListHidden }]" @click="toggleInfoList">→</button>
            <div v-if="showInfoList && !isInfoLeftPosition" :class="['InfoList', 'RightList', { hidden: isInfoListHidden }]"
                ref="infoListRef">
                <div class="context">
                    <component v-for="(componentName, index) in infoListUpComponents" :is="componentName"
                        :key="index" />
                    <slot name="info"></slot>
                    <component v-for="(componentName, index) in infoListDownComponents" :is="componentName"
                        :key="index" />
                </div>
                <div class="FloatList" :style="{ top: floatListStyle.topInfo }">
                    <div class="float-list">
                        <component v-for="(componentName, index) in infoListFloatComponents" :is="componentName"
                            :key="index" />
                    </div>
                </div>
            </div>
            <button v-if="showTipList && isInfoLeftPosition" :class="['toggle-btn', 'left-btn', { hidden: isTipListHidden }]" @click="toggleTipList">→</button>
            <div v-if="showTipList && isInfoLeftPosition" :class="['TipList', 'RightList', { hidden: isTipListHidden }]"
                ref="tipListRef">
                <div class="context">
                    <component v-for="(componentName, index) in tipListUpComponents" :is="componentName" :key="index" />
                    <slot name="tip"></slot>
                    <component v-for="(componentName, index) in tipListDownComponents" :is="componentName"
                        :key="index" />
                </div>
                <div class="FloatList" :style="{ top: floatListStyle.topTip }">
                    <div class="float-list">
                        <component v-for="(componentName, index) in infoListFloatComponents" :is="componentName"
                            :key="index" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { defineProps, ref, computed, onMounted, onUnmounted } from 'vue';
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
const infoListFloatComponents = ref([]);
const tipListFloatComponents = ref([]);

const isTipListHidden = ref(false);
const isInfoListHidden = ref(false);

const infoListRef = ref(null);
const tipListRef = ref(null);

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

const mainListStyle = computed(() => {
    if (!props.showTipList && !props.showInfoList) {
        // Both TipList and InfoList are not shown
        return { minWidth: 'calc(100% - 4rem)' };
    } else if (!props.showTipList && props.showInfoList) {
        // Only InfoList is shown
        if (isInfoListHidden.value) {
            return { minWidth: 'calc(100% - 4rem)' };
        } else {
            return { minWidth: 'calc(100% - 33rem)' }; // 25rem for InfoList + 2rem margin
        }
    } else if (props.showTipList && !props.showInfoList) {
        // Only TipList is shown
        if (isTipListHidden.value) {
            return { minWidth: 'calc(100% - 4rem)' };
        } else {
            return { minWidth: 'calc(100% - 33rem)' }; // 25rem for TipList + 2rem margin
        }
    } else {
        // Both TipList and InfoList are shown
        if (isTipListHidden.value && isInfoListHidden.value) {
            return { minWidth: 'calc(100% - 4rem)' };
        } else if (isTipListHidden.value || isInfoListHidden.value) {
            return { minWidth: 'calc(100% - 33rem)' }; // 25rem for one list + 2rem margin
        } else {
            return { minWidth: 'calc(100% - 58rem)' }; // 25rem for each list + 4rem margin
        }
    }
});

const floatListStyle = ref({
    topInfo: 'calc(100% + 2rem)',
    topTip: 'calc(100% + 2rem)',
});

const updateFloatListPosition = () => {
    const scrollTop = document.documentElement.scrollTop;
    const rootFontSize = parseFloat(getComputedStyle(document.documentElement).fontSize);

    let newTopInfo = 'calc(100% + 2rem)';
    let newTopTip = 'calc(100% + 2rem';
    // 获取 InfoList 和 TipList 的实际高度
    if (infoListRef.value) {
        const infoListHeight = infoListRef.value.offsetHeight;
        newTopInfo = Math.max(4, 6 + (infoListHeight - scrollTop) / rootFontSize) + 'rem';
    }
    if (tipListRef.value) {
        const tipListHeight = tipListRef.value.offsetHeight;
        newTopTip = Math.max(4, 6 + (tipListHeight - scrollTop) / rootFontSize) + 'rem';
    }

    floatListStyle.value.topInfo = newTopInfo;
    floatListStyle.value.topTip = newTopTip;
};


onMounted(async () => {
    await loadComponents(config.TipListUp, tipListUpComponents);
    await loadComponents(config.TipListDown, tipListDownComponents);
    await loadComponents(config.MainListUp, mainListUpComponents);
    await loadComponents(config.MainListDown, mainListDownComponents);
    await loadComponents(config.InfoListUp, infoListUpComponents);
    await loadComponents(config.InfoListDown, infoListDownComponents);
    await loadComponents(config.InfoListFloat, infoListFloatComponents);
    await loadComponents(config.TipListFloat, tipListFloatComponents);
    updateFloatListPosition();

    window.addEventListener('scroll', updateFloatListPosition);
});

onUnmounted(() => {
    window.removeEventListener('scroll', updateFloatListPosition);
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
    width: 100%;
    height: 100%;
    transition: all 0.3s ease-in-out;
}

.InfoList,
.TipList {
    height: 100%;
    width: 25rem;
    color: var(--rightlist-text-color);
    position: relative;
    transition: all 0.3s ease-in-out;
    margin-left: 2rem;
    margin-right: 2rem;
}

.RightList.hidden {
    transform: translateX(100%);
    width: 0;
    margin-right: 0;
    margin-left: 0;
}

.LeftList.hidden {
    transform: translateX(-100%);
    width: 0;
    margin-right: 0;
    margin-left: 0;
}

.context {
    display: flex;
    width: 100%;
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
    max-width: calc(100% - 50rem - 8rem);
    min-width: 30rem;
    height: 100%;
    transition: all 0.3s ease-in-out;
}

.FloatList {
    position: fixed;
    margin-top: 2rem;
    top: calc(100% + 2rem);
    width: 25rem;
    display: flex;
    flex-direction: column;
}

.InfoList.hidden .FloatList,
.TipList.hidden .FloatList {
    width: 0;
    overflow: hidden;
}

.float-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.toggle-btn {
    position: fixed;
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
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    left: 29rem;
    transition: all 0.5s ease-in-out, top 0s;
}

.left-btn {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    right: 29rem;
    transition: all 0.5s ease-in-out, top 0s;
}


.hidden.right-btn {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    transform: rotate(180deg) translateY(100%);
    left: 0rem;
}


.hidden.left-btn {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    transform: rotate(180deg) translateY(100%);
    right: 0rem;
}
</style>