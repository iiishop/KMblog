<template>
    <div>
        <HeadMenu />
        <div class="Scene">
            <!-- 桌面端：左侧切换按钮 -->
            <button v-if="showTipList && !isInfoLeftPosition && !isMobile"
                :class="['toggle-btn', 'right-btn', { hidden: isTipListHidden }]" @click="toggleTipList">→</button>
            <div v-if="showTipList && !isInfoLeftPosition && !isMobile"
                :class="['TipList', 'LeftList', { hidden: isTipListHidden }]" ref="tipListRef">
                <div class="context">
                    <component v-for="(componentName, index) in tipListUpComponents" :is="componentName" :key="index" />
                    <slot name="tip"></slot>
                    <component v-for="(componentName, index) in tipListDownComponents" :is="componentName"
                        :key="index" />
                </div>
                <div class="FloatList" :class="{ 'float-fixed': isTipFloatFixed }"
                    :style="isTipFloatFixed ? { top: tipFloatTop + 'px', left: tipFloatLeft + 'px' } : {}">
                    <div class="float-list">
                        <component v-for="(componentName, index) in tipListFloatComponents" :is="componentName"
                            :key="index" />
                        <slot name="float-tip"></slot>
                    </div>
                </div>
            </div>
            <button v-if="showInfoList && isInfoLeftPosition && !isMobile"
                :class="['toggle-btn', 'right-btn', { hidden: isInfoListHidden }]" @click="toggleInfoList">→</button>
            <div v-if="showInfoList && isInfoLeftPosition && !isMobile"
                :class="['InfoList', 'LeftList', { hidden: isInfoListHidden }]" ref="infoListRef">
                <div class="context">
                    <component v-for="(componentName, index) in infoListUpComponents" :is="componentName"
                        :key="index" />
                    <slot name="info"></slot>
                    <component v-for="(componentName, index) in infoListDownComponents" :is="componentName"
                        :key="index" />
                </div>
                <div class="FloatList" :class="{ 'float-fixed': isInfoFloatFixed }"
                    :style="isInfoFloatFixed ? { top: infoFloatTop + 'px', left: infoFloatLeft + 'px' } : {}">
                    <div class="float-list">
                        <component v-for="(componentName, index) in infoListFloatComponents" :is="componentName"
                            :key="index" />
                        <slot name="float-info"></slot>
                    </div>
                </div>
            </div>

            <!-- 主内容区 -->
            <div class="MainList" :style="mainListStyle">
                <component v-for="(componentName, index) in mainListUpComponents" :is="componentName" :key="index" />
                <slot name="main"></slot>
                <component v-for="(componentName, index) in mainListDownComponents" :is="componentName" :key="index" />
            </div>

            <!-- 桌面端：右侧切换按钮 -->
            <button v-if="showInfoList && !isInfoLeftPosition && !isMobile"
                :class="['toggle-btn', 'left-btn', { hidden: isInfoListHidden }]" @click="toggleInfoList">→</button>
            <div v-if="showInfoList && !isInfoLeftPosition && !isMobile"
                :class="['InfoList', 'RightList', { hidden: isInfoListHidden }]" ref="infoListRef">
                <div class="context">
                    <component v-for="(componentName, index) in infoListUpComponents" :is="componentName"
                        :key="index" />
                    <slot name="info"></slot>
                    <component v-for="(componentName, index) in infoListDownComponents" :is="componentName"
                        :key="index" />
                </div>
                <div class="FloatList" :class="{ 'float-fixed': isInfoFloatFixed }"
                    :style="isInfoFloatFixed ? { top: infoFloatTop + 'px', left: infoFloatLeft + 'px' } : {}">
                    <div class="float-list">
                        <component v-for="(componentName, index) in infoListFloatComponents" :is="componentName"
                            :key="index" />
                        <slot name="float-info"></slot>
                    </div>
                </div>
            </div>
            <button v-if="showTipList && isInfoLeftPosition && !isMobile"
                :class="['toggle-btn', 'left-btn', { hidden: isTipListHidden }]" @click="toggleTipList">→</button>
            <div v-if="showTipList && isInfoLeftPosition && !isMobile"
                :class="['TipList', 'RightList', { hidden: isTipListHidden }]" ref="tipListRef">
                <div class="context">
                    <component v-for="(componentName, index) in tipListUpComponents" :is="componentName" :key="index" />
                    <slot name="tip"></slot>
                    <component v-for="(componentName, index) in tipListDownComponents" :is="componentName"
                        :key="index" />
                </div>
                <div class="FloatList" :class="{ 'float-fixed': isTipFloatFixed }"
                    :style="isTipFloatFixed ? { top: tipFloatTop + 'px', left: tipFloatLeft + 'px' } : {}">
                    <div class="float-list">
                        <component v-for="(componentName, index) in tipListFloatComponents" :is="componentName"
                            :key="index" />
                        <slot name="float-tip"></slot>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 移动端：底部导航栏 -->
    <div v-if="isMobile" class="mobile-bottom-nav">
        <!-- 根据配置决定按钮顺序 -->
        <template v-if="!isInfoLeftPosition">
            <!-- 默认：导航在左，信息在右 -->
            <button class="nav-item" @click="openDrawer('tip')" :class="{ active: activeDrawer === 'tip' }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                    <path d="M2 17l10 5 10-5"></path>
                    <path d="M2 12l10 5 10-5"></path>
                </svg>
                <span>导航</span>
            </button>
            <button class="nav-item" @click="openDrawer('info')" :class="{ active: activeDrawer === 'info' }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <span>信息</span>
            </button>
        </template>
        <template v-else>
            <!-- 交换后：信息在左，导航在右 -->
            <button class="nav-item" @click="openDrawer('info')" :class="{ active: activeDrawer === 'info' }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <span>信息</span>
            </button>
            <button class="nav-item" @click="openDrawer('tip')" :class="{ active: activeDrawer === 'tip' }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                    <path d="M2 17l10 5 10-5"></path>
                    <path d="M2 12l10 5 10-5"></path>
                </svg>
                <span>导航</span>
            </button>
        </template>
    </div>

    <!-- 移动端：抽屉式侧边栏 -->
    <transition name="drawer-backdrop">
        <div v-if="isMobile && isDrawerOpen" class="drawer-backdrop" @click="closeDrawer"></div>
    </transition>
    <transition name="drawer">
        <div v-if="isMobile && isDrawerOpen" class="mobile-drawer" :class="drawerPosition">
            <div class="drawer-header">
                <h3>{{ activeDrawer === 'info' ? '信息面板' : '导航面板' }}</h3>
                <button class="close-btn" @click="closeDrawer">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="drawer-content">
                <template v-if="activeDrawer === 'info'">
                    <component v-for="(componentName, index) in infoListUpComponents" :is="componentName"
                        :key="'info-up-' + index" />
                    <slot name="info"></slot>
                    <component v-for="(componentName, index) in infoListDownComponents" :is="componentName"
                        :key="'info-down-' + index" />
                    <component v-for="(componentName, index) in infoListFloatComponents" :is="componentName"
                        :key="'info-float-' + index" />
                    <slot name="float-info"></slot>
                </template>
                <template v-if="activeDrawer === 'tip'">
                    <component v-for="(componentName, index) in tipListUpComponents" :is="componentName"
                        :key="'tip-up-' + index" />
                    <slot name="tip"></slot>
                    <component v-for="(componentName, index) in tipListDownComponents" :is="componentName"
                        :key="'tip-down-' + index" />
                    <component v-for="(componentName, index) in tipListFloatComponents" :is="componentName"
                        :key="'tip-float-' + index" />
                    <slot name="float-tip"></slot>
                </template>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { ref, shallowRef, computed, onMounted, onUnmounted, defineAsyncComponent } from 'vue';
