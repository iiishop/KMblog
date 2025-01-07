<script setup>
import { onMounted, ref } from 'vue';
import PostPanel from './components/PostPanel.vue';
import SelfIntroduction from './components/SelfIntroduction.vue';
import Collection from './components/Collection.vue';
import globalVar from './globalVar';

// 数据数组，每个对象包含 imageUrl 和 markdownUrl
const posts = ref([]);

onMounted(() => {
  posts.value = globalVar.markdowns;
});
</script>

<template>
  <div class="Scene">

    <div class="Posts">
      <!-- 使用 v-for 指令迭代 posts 数组 -->
      <PostPanel v-for="(post, index) in posts" :key="index" :imageUrl="post.imageUrl"
        :markdownUrl="post.markdownUrl" />
    </div>
    <div class="RightList">
      <SelfIntroduction />
      <div class="CollectionPanel">
        <h1>Collections</h1>
        <Collection :name="'旮旯给'" :imageUrl="'/src/Posts/Images/1.jpg'" :createDate="'2023-10-10'" :count="10" />
      </div>
    </div>
  </div>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'Noto Sans SC', sans-serif;
  background: white;
}

.Scene {
  display: flex;
  flex-direction: row;
  width: 100vw;
  justify-content: center;
  align-items: center;
  gap: 2rem;
}

.Posts {
  display: flex;
  gap: 2rem;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 50vw;
}

.RightList {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  align-items: center;
  justify-content: center;
  width: 25rem;
}

.CollectionPanel {
  display: flex;
  flex-direction: column;
  text-align: center;
  color: black;
  padding: 1rem;
  width: 100%;
  border-radius: 20px;
  box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
  height: auto;
}
</style>