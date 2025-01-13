<!-- MarkdownViewer.vue -->
<template>
  <div class="MarkdownPanel">

    <div v-if="metadata.img" class="post-header">
      <img :src="metadata.img" alt="Post Image" />
    </div>
    <div class="post-content">

      <h1>{{ metadata.title }}</h1>
      <p>{{ metadata.date }}</p>
      <div v-html="htmlContent"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import fm from 'front-matter';
import MarkdownIt from 'markdown-it';
import { defineProps } from 'vue';

// 定义 props
const props = defineProps({
  markdownUrl: {
    type: String,
    required: true
  }
});

const metadata = ref({});
const htmlContent = ref('');

// 创建 markdown-it 实例
const md = new MarkdownIt();

// 解析 Markdown 文件并提取 metadata 和内容
const parseMarkdown = async (url) => {
  try {
    const response = await axios.get(url);
    const markdown = response.data;

    // 使用 front-matter 解析 metadata
    const { attributes, body } = fm(markdown);
    metadata.value = attributes;
    metadata.value.img = `/src/Posts/Images/${metadata.value.img}`;

    // 解析 Markdown 内容
    htmlContent.value = md.render(body);
  } catch (error) {
    console.error('Error fetching or parsing markdown file:', error);
  }
};

// 监控 markdownUrl 的变化
watch(() => props.markdownUrl, (newUrl) => {
  parseMarkdown(newUrl);
}, { immediate: true });

onMounted(() => {
  parseMarkdown(props.markdownUrl);
});
</script>

<style>
.MarkdownPanel {
  display: flex;
  gap: 2rem;
  flex-direction: column;
  color: rgb(10, 10, 10);
  width: 100%;
  padding: 1rem;
  background-color: #f8f8f8;
  border-radius: 1rem;
  box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
}
.post-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
.post-header img {
  max-width: 100%;
  height: auto;
  max-height: 30rem;
}
</style>