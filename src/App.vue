<script setup>
import { onMounted, ref } from 'vue';
import globalVar from './globalVar';
import config from './config';
import './color.css'; // 导入 color.css

// 数据数组，每个对象包含 imageUrl 和 markdownUrl

// 设置主题
const setTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme);
};

onMounted(() => {
  document.title = config.BlogName + "|" + config.ShortDesc;

  // 应用主题
  setTheme(config.theme);
});
</script>

<template>
<div id="app">
  <router-view />
</div>
</template>

<style>
</style>