<script setup>
import globalVar from '@/globalVar';
import { ref, onMounted } from 'vue';
const props = defineProps({
    
})
const posts = ref({});

onMounted(() => {
    posts.value = globalVar.markdowns;
});
</script>
<template>
    <div class="ArchivePanel">

    </div>
</template>
<style scoped>
.ArchivePanel {
    display: flex;
    flex-direction: column;
    color: rgb(10, 10, 10);
    width: 100%;
    background-color: #f8f8f8;
    border-radius: 1rem;
    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
}
</style>