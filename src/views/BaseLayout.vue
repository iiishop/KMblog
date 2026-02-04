<template>
    <div>
        <!-- 全局背景遮挡层 - 在BaseLayout区域显示 -->
        <div class="baselayout-background-overlay"></div>

        <HeadMenu />
        <div class="Scene">
            <!-- 桌面端：左侧切换按钮 -->
            <button v-if="showTipList && !isInfoLeftPosition && !isMobile && shouldShowToggleBtn"
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
            <button v-if="showInfoList && isInfoLeftPosition && !isMobile && shouldShowToggleBtn"
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
            <button v-if="showInfoList && !isInfoLeftPosition && !isMobile && shouldShowToggleBtn"
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
            <button v-if="showTipList && isInfoLeftPosition && !isMobile && shouldShowToggleBtn"
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
import { useRoute } from 'vue-router';
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

// 滚动相关状态 - 用于控制toggle-btn显示
const isScrolledPastHero = ref(false);

// 检测是否为首页（有 HeroSection 的页面）
const route = useRoute();
const isHomePage = computed(() => route.name === 'HomePage' || route.path === '/');

// toggle-btn 显示逻辑：首页需要滚动后显示，其他页面立即显示
const shouldShowToggleBtn = computed(() => {
    if (isHomePage.value) {
        return isScrolledPastHero.value;
    }
    return true; // 非首页立即显示
});

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

// 检测是否滚动过Hero区域（只在首页生效）
const checkScrollPosition = () => {
    // 非首页不需要检测
    if (!isHomePage.value) {
        isScrolledPastHero.value = true; // 非首页直接设为 true
        return;
    }

    // Hero区域高度为100vh
    const heroHeight = window.innerHeight;
    isScrolledPastHero.value = window.scrollY > heroHeight * 0.3; // 滚动超过30%后显示
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

    // 桌面端逻辑 - 使用动态计算的侧边栏宽度
    const sidebarWidth = 'var(--sidebar-width)';
    const sidebarMargin = '4rem'; // 2rem * 2 (左右边距)

    // 检查左右侧边栏的显示状态
    const hasLeftSidebar = (isInfoLeftPosition && props.showInfoList && !isInfoListHidden.value) ||
        (!isInfoLeftPosition && props.showTipList && !isTipListHidden.value);
    const hasRightSidebar = (isInfoLeftPosition && props.showTipList && !isTipListHidden.value) ||
        (!isInfoLeftPosition && props.showInfoList && !isInfoListHidden.value);

    if (!props.showTipList && !props.showInfoList) {
        // 没有任何侧边栏：左右各留 2rem 间隔
        return {
            minWidth: 'calc(100% - 4rem)',
            maxWidth: 'calc(100% - 4rem)',
            margin: '0 2rem'
        };
    } else if (!hasLeftSidebar && !hasRightSidebar) {
        // 侧边栏都被隐藏：左右各留 2rem 间隔
        return {
            minWidth: 'calc(100% - 4rem)',
            maxWidth: 'calc(100% - 4rem)',
            margin: '0 2rem'
        };
    } else if (hasLeftSidebar && !hasRightSidebar) {
        // 只有左侧边栏：右侧留 2rem 间隔
        return {
            minWidth: `calc(100% - ${sidebarWidth} - ${sidebarMargin} - 2rem)`,
            maxWidth: `calc(100% - ${sidebarWidth} - ${sidebarMargin} - 2rem)`,
            marginRight: '2rem'
        };
    } else if (!hasLeftSidebar && hasRightSidebar) {
        // 只有右侧边栏：左侧留 2rem 间隔
        return {
            minWidth: `calc(100% - ${sidebarWidth} - ${sidebarMargin} - 2rem)`,
            maxWidth: `calc(100% - ${sidebarWidth} - ${sidebarMargin} - 2rem)`,
            marginLeft: '2rem'
        };
    } else {
        // 两个侧边栏都有：保持原有设定
        return {
            minWidth: `calc(100% - ${sidebarWidth} * 2 - ${sidebarMargin} * 2)`,
            maxWidth: `calc(100% - ${sidebarWidth} * 2 - ${sidebarMargin} * 2)`
        };
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
    checkScrollPosition(); // 初始检测
    toggleInfoList();
    toggleInfoList();
    toggleTipList();
    toggleTipList();
    handleFloatListScroll();

    window.addEventListener('scroll', handleFloatListScroll);
    window.addEventListener('scroll', checkScrollPosition); // 添加滚动监听
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
    window.removeEventListener('scroll', checkScrollPosition);
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
    background: transparent;
    color: var(--body-text-color);
}

/* BaseLayout 背景遮挡层 */
.baselayout-background-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: var(--theme-body-bg);
    opacity: var(--background-opacity, 0.5);
    backdrop-filter: blur(var(--background-blur, 20px));
    z-index: -1;
    pointer-events: none;
}

/* 响应式侧边栏宽度 */
:root {
    /* 超宽屏 (≥ 2560px) - 更宽的侧边栏 */
    --sidebar-width: 28rem;
    --sidebar-margin: 4rem;
}

@media (max-width: 2559px) and (min-width: 1920px) {
    :root {
        /* 2K 分辨率 (1920px - 2559px) - 标准侧边栏 */
        --sidebar-width: 25rem;
        --sidebar-margin: 4rem;
    }
}

@media (max-width: 1919px) and (min-width: 1440px) {
    :root {
        /* 1440p 分辨率 (1440px - 1919px) - 稍窄侧边栏 */
        --sidebar-width: 22rem;
        --sidebar-margin: 3rem;
    }
}