import config from '@/config';
import { themeManager } from '@/composables/useTheme';

// 使用 Vite 的代码分割功能进行动态导入
const HeadMenu = defineAsyncComponent(() => import('@/components/HeadMenu.vue'));

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

const tipListUpComponents = shallowRef([]);
const tipListDownComponents = shallowRef([]);
const mainListUpComponents = shallowRef([]);
const mainListDownComponents = shallowRef([]);
const infoListUpComponents = shallowRef([]);
const infoListDownComponents = shallowRef([]);
const infoListFloatComponents = shallowRef([]);
const tipListFloatComponents = shallowRef([]);

const isTipListHidden = shallowRef(false);
const isInfoListHidden = shallowRef(false);

const infoListRef = shallowRef(null);
const tipListRef = shallowRef(null);

// 移动端相关状态
const isMobile = ref(false);
const isDrawerOpen = ref(false);
const activeDrawer = ref(''); // 'info' or 'tip'

// 根据配置决定抽屉位置
// 如果 ChangeInfoAndTipPosition 为 false（默认）：info在右，tip在左
// 如果 ChangeInfoAndTipPosition 为 true：info在左，tip在右
const drawerPosition = computed(() => {
    if (isInfoLeftPosition) {
        // 交换了位置：info在左，tip在右
        return activeDrawer.value === 'info' ? 'left' : 'right';
    } else {
        // 默认：info在右，tip在左
        return activeDrawer.value === 'info' ? 'right' : 'left';
    }
});

