<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
    name: String,
    node: Object,
    parentPath: {
        type: String,
        default: ''
    }
});

const router = useRouter();

const navigateToCategory = () => {
    const newPath = `${props.parentPath}/${props.name}`.replace(/^\/+/, '');
    router.push(`/category/${newPath}`);
};

const navigateToArchive = (event) => {
    event.stopPropagation();
    const archivePath = `${props.parentPath}/${props.name}`.replace(/^\/+/, '');
    router.push(`/archive/categories/${archivePath}`);
};

const totalFileCount = computed(() => {
    const countFiles = (node) => {
        let count = node.files ? node.files.length : 0;
        if (node.childCategories) {
            for (const child of Object.values(node.childCategories)) {
                count += countFiles(child);
            }
        }
        return count;
    };
    return countFiles(props.node);
});
</script>

<template>
    <li class="category-item">
        <div class="category-node" @click="navigateToCategory">
            <div class="node-content">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="folder-icon">
                    <path
                        d="M19.5 21a3 3 0 0 0 3-3v-4.5a3 3 0 0 0-3-3h-15a3 3 0 0 0-3 3V18a3 3 0 0 0 3 3h15ZM1.5 10.146V6a3 3 0 0 1 3-3h5.379a2.25 2.25 0 0 1 1.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 0 1 3 3v1.146A4.483 4.483 0 0 0 19.5 9h-15a4.483 4.483 0 0 0-3 1.146Z" />
                </svg>
                <span class="category-name">{{ name }}</span>
            </div>

            <div class="file-count-badge" @click="navigateToArchive" title="查看归档">
                <span>{{ totalFileCount }}</span>
            </div>
        </div>

        <transition name="expand">
            <ul v-if="node.childCategories && Object.keys(node.childCategories).length" class="nested-list">
                <CategoryNode v-for="(subNode, subName) in node.childCategories" :key="subName" :name="subName"
                    :node="subNode" :parentPath="`${props.parentPath}/${props.name}`" />
            </ul>
        </transition>
    </li>
</template>

<style scoped>
.category-item {
    margin-bottom: 0.5rem;
    list-style: none;
}

.category-node {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 1rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(0, 0, 0, 0.05);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.category-node::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #3b82f6, #06b6d4);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.category-node:hover {
    transform: translateX(5px);
    background: rgba(255, 255, 255, 0.8);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.category-node:hover::before {
    opacity: 1;
}

.node-content {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.folder-icon {
    width: 20px;
    height: 20px;
    color: #3b82f6;
    /* Blue folder color */
    transition: transform 0.3s ease;
}

.category-node:hover .folder-icon {
    transform: scale(1.1);
}

.category-name {
    font-weight: 600;
    color: var(--text-color, #333);
    font-size: 1rem;
}

.file-count-badge {
    background: rgba(59, 130, 246, 0.1);
    color: #3b82f6;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.8rem;
    font-weight: 700;
    min-width: 20px;
    text-align: center;
    transition: all 0.2s ease;
}

.file-count-badge:hover {
    background: #3b82f6;
    color: white;
    transform: scale(1.1);
}

/* Updated Nested List Styles with Tree Lines */
.nested-list {
    margin-left: 1.5rem;
    padding-left: 1rem;
    border-left: 2px dashed rgba(0, 0, 0, 0.1);
    margin-top: 0.5rem;
    list-style: none;
}

/* Animation for expanding/collapsing if we add toggling later, 
   but currently it just renders if present. 
   Vue Transition classes for standard entry/leave */

.expand-enter-active,
.expand-leave-active {
    transition: all 0.3s ease;
    overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}
</style>