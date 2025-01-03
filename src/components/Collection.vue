<script setup>
const props = defineProps({
    name: String,
    imageUrl: String,
    createDate: String,
    count: Number,
});
</script>

<template>
    <div class="collection">
        <img :src="imageUrl" alt="Collection" />
        <div class="info">
            <h2>{{ name }}</h2>
            <p>{{ createDate }}</p>
            <p>内有{{ count }}篇文章</p>
        </div>
    </div>
</template>

<style scoped>
.collection {
    display: flex;
    align-items: center;
    gap: 1rem;
    width: 100%;
    padding: 1rem;
    background-color: #f7f7f7;
    border-radius: 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.info {
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 100%;
}

img {
    width: 8rem;
    height: 5rem;
    object-fit: cover;
    border-radius: 10px;
    transition: transform 0.2s ease;
}

p {
    color: #666;
    margin: 0.5rem 0 0;
}

.collection:hover img {
    transform: scale(1.05);
}
</style>
