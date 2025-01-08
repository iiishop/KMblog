<script setup>
import { config } from '@/config';
import { ref } from 'vue';
import { Icon } from '@iconify/vue';
import { openLink } from '@/utils';
import globalVar from '@/globalVar';

const avatarUrl = ref(config.HeadImg);
const name = ref(config.Name);
const description = ref(config.Description);
const links = ref(config.Links.map(link => ({
    name: link.name.toLowerCase(),
    url: link.url,
})));

const articleCount = ref(globalVar.markdowns.length);
const tagCount = ref(Object.keys(globalVar.tags).length);
const categoryCount = ref(Object.keys(globalVar.categories).length);
</script>
<template>
  <div class="user-info">
    <img :src="avatarUrl"/>
    <h2>{{ name }}</h2>
    <p>{{ description }}</p>
    <div class="stats">
      <div>
        <span>文章数量</span>
        <span>{{ articleCount }}</span>
      </div>
      <div>
        <span>标签数量</span>
        <span>{{ tagCount }}</span>
      </div>
      <div>
        <span>目录数量</span>
        <span>{{ categoryCount }}</span>
      </div>
    </div>
    <div class="icons">
        <div v-for="(link, index) in links" :key="index" class="link">
            <Icon :icon="`mdi:${link.name}`" @click="openLink(link.url)" style="cursor: pointer;"/>
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
  width: 100%;
  background-color: #ffe;
  box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
  color:black;
}

.user-info img{
  width: 40%;
  height: auto;
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
.icons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.link {
  font-size: 1.5rem;
  transition: all 0.3s ease;
}


.link:hover {
  color: #ff6347;
}
</style>