// 检测屏幕尺寸
const checkMobile = () => {
    isMobile.value = window.innerWidth <= 968;
    // 移动端时关闭抽屉
    if (!isMobile.value) {
        isDrawerOpen.value = false;
        activeDrawer.value = '';
    }
};

// 打开抽屉
const openDrawer = (type) => {
    if (activeDrawer.value === type && isDrawerOpen.value) {
        closeDrawer();
    } else {
        activeDrawer.value = type;
        isDrawerOpen.value = true;
        // 禁止背景滚动
        document.body.style.overflow = 'hidden';
    }
};

// 关闭抽屉
const closeDrawer = () => {
    isDrawerOpen.value = false;
    activeDrawer.value = '';
    // 恢复背景滚动
    document.body.style.overflow = '';
};

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

// FloatList 固定定位状态
const isInfoFloatFixed = ref(false);
const isTipFloatFixed = ref(false);
const infoFloatTop = ref(0);
const tipFloatTop = ref(0);
const infoFloatLeft = ref(0);
const tipFloatLeft = ref(0);

// 处理 FloatList 的滚动固定效果
const handleFloatListScroll = () => {
    if (isMobile.value) return;

    const headerHeight = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--header-height')) || 96;
    const targetTop = headerHeight + 32; // header高度 + 2rem (假设 1rem = 16px)

    // 处理 InfoList 的 FloatList
    if (infoListRef.value) {
        const contextEl = infoListRef.value.querySelector('.context');
        const floatEl = infoListRef.value.querySelector('.FloatList');

        if (contextEl && floatEl) {
            const contextRect = contextEl.getBoundingClientRect();
            const contextBottom = contextRect.bottom;
            const floatRect = floatEl.getBoundingClientRect();

            // 如果 context 底部已经滚动到目标位置以上，固定 FloatList
            if (contextBottom <= targetTop) {
                isInfoFloatFixed.value = true;
                infoFloatTop.value = targetTop;
                infoFloatLeft.value = floatRect.left; // 保持原来的水平位置
            } else {
                isInfoFloatFixed.value = false;
            }
        }
    }

    // 处理 TipList 的 FloatList
    if (tipListRef.value) {
        const contextEl = tipListRef.value.querySelector('.context');
        const floatEl = tipListRef.value.querySelector('.FloatList');

        if (contextEl && floatEl) {
            const contextRect = contextEl.getBoundingClientRect();
            const contextBottom = contextRect.bottom;
            const floatRect = floatEl.getBoundingClientRect();

            // 如果 context 底部已经滚动到目标位置以上，固定 FloatList
            if (contextBottom <= targetTop) {
                isTipFloatFixed.value = true;
                tipFloatTop.value = targetTop;
                tipFloatLeft.value = floatRect.left; // 保持原来的水平位置
            } else {
                isTipFloatFixed.value = false;
            }
        }
    }
};

