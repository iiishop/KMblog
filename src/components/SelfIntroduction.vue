<script setup>
import { config } from '@/config';
import { ref } from 'vue';
import { Icon } from '@iconify/vue';

const avatarUrl = ref(config.HeadImg);
const name = ref(config.Name);
const description = ref(config.Description);
const links = ref(config.Links.map(link => ({
    name: link.name.toLowerCase(),
    url: link.url,
})));
</script>
<template>
  <div class="user-info">
    <img :src="avatarUrl"/>
    <h2>{{ name }}</h2>
    <p>{{ description }}</p>
    <div class="stats">
      <div>
        <span>文章数量</span>
        <span>16</span>
      </div>
      <div>
        <span>分类数量</span>
        <span>4</span>
      </div>
      <div>
        <span>标签数量</span>
        <span>19</span>
      </div>
    </div>
    <div class="icons">
        <div v-for="(link, index) in links" :key="index" class="link">
            <Icon :icon="`mdi:${link.name}`" />
            <a :href="link.url">{{ link.name }}</a>
        </div>
    </div>
  </div>
</template>

<style scoped>
.user-info {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-radius: 20px;
  padding: 1rem;
  width: 20rem;
  background-color: #ffe;
  box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
  color:black;
}

.user-info img{
  width: 40%;
  height: 40%;
  border-radius: 50%;
  box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.5);
  transition: all 0.5s ease;
}

.user-info img:hover {
  transform: rotate(180deg);
}

.stats {
  margin-bottom: 20px;
}

.stats div {
  display: inline-block;
  margin: 0 10px;
}

.stats span {
  display: block;
}

.icons img {
  width: 30px;
  height: 30px;
  margin: 5px;
}
</style>
