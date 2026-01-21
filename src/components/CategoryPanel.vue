<script setup>
import { computed, onMounted, defineAsyncComponent, nextTick, watch } from 'vue';
import { gsap } from 'gsap';
import globalVar from '@/globalVar';
import { useRouter } from 'vue-router';

// 使用 Vite 的代码分割功能进行动态导入
const CategoryNode = defineAsyncComponent(() => import('./CategoryPanelComps/CategoryNode.vue'));

const props = defineProps({
    categoryPath: {
        type: Array,
        default: () => [],
    }
});

const router = useRouter();

const categories = globalVar.categories;

const buildTree = (categories) => {
    const tree = {};
    const buildNode = (node) => {
        const treeNode = {};
        for (const [childNode, value] of Object.entries(node)) {
            treeNode[childNode] = {
                name: childNode,
                files: value.files || [],
                childCategories: value.childCategories ? buildNode(value.childCategories) : {},
            }
        }
        return treeNode;

    }
    //遍历所有节点
    for (const [node, value] of Object.entries(categories)) {
        tree[node] = {
            name: node,
            files: value.files || [],
            childCategories: value.childCategories ? buildNode(value.childCategories) : {},
        }
    }
    return tree;
};

const categoryTree = computed(() => buildTree(categories));

// 计算当前路径下的所有文件（文章）
const currentFiles = computed(() => {
    // 1. 如果在根目录，寻找没有分类的文章
    if (props.categoryPath.length === 0) {
        return Object.entries(globalVar.markdowns)
            .filter(([path, info]) => !info.categories || info.categories.length === 0)
            .map(([path, info]) => ({ ...info, path }));
    }

    // 2. 如果在分类目录，遍历树找到当前节点，获取其 files 属性
    let pointer = categoryTree.value;
    for (let i = 0; i < props.categoryPath.length; i++) {
        const part = props.categoryPath[i];
        if (pointer[part]) {
            if (i === props.categoryPath.length - 1) {
                // 找到当前分类节点
                const files = pointer[part].files || [];
                // 将文件路径映射为完整的文章对象
                return files.map(filePath => ({
                    ...globalVar.markdowns[filePath],
                    path: filePath
                }));
            }
            // 继续向下遍历
            pointer = pointer[part].childCategories;
        } else {
            // 路径断裂（找不到分类）
            return [];
        }
    }
    return [];
});

const filteredTree = computed(() => {
    if (props.categoryPath.length === 0) {
        return categoryTree.value;
    }
    let current = categoryTree.value;
    for (const part of props.categoryPath) {
        if (current[part]) {
            current = current[part].childCategories;
        } else {
            return {};
        }
    }
    return current;
});

const goBack = () => {
    if (props.categoryPath.length > 0) {
        const newPath = props.categoryPath.slice(0, -1).join('/');
        router.push(`/category/${newPath}`);
    }
};

const getParentPath = () => {
    const currentPath = router.currentRoute.value.path;
    return currentPath.startsWith('/category') ? props.categoryPath.join('/') : `/${props.categoryPath.join('/')}`;
};

// 导航到文章详情页
function navigateToPost(markdownUrl) {
    const urlParts = markdownUrl.split('/').filter(part => part !== '');
    const fileName = urlParts.pop();
    const mdName = fileName.replace('.md', '');

    let collection = null;
    if (urlParts.length > 0) {
        const lastPart = urlParts[urlParts.length - 1];
        if (lastPart.toLowerCase() !== 'posts') {
            collection = lastPart;
        }
    }

    router.push({
        name: 'PostPage',
        params: { collection, mdName }
    });
}

onMounted(async () => {
    // Initial Panel Animation
    gsap.from('.CategoryPanel', {
        duration: 0.8,
        opacity: 0,
        y: 30,
        ease: 'power3.out'
    });

    await nextTick();
    // Removed GSAP specific list animations for files/categories to let Vue CSS transitions handle it
});

