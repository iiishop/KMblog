<script setup>
import { computed, onMounted, defineAsyncComponent } from 'vue';
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
    console.log(categories);
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
        console.log(node, value);
        tree[node] = {
            name: node,
            files: value.files || [],
            childCategories: value.childCategories ? buildNode(value.childCategories) : {},
        }
    }
    return tree;
};

const categoryTree = computed(() => buildTree(categories));
console.log(categoryTree.value);

const filteredTree = computed(() => {
    if (props.categoryPath.length === 0) {
        return categoryTree.value;
    }
    let current = categoryTree.value;
    console.log(current);
    for (const part of props.categoryPath) {
        if (current[part]) {
            current = current[part].childCategories;
        } else {
            return {};
        }
    }
    console.log(current);
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

onMounted(() => {
    gsap.from('.CategoryPanel', { opacity: 0, y: 50, duration: 1 });
});
</script>

<template>
    <div class="CategoryPanel">
        <h2 class="category-title">{{ props.categoryPath[props.categoryPath.length - 1] || '所有目录' }}</h2>
        <button @click="goBack" :disabled="props.categoryPath.length === 0" class="back-button">返回上级目录</button>
        <transition-group name="list" tag="ul">
            <CategoryNode v-for="(node, name) in filteredTree" :key="name" :name="name" :node="node"
                :parentPath="getParentPath()" />
        </transition-group>
    </div>
</template>

<style scoped>
.CategoryPanel {
    display: flex;
    flex-direction: column;
    color: rgb(10, 10, 10);
    width: 100%;
    background-color: #f8f8f8;
    border-radius: 1rem;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
    box-sizing: border-box;
}

.category-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 1rem;
    color: #333;
    text-align: center;
}

.back-button {
    align-self: flex-start;
    margin-bottom: 1rem;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    color: #fff;
    background-color: #007BFF;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: background-color 0.3s ease;
}

.back-button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

.back-button:not(:disabled):hover {
    background-color: #0056b3;
}

ul {
    list-style-type: none;
    padding-left: 1rem;
}

.list-enter-active,
.list-leave-active {
    transition: all 0.5s;
}

.list-enter,
.list-leave-to {
    opacity: 0;
    transform: translateY(30px);
}
</style>