const mainListStyle = computed(() => {
    // 移动端：全宽
    if (isMobile.value) {
        return {
            minWidth: 'calc(100% - 2rem)',
            maxWidth: 'calc(100% - 2rem)',
            margin: '0 1rem'
        };
    }

    // 桌面端逻辑保持不变
    if (!props.showTipList && !props.showInfoList) {
        return { minWidth: 'calc(100% - 4rem)' };
    } else if (!props.showTipList && props.showInfoList) {
        if (isInfoListHidden.value) {
            return { minWidth: 'calc(100% - 4rem)' };
        } else {
            return { minWidth: 'calc(100% - 33rem)' };
        }
    } else if (props.showTipList && !props.showInfoList) {
        if (isTipListHidden.value) {
            return { minWidth: 'calc(100% - 4rem)' };
        } else {
            return { minWidth: 'calc(100% - 33rem)' };
        }
    } else {
        if (isTipListHidden.value && isInfoListHidden.value) {
            return { minWidth: 'calc(100% - 4rem)' };
        } else if (isTipListHidden.value || isInfoListHidden.value) {
            return { minWidth: 'calc(100% - 33rem)' };
        } else {
            return { minWidth: 'calc(100% - 58rem)' };
        }
    }
});
// 动态更新 header 高度
const updateHeaderHeight = () => {
    const header = document.querySelector('.header-menu');
    if (header) {
        const headerHeight = header.offsetHeight;
        document.documentElement.style.setProperty('--header-height', `${headerHeight + 16}px`);
    }
};

onMounted(async () => {
    // Ensure theme system is initialized before loading components
    if (!themeManager.currentTheme.value) {
        themeManager.initializeTheme();
    }

    await loadComponents(config.TipListUp, tipListUpComponents);
    await loadComponents(config.TipListDown, tipListDownComponents);
    await loadComponents(config.MainListUp, mainListUpComponents);
    await loadComponents(config.MainListDown, mainListDownComponents);
    await loadComponents(config.InfoListUp, infoListUpComponents);
    await loadComponents(config.InfoListDown, infoListDownComponents);
    await loadComponents(config.InfoListFloat, infoListFloatComponents);
    await loadComponents(config.TipListFloat, tipListFloatComponents);

    // 初始化
    checkMobile();
    updateHeaderHeight();
    toggleInfoList();
    toggleInfoList();
    toggleTipList();
    toggleTipList();
    handleFloatListScroll();

    window.addEventListener('scroll', handleFloatListScroll);
    window.addEventListener('resize', () => {
        checkMobile();
        updateHeaderHeight();
        handleFloatListScroll();
    });

    // 监听 header 高度变化
    const headerObserver = new ResizeObserver(() => {
        updateHeaderHeight();
        handleFloatListScroll();
    });
    const header = document.querySelector('.header-menu');
    if (header) {
        headerObserver.observe(header);
    }
});

onUnmounted(() => {
    window.removeEventListener('scroll', handleFloatListScroll);
    window.removeEventListener('resize', checkMobile);
    // 清理
    document.body.style.overflow = '';
});
</script>

<style>
body {
    margin: 0;
    padding: 0;
    font-family: 'Noto Sans SC', sans-serif;
    background: var(--body-background-color);
    color: var(--body-text-color);
    overflow-x: hidden;
    overflow-y: auto;
}

.Scene {
    margin-top: 1rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: row;
    justify-content: center;
    padding-top: var(--header-height, 6rem);
    width: 100%;
    min-height: 100vh;
    transition: all 0.3s ease-in-out;
}

