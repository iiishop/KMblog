<script setup>
import config from '@/config';
import { ref, onMounted } from 'vue';
import { Icon } from '@iconify/vue';
import { openLink } from '@/utils';
import globalVar from '@/globalVar';
import { useRouter } from 'vue-router';
import { gsap } from 'gsap';

const avatarUrl = ref(config.HeadImg);
const name = ref(config.Name);
const description = ref(config.Description);
const links = ref(config.Links.map(link => ({
  name: link.name.toLowerCase(),
  url: link.url,
})).slice(0, 10));

const articleCount = ref(Object.keys(globalVar.markdowns).length);
const tagCount = ref(Object.keys(globalVar.tags).length);
const categoryCount = ref(Object.keys(globalVar.categories).length);

onMounted(() => {
  gsap.from('.user-info', { opacity: 0, duration: 1 });
});
</script>
<template>
  <div class="user-info">
    <img :src="avatarUrl" />
    <h2>{{ name }}</h2>
    <p>{{ description }}</p>
    <div class="stats">
      <router-link to="/archive" class="stat-link">
        <div>
          <span>文章数量</span>
          <span>{{ articleCount }}</span>
        </div>
      </router-link>
      <router-link to="/tags" class="stat-link">
        <div class="clickable">
          <span>标签数量</span>
          <span>{{ tagCount }}</span>
        </div>
      </router-link>
      <div>
        <span>目录数量</span>
        <span>{{ categoryCount }}</span>
      </div>
    </div>
    <div class="icons">
      <div v-for="(link, index) in links" :key="index" class="link">
        <Icon :icon="`mdi:${link.name}`" @click="openLink(link.url)" style="cursor: pointer;" />
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
  padding: 1.5rem;
  width: 100%;
  background-color: var(--user-info-background-color);
  box-shadow: 1px 1px 5px var(--user-info-box-shadow);
  color: var(--user-info-text-color);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.user-info:hover {
  transform: translateY(-10px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.user-info img {
  width: 40%;
  height: auto;
  border-radius: 50%;
  box-shadow: 0px 0px 5px var(--user-info-img-box-shadow);
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

.stat-link {
  text-decoration: none;
  color: inherit;
  transition: color 0.3s ease;
}

.stat-link:hover {
  color: var(--link-hover-color);
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
  color: var(--link-hover-color);
  transform: scale(1.2);
}
</style>