watch(() => props.categoryPath, () => {
    // 简单的标题切换动画
    gsap.fromTo('.header-content',
        { y: -5, opacity: 0.5 },
        { y: 0, opacity: 1, duration: 0.3, ease: 'power2.out' }
    );
});
</script>

<template>
    <div class="CategoryPanel">
        <div class="panel-header">
            <div class="header-left">
                <div class="icon-wrapper">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="header-icon">
                        <path
                            d="M19.5 21a3 3 0 0 0 3-3v-4.5a3 3 0 0 0-3-3h-15a3 3 0 0 0-3 3V18a3 3 0 0 0 3 3h15ZM1.5 10.146V6a3 3 0 0 1 3-3h5.379a2.25 2.25 0 0 1 1.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 0 1 3 3v1.146A4.483 4.483 0 0 0 19.5 9h-15a4.483 4.483 0 0 0-3 1.146Z" />
                    </svg>
                </div>
                <div class="header-content">
                    <h2 class="category-title">{{ props.categoryPath.length > 0 ?
                        props.categoryPath[props.categoryPath.length - 1] : 'Categories' }}</h2>
                    <span class="subtitle">{{ props.categoryPath.length > 0 ? '子目录浏览' : '知识分类索引' }}</span>
                </div>
            </div>

            <button @click="goBack" :disabled="props.categoryPath.length === 0" class="back-button"
                v-if="props.categoryPath.length > 0" title="返回上一级">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="back-icon">
                    <path fill-rule="evenodd"
                        d="M9.53 2.47a.75.75 0 0 1 0 1.06L4.81 8.25H15a6.75 6.75 0 0 1 0 13.5h-3a.75.75 0 0 1 0-1.5h3a5.25 5.25 0 1 0 0-10.5H4.81l4.72 4.72a.75.75 0 1 1-1.06 1.06l-6-6a.75.75 0 0 1 0-1.06l6-6a.75.75 0 0 1 1.06 0Z"
                        clip-rule="evenodd" />
                </svg>
            </button>
        </div>

        <div class="tree-container">
            <!-- Sub-Categories List -->
            <transition-group name="list" tag="ul" class="category-ul" appear>
                <!-- Using index as part of key if name isn't unique, but usually category names are unique at level -->
                <CategoryNode v-for="(node, name, index) in filteredTree" :key="name" :name="name" :node="node"
                    :parentPath="getParentPath()" class="category-list-enter"
                    :style="{ '--delay': index * 0.05 + 's' }" />
            </transition-group>

            <!-- Files List -->
            <transition-group name="list" tag="ul" class="file-ul" appear>
                <li v-for="(file, index) in currentFiles" :key="file.path" class="file-item-wrapper file-list-enter"
                    :style="{ '--delay': (Object.keys(filteredTree).length * 0.05 + index * 0.05) + 's' }">
                    <div class="file-node" @click="navigateToPost(file.path)">
                        <div class="node-content">
                            <!-- Document Icon -->
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"
                                class="file-icon">
                                <path fill-rule="evenodd"
                                    d="M5.625 1.5c-1.036 0-1.875.84-1.875 1.875v17.25c0 1.035.84 1.875 1.875 1.875h12.75c1.035 0 1.875-.84 1.875-1.875V12.75A3.75 3.75 0 0 0 16.5 9h-1.875a1.875 1.875 0 0 1-1.875-1.875V5.25A3.75 3.75 0 0 0 9 1.5H5.625ZM7.5 15a.75.75 0 0 1 .75-.75h7.5a.75.75 0 0 1 0 1.5h-7.5A.75.75 0 0 1 7.5 15Zm.75 2.25a.75.75 0 0 0 0 1.5H12a.75.75 0 0 0 0-1.5H8.25Z"
                                    clip-rule="evenodd" />
                                <path
                                    d="M12.971 1.816A5.23 5.23 0 0 1 14.25 5.25v1.875c0 .207.168.375.375.375H16.5a5.23 5.23 0 0 1 3.434 1.279 9.768 9.768 0 0 0-6.963-6.963Z" />
                            </svg>
                            <span class="file-name">{{ file.title || 'Untitled' }}</span>
                        </div>
                        <span class="file-date">{{ file.date }}</span>
                    </div>
                </li>
            </transition-group>

            <transition name="fade">
                <div v-if="Object.keys(filteredTree).length === 0 && currentFiles.length === 0" class="empty-state">
                    <span>此目录下暂无内容</span>
                </div>
            </transition>
        </div>
    </div>
