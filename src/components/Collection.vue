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
        <img :src="imageUrl" />
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
    background-color: #f7f7f7;
    border-radius: 1rem;
    overflow: hidden;
    box-shadow: 5px 5px 10px #ccc;
    transition: all 0.2s ease-in-out;
}

.collection:hover {
    transform: scale(1.02);
}

.info {
    display: flex;
    flex-direction: column;
    justify-content: center;
    width: 100%;
}

img {
    width: auto;
    max-width: 50%;
    height: 8rem;
    object-fit: cover;
    /* 使用 -webkit-mask-image 和 mask-image 实现从左向右的透明渐变 */
    -webkit-mask-image: linear-gradient(to right, rgba(0, 0, 0, 1) 10%, rgba(0, 0, 0, 0));
    mask-image: linear-gradient(to right, rgba(0, 0, 0, 1) 10%, rgba(0, 0, 0, 0));
    -webkit-mask-size: 100% 100%;
    mask-size: 100% 100%;
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
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
