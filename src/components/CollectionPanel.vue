<script setup>
import Collection from './CollectionPanelComps/Collection.vue'
import { onMounted, ref } from 'vue'
import globalVar from '../globalVar.js'

const collections = ref({});
onMounted(() => {
    collections.value = globalVar.collections;
}
)
</script>
<template>
    <div class="CollectionPanel">
        <h1>Collections</h1>
        <Collection v-for="(collection, name) in collections" :name="name" :imageUrl="collection.image"
            :createDate="collection.date" :count="collection.count" />
    </div>
</template>
<style scoped>
.CollectionPanel {
    display: flex;
    flex-direction: column;
    text-align: center;
    background: var(--collectionpanel-background-color);
    padding: 1rem;
    width: 100%;
    border-radius: 20px;
    box-shadow: 1px 1px 5px var(--collectionpanel-shadow-color);
    height: auto;
    gap: 1rem;
    color: var(--collectionpanel-text-color);
}
</style>