@media (max-width: 1439px) and (min-width: 1200px) {
    :root {
        /* 1080p 分辨率 (1200px - 1439px) - 更窄侧边栏 */
        --sidebar-width: 20rem;
        --sidebar-margin: 2rem;
    }
}

@media (max-width: 1199px) and (min-width: 969px) {
    :root {
        /* 小桌面 (969px - 1199px) - 最窄侧边栏 */
        --sidebar-width: 18rem;
        --sidebar-margin: 2rem;
    }
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
    width: var(--sidebar-width);
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
    width: var(--sidebar-width);
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
    left: calc(var(--sidebar-width) + 4rem);
    transition: all 0.5s ease-in-out, top 0s;
}

.left-btn {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    right: calc(var(--sidebar-width) + 4rem);
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

/* 移动端：底部导航栏 - 极致美化版 */
.mobile-bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 70px;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-top: 1px solid rgba(255, 255, 255, 0.3);
    display: flex;
    justify-content: space-around;
    align-items: center;
    z-index: 9999;
    box-shadow:
        0 -8px 32px rgba(0, 0, 0, 0.08),
        0 -2px 8px rgba(0, 0, 0, 0.04),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 0 1rem;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
    .mobile-bottom-nav {
        background: rgba(30, 30, 30, 0.9);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow:
            0 -8px 32px rgba(0, 0, 0, 0.4),
            0 -2px 8px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
}

.mobile-bottom-nav .nav-item {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.3rem;
    padding: 0.6rem 1.8rem;
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    border-radius: 16px;
    min-width: 80px;
    isolation: isolate;
}

/* 导航项背景光晕效果 */
.mobile-bottom-nav .nav-item::before {
    content: '';
    position: absolute;
    inset: -4px;
    background: linear-gradient(135deg,
            var(--theme-primary),
            var(--theme-secondary, #667eea));
    border-radius: 20px;
    opacity: 0;
    filter: blur(12px);
    transition: opacity 0.4s ease;
    z-index: -2;
}

/* 导航项背景 */
.mobile-bottom-nav .nav-item::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg,
            rgba(99, 102, 241, 0.1),
            rgba(102, 126, 234, 0.1));
    border-radius: 16px;
    opacity: 0;
    transition: all 0.3s ease;
    z-index: -1;
}

.mobile-bottom-nav .nav-item svg {
    width: 26px;
    height: 26px;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.mobile-bottom-nav .nav-item span {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: all 0.3s ease;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* Hover 效果 */
.mobile-bottom-nav .nav-item:hover {
    color: var(--theme-primary);
    transform: translateY(-2px);
}

.mobile-bottom-nav .nav-item:hover::after {
    opacity: 1;
}

.mobile-bottom-nav .nav-item:hover svg {
    transform: scale(1.1);
}

/* 按下效果 */
.mobile-bottom-nav .nav-item:active {
    transform: translateY(0) scale(0.95);
}

/* 激活状态 - 极致美化 */
.mobile-bottom-nav .nav-item.active {
    color: #fff;
    background: linear-gradient(135deg,
            var(--theme-primary) 0%,
            var(--theme-secondary, #667eea) 100%);
    box-shadow:
        0 8px 24px rgba(99, 102, 241, 0.35),
        0 4px 12px rgba(99, 102, 241, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.3),
        inset 0 -1px 0 rgba(0, 0, 0, 0.1);
    transform: translateY(-4px) scale(1.05);
}

.mobile-bottom-nav .nav-item.active::before {
    opacity: 0.6;
    animation: pulse 2s ease-in-out infinite;
}

.mobile-bottom-nav .nav-item.active::after {
    opacity: 0;
}

.mobile-bottom-nav .nav-item.active svg {
    stroke: #fff;
    transform: scale(1.15) rotate(5deg);
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.mobile-bottom-nav .nav-item.active span {
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* 激活指示器 */
.mobile-bottom-nav .nav-item.active::before {
    content: '';
    position: absolute;
    top: -3px;
    left: 50%;
    transform: translateX(-50%);
    width: 40px;
    height: 3px;
    background: linear-gradient(90deg,
            transparent,
            rgba(255, 255, 255, 0.8),
            transparent);
    border-radius: 2px;
    box-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
}

/* 脉冲动画 */
@keyframes pulse {

    0%,
    100% {
        opacity: 0.4;
        transform: scale(1);
    }

    50% {
        opacity: 0.8;
        transform: scale(1.05);
    }
}

/* 导航栏入场动画 */
@keyframes navSlideUp {
    from {
        transform: translateY(100%);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.mobile-bottom-nav {
    animation: navSlideUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* 导航项依次入场 */
.mobile-bottom-nav .nav-item:nth-child(1) {
    animation: navItemFadeIn 0.5s ease-out 0.1s both;
}

.mobile-bottom-nav .nav-item:nth-child(2) {
    animation: navItemFadeIn 0.5s ease-out 0.2s both;
}

@keyframes navItemFadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
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
        padding-bottom: 70px;
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
        height: 64px;
        padding: 0 0.5rem;
    }

    .mobile-bottom-nav .nav-item {
        padding: 0.5rem 1.2rem;
        min-width: 70px;
    }

    .mobile-bottom-nav .nav-item svg {
        width: 22px;
        height: 22px;
    }

    .mobile-bottom-nav .nav-item span {
        font-size: 0.65rem;
    }

    .mobile-drawer {
        width: 90%;
        max-width: 100%;
        bottom: 64px;
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