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
    <li>
        <div class="category-node" @click="navigateToCategory">
            <span>{{ name }}</span>
            <span class="file-count" @click="navigateToArchive">&ensp;({{ totalFileCount }} 篇文章)</span>
        </div>
        <ul v-if="node.childCategories && Object.keys(node.childCategories).length" class="nested">
            <CategoryNode v-for="(subNode, subName) in node.childCategories" :key="subName" :name="subName" :node="subNode" :parentPath="`${props.parentPath}/${props.name}`" />
        </ul>
    </li>
</template>

<style scoped>
li {
    margin-bottom: 0.5rem;
}

.category-node {
    display: flex;
    padding: 0.5rem;
    border-radius: 0.5rem;
    transition: transform 0.3s ease, background-color 0.3s ease;
    cursor: pointer;
}

.category-node:hover {
    transform: scale(1.05);
    background-color: #f0f0f0;
}

.file-count {
    font-size: 0.9rem;
    color: #666;
    cursor: pointer;
}

ul.nested {
    margin-left: 1rem;
    padding-left: 1rem;
}
</style>