.InfoList,
.TipList {
    height: fit-content;
    width: 25rem;
    color: var(--rightlist-text-color);
    position: relative;
    transition: all 0.3s ease-in-out;
    margin-left: 2rem;
    margin-right: 2rem;
    overflow: visible;
    display: flex;
    flex-direction: column;
    align-self: flex-start;
}

/* 移动端抽屉内的侧边栏需要滚动 */
.mobile-drawer .InfoList,
.mobile-drawer .TipList {
    overflow-y: auto;
    max-height: 100%;
}

/* 侧边栏滚动条样式 */
.InfoList::-webkit-scrollbar,
.TipList::-webkit-scrollbar {
    width: 6px;
}

.InfoList::-webkit-scrollbar-track,
.TipList::-webkit-scrollbar-track {
    background: var(--theme-panel-bg);
    border-radius: 3px;
}

.InfoList::-webkit-scrollbar-thumb,
.TipList::-webkit-scrollbar-thumb {
    background: var(--theme-border-light);
    border-radius: 3px;
}

.InfoList::-webkit-scrollbar-thumb:hover,
.TipList::-webkit-scrollbar-thumb:hover {
    background: var(--theme-content-border);
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
    max-width: calc(100% - 50rem - 8rem);
    min-width: 30rem;
    height: 100%;
    transition: all 0.3s ease-in-out;
}

.FloatList {
    margin-top: 2rem;
    width: 25rem;
    display: flex;
    flex-direction: column;
    position: relative;
    transition: none;
}

.FloatList.float-fixed {
    position: fixed;
    z-index: 100;
}

.InfoList.hidden .FloatList,
.TipList.hidden .FloatList {
    width: 0;
    overflow: hidden;
}

.float-list {
    width: 100%;
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

/* ========================================
   移动端样式
   ======================================== */

/* 移动端：底部导航栏 */
.mobile-bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: var(--theme-content-bg);
    border-top: 1px solid var(--theme-content-border);
    display: flex;
    justify-content: space-around;
    align-items: center;
    z-index: 9999;
    box-shadow: 0 -2px 10px var(--theme-shadow-sm);
    transition: var(--theme-transition-colors);
}

.mobile-bottom-nav .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 0.5rem 1.5rem;
    background: none;
    border: none;
    color: var(--theme-meta-text);
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 8px;
}

.mobile-bottom-nav .nav-item svg {
    width: 24px;
    height: 24px;
    transition: all 0.3s ease;
}

.mobile-bottom-nav .nav-item span {
    font-size: 0.75rem;
    font-weight: 500;
}

.mobile-bottom-nav .nav-item:active {
    transform: scale(0.95);
}

.mobile-bottom-nav .nav-item.active {
    color: var(--theme-primary);
    background: var(--theme-panel-bg);
}

.mobile-bottom-nav .nav-item.active svg {
    stroke: var(--theme-primary);
}

/* 移动端：抽屉背景遮罩 */
.drawer-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 10000;
    backdrop-filter: blur(4px);
}

.drawer-backdrop-enter-active,
.drawer-backdrop-leave-active {
    transition: all 0.3s ease;
}

.drawer-backdrop-enter-from,
.drawer-backdrop-leave-to {
    opacity: 0;
}

/* 移动端：抽屉式侧边栏 */
.mobile-drawer {
    position: fixed;
    top: 0;
    bottom: 60px;
    /* 留出底部导航栏空间 */
    width: 85%;
    max-width: 400px;
    background: var(--theme-content-bg);
    z-index: 10001;
    display: flex;
    flex-direction: column;
    box-shadow: 0 0 20px var(--theme-shadow-lg);
    transition: var(--theme-transition-colors);
}

.mobile-drawer.left {
    left: 0;
    border-right: 1px solid var(--theme-content-border);
}

.mobile-drawer.right {
    right: 0;
    border-left: 1px solid var(--theme-content-border);
}

