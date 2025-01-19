<script setup>
import { defineComponent, onMounted } from 'vue';
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

onMounted(() => {
    console.log(props.parentPath);
    console.log(props.name);
});
</script>

<template>
    <li>
        <div class="category-node" @click="navigateToCategory">
            <span>{{ name }}</span>
            <span class="file-count" @click="navigateToArchive">({{ node.files.length }} 篇文章)</span>
        </div>
        <ul v-if="Object.keys(node.subcategories).length" class="nested">
            <CategoryNode v-for="(subNode, subName) in node.subcategories" :key="subName" :name="subName" :node="subNode" :parentPath="`${props.parentPath}/${props.name}`" />
        </ul>
    </li>
</template>

<style scoped>
li {
    margin-bottom: 0.5rem;
}

.category-node {
    display: flex;
    justify-content: space-between;
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
    border-left: 1px solid #ccc;
}
</style>