</template>

<style scoped>
/* Previous Styles Remain */
.CategoryPanel {
    display: flex;
    flex-direction: column;
    color: var(--category-panel-text-color, #333);
    width: 100%;
    background: var(--category-panel-background-color, rgba(255, 255, 255, 0.8));
    border-radius: 20px;
    box-shadow: 0 10px 30px -10px var(--category-panel-shadow-color, rgba(0, 0, 0, 0.1));
    padding: 1.5rem;
    box-sizing: border-box;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.CategoryPanel:hover {
    transform: translateY(-2px);
    box-shadow: 0 15px 40px -12px var(--category-panel-shadow-color, rgba(0, 0, 0, 0.15));
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid rgba(128, 128, 128, 0.1);
}

.header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.icon-wrapper {
    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
    padding: 10px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.header-icon {
    width: 24px;
    height: 24px;
    color: white;
}

.header-content {
    display: flex;
    flex-direction: column;
}

.category-title {
    font-size: 1.25rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.2;
    background: linear-gradient(to right, var(--category-panel-text-color, #333), #666);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.subtitle {
    font-size: 0.8rem;
    opacity: 0.7;
    font-weight: 500;
}

.back-button {
    background: rgba(0, 0, 0, 0.05);
    border: none;
    cursor: pointer;
    padding: 8px;
    border-radius: 50%;
    transition: all 0.2s ease;
    color: var(--category-panel-text-color, #333);
    display: flex;
    align-items: center;
    justify-content: center;
}

.back-button:hover {
    background: rgba(0, 0, 0, 0.1);
    transform: translateX(-2px);
    color: #3b82f6;
}

.back-button:disabled {
    opacity: 0;
    pointer-events: none;
}

.back-icon {
    width: 20px;
    height: 20px;
}

.tree-container {
    position: relative;
    min-height: 50px;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.category-ul,
.file-ul {
    list-style-type: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}


.file-node {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 1rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.3);
    /* Slightly clearer than folders */
    border: 1px solid rgba(0, 0, 0, 0.03);
    transition: all 0.2s ease;
    cursor: pointer;
}

.file-node:hover {
    background: rgba(255, 255, 255, 0.9);
    transform: translateX(5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.node-content {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    overflow: hidden;
}

.file-icon {
    width: 20px;
    height: 20px;
    color: #8b5cf6;
    /* Violet for files */
    flex-shrink: 0;
}

.file-name {
    font-size: 0.95rem;
    color: var(--text-color, #444);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.file-date {
    font-size: 0.8rem;
    color: #999;
    flex-shrink: 0;
    margin-left: 1rem;
}

.empty-state {
    text-align: center;
    padding: 2rem;
    opacity: 0.5;
    font-size: 0.9rem;
    font-style: italic;
}

/* Animations Updates */

/* List Staggered Animation */
.list-move,
.list-enter-active,
.list-leave-active {
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* Ensure absolute positioning for smoother list reordering/leaving */
.list-leave-active {
    position: absolute;
    width: 100%;
    z-index: 0;
    opacity: 0;
    /* Fade out faster */
    transition-duration: 0.3s;
}

.list-enter-from {
    opacity: 0;
    transform: translateX(20px) scale(0.95);
}

.list-leave-to {
    opacity: 0;
    transform: translateX(-20px) scale(0.95);
}

/* Apply staggered delay only on enter */
.list-enter-active {
    transition-delay: var(--delay);
}

/* Fade Scale for buttons */
.fade-scale-enter-active,
.fade-scale-leave-active {
    transition: all 0.3s ease;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
    opacity: 0;
    transform: scale(0.5);
}

/* Simple Fade for empty state */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>