<script setup>
import { onMounted, ref } from 'vue';
import globalVar from './globalVar';
import config from './config';
import PostPanel from './components/PostPanel.vue';
import SelfIntroduction from './components/SelfIntroduction.vue';
import Collection from './components/Collection.vue';
import HeadMenu from './components/HeadMenu.vue';
import './color.css'; // 导入 color.css
import TagPanel from './components/TagPanel.vue';

// 数据数组，每个对象包含 imageUrl 和 markdownUrl
const posts = ref([]);
const collections = ref([]);

// 设置主题
const setTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme);
};

onMounted(() => {
  posts.value = globalVar.markdowns;
  collections.value = globalVar.collections;
  document.title = config.BlogName + "|" + config.ShortDesc;

  // 应用主题
  setTheme(config.theme);
});
</script>

<template>
  <HeadMenu />
  <div class="Scene">
    <div class="Posts">
      <!-- 使用 v-for 指令迭代 posts 数组 -->
      <PostPanel v-for="(post, index) in posts" :key="post.id" :imageUrl="post.imageUrl"
        :markdownUrl="post.markdownUrl" />
    </div>
    <div class="RightList">
      <SelfIntroduction />
      <div class="CollectionPanel">
        <h1>Collections</h1>
        <Collection v-for="(collection, name) in collections" :name="name" :imageUrl="collection.image"
          :createDate="collection.date" :count="collection.count" />
      </div>
      <TagPanel />
    </div>
  </div>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'Noto Sans SC', sans-serif;
  background: var(--body-background-color);
  color: var(--body-text-color);
}

.Scene {
  display: flex;
  flex-direction: row;
  width: 100vw;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  padding-top: 4rem;
  background: var(--scene-background-color);
}

.Posts {
  display: flex;
  gap: 2rem;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 50vw;
  color: var(--posts-text-color);
}

.RightList {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  align-items: center;
  justify-content: center;
  width: 25rem;
  color: var(--rightlist-text-color);
}

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