.drawer-enter-active,
.drawer-leave-active {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-enter-from.left,
.drawer-leave-to.left {
    transform: translateX(-100%);
}

.drawer-enter-from.right,
.drawer-leave-to.right {
    transform: translateX(100%);
}

.drawer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid var(--theme-content-border);
    background: var(--theme-panel-bg);
    transition: var(--theme-transition-colors);
}

.drawer-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--theme-content-text);
}

.drawer-header .close-btn {
    width: 36px;
    height: 36px;
    border: none;
    background: var(--theme-content-bg);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    color: var(--theme-content-text);
}

.drawer-header .close-btn:hover {
    background: var(--theme-border-light);
    transform: rotate(90deg);
}

.drawer-header .close-btn svg {
    width: 20px;
    height: 20px;
}

.drawer-content {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    -webkit-overflow-scrolling: touch;
    /* 启用iOS平滑滚动 */
}

/* 确保抽屉内的组件保持原始高度 */
.drawer-content>* {
    flex-shrink: 0;
    /* 防止内容被压缩 */
}

/* 移动端：滚动条样式 */
.drawer-content::-webkit-scrollbar {
    width: 6px;
}

.drawer-content::-webkit-scrollbar-track {
    background: var(--theme-panel-bg);
}

.drawer-content::-webkit-scrollbar-thumb {
    background: var(--theme-border-light);
    border-radius: 3px;
}

.drawer-content::-webkit-scrollbar-thumb:hover {
    background: var(--theme-content-border);
}

/* ========================================
   响应式设计
   ======================================== */

/* 平板端 (768px - 968px) */
@media (max-width: 968px) and (min-width: 769px) {
    .Scene {
        padding-top: 5rem;
    }

    .InfoList,
    .TipList {
        width: 20rem;
        margin-left: 1rem;
        margin-right: 1rem;
    }

    .MainList {
        min-width: 25rem;
        max-width: calc(100% - 40rem - 4rem);
    }

    .FloatList {
        width: 20rem;
    }

    .right-btn {
        left: 23rem;
    }

    .left-btn {
        right: 23rem;
    }
}

/* 移动端 (≤ 768px) */
@media (max-width: 768px) {
    body {
        padding-bottom: 60px;
        /* 为底部导航栏留出空间 */
    }

    .Scene {
        padding-top: var(--header-height, 4rem);
        padding-bottom: 1rem;
    }

    .MainList {
        min-width: calc(100% - 2rem) !important;
        max-width: calc(100% - 2rem) !important;
        margin: 0 1rem;
        gap: 1.5rem;
    }

    /* 隐藏桌面端的侧边栏和切换按钮 */
    .InfoList,
    .TipList,
    .toggle-btn {
        display: none !important;
    }

    /* 移动端禁用 FloatList 的 sticky 效果 */
    .FloatList {
        position: static;
        top: auto;
    }
}

/* 小屏移动端 (≤ 480px) */
@media (max-width: 480px) {
    .Scene {
        padding-top: var(--header-height, 3.5rem);
    }

    .MainList {
        gap: 1rem;
    }

    .mobile-bottom-nav {
        height: 56px;
    }

    .mobile-bottom-nav .nav-item {
        padding: 0.4rem 1rem;
    }

    .mobile-bottom-nav .nav-item svg {
        width: 20px;
        height: 20px;
    }

    .mobile-bottom-nav .nav-item span {
        font-size: 0.7rem;
    }

    .mobile-drawer {
        width: 90%;
        max-width: 100%;
        bottom: 56px;
    }

    .drawer-header {
        padding: 1rem;
    }

    .drawer-header h3 {
        font-size: 1.1rem;
    }

    .drawer-content {
        padding: 1rem;
        gap: 1rem;
    }

    /* 确保小屏幕上内容也能正常滚动 */
    .drawer-content>* {
        min-height: auto;
    }
}
</style>