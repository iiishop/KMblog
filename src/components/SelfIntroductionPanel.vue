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
      <router-link to="/category" class="stat-link">
        <div>
          <span>目录数量</span>
          <span>{{ categoryCount }}</span>
        </div>
      </router-link>
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
  border-radius: 24px;
  padding: 2.5rem 2rem;
  width: 100%;
  /* 极致质感背景：保持原变量为基底，叠加细腻光泽 */
  background: var(--user-info-background-color);
  background-image: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.05) 100%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  /* 现代多层阴影 & 内发光边框 */
  box-shadow: 
    0 15px 35px -5px rgba(0,0,0,0.1), 
    0 0 0 1px rgba(255,255,255,0.6) inset;
  color: var(--user-info-text-color);
  transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
}

/* 悬停时的上浮与光影增强 */
.user-info:hover {
  transform: translateY(-8px);
  box-shadow: 
    0 25px 50px -12px rgba(0,0,0,0.15),
    0 0 0 1px rgba(255,255,255,0.9) inset;
}

.user-info img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 50%;
  /* 双层立体边框 */
  border: 4px solid rgba(255,255,255,0.95);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  transition: all 0.7s cubic-bezier(0.34, 1.56, 0.64, 1);
  background-color: #fff;
}

.user-info img:hover {
  transform: rotate(360deg) scale(1.15);
  box-shadow: 0 15px 35px rgba(0,0,0,0.25);
  border-color: #fff;
}

.user-info h2 {
  margin: 1.5rem 0 0.5rem;
  font-size: 1.8rem;
  font-weight: 800;
  letter-spacing: -0.5px;
  /* 文字渐变增强层次（需背景色配合，若背景深色则回退到inherit） */
  background: linear-gradient(120deg, var(--user-info-text-color) 0%, #888 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: var(--user-info-text-color); /* 回退颜色 */
}

.user-info p {
  margin: 0 0 1.5rem;
  font-size: 0.95rem;
  opacity: 0.8;
  line-height: 1.6;
  max-width: 90%;
  font-weight: 500;
}

.stats {
  display: flex;
  justify-content: space-around;
  width: 100%;
  padding: 1.25rem 0;
  margin-bottom: 1.5rem;
  /* 精致的分隔线 */
  border-top: 1px solid rgba(0,0,0,0.06);
  border-bottom: 1px solid rgba(0,0,0,0.06);
}

.stats div {
  margin: 0 !important; /* 覆盖原有 inline-block 的 margin */
}

.stat-link {
  text-decoration: none;
  color: inherit;
  flex: 1;
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
}

.stat-link:hover {
  transform: translateY(-3px);
}

/* 统计项内部布局 */
.stat-link div.clickable, 
.stat-link div {
  display: flex !important;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-link span:first-child {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.6;
  font-weight: 700;
}

.stat-link span:last-child {
  font-size: 1.5rem;
  font-weight: 800;
  transition: color 0.3s ease;
}

.stat-link:hover span:last-child {
  color: var(--link-hover-color);
}

.icons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
  width: 100%;
}

.link {
  font-size: 1.3rem;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgb(228, 226, 226);
  color: var(--user-info-text-color);
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
}

.link:hover {
  color: #fff;
  background: var(--link-hover-color, #333);
  transform: translateY(-4px) scale(1.1);
  box-shadow: 0 8px 20px rgba(0,0,0,0.15);
}



/* 3. 标题底部动态装饰线 */
.user-info h2 {
  position: relative;
  display: inline-block; /* 收缩宽度以适应文字 */
}

.user-info h2::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 4px;
  background: var(--user-info-text-color);
  opacity: 0.15;
  border-radius: 10px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.user-info:hover h2::after {
  width: 50px;
  opacity: 0.4;
  background: var(--link-hover-color, var(--user-info-text-color));
}
</style>