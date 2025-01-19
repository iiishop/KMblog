<template>
  <div class="MarkdownPanel">
    <div class="post-header">
      <div class="image-container">
        <img v-if="metadata.img" :src="metadata.img" alt="Post Image" />
        <div class="overlay">
          <h1>{{ metadata.title }}</h1>
          <div class="category-panel">
            <IconCategory style="width: 1rem; height: 1rem;" v-if="lastCategory" />
            <router-link :to="categoryLink">{{ lastCategory }}</router-link>
          </div>
          <div class="date-panel">
            <IconDate style="width: 1rem; height: 1rem;" v-if="metadata.date" />
            <router-link :to="archiveLink">{{ metadata.date }}</router-link>
          </div>
        </div>
      </div>
    </div>
    <div class="post-content markdown">
      <div v-html="htmlContent"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed, nextTick } from 'vue';
import axios from 'axios';
import fm from 'front-matter';
import md from '@/components/MarkdownPanelComps/MarkdownRenender.js';
import '@/components/MarkdownPanelComps/MarkdownStyle.css';
import { defineProps } from 'vue';
import IconCategory from '@/components/icons/IconCategory.vue';
import IconDate from '@/components/icons/IconDate.vue';
import config from '@/config';
import SteamGameBlock from './MarkdownPanelComps/SteamGameBlock.vue';
import { renderDynamicComponents } from '@/components/MarkdownPanelComps/DynamicComponentRenderer.js';
import { parseMarkdownMetadata } from '@/utils';

// 定义 props
const props = defineProps({
  markdownUrl: {
    type: String,
    required: true
  }
});

const metadata = ref({});
const htmlContent = ref('');

// 解析 Markdown 文件并提取 metadata 和内容
const parseMarkdown = async (url) => {
  try {
    const response = await axios.get(url);
    const markdown = response.data;

    // 使用 front-matter 解析 metadata
    const { body } = fm(markdown);
    const { meta } = await parseMarkdownMetadata(markdown);
    metadata.value = meta;
    if (metadata.value.img) {
      metadata.value.img = `/src/Posts/Images/${metadata.value.img}`;
    }
    const date = new Date(metadata.value.date);
    const hours = date.getHours();

    // 格式化日期为 '年-月-日'
    metadata.value.date = date.toLocaleDateString().replace(/\//g, '月').replace('月', '年') + '日';

    // 添加时间段
    if (hours < 6) {
      metadata.value.date += ' 凌晨';
    } else if (hours < 12) {
      metadata.value.date += ' 上午';
    } else if (hours < 18) {
      metadata.value.date += ' 下午';
    } else {
      metadata.value.date += ' 晚上';
    }

    // 解析 Markdown 内容
    htmlContent.value = md.render(body);
    console.log(htmlContent.value);
    console.log(body);

    // 在 nextTick 中手动编译和挂载组件
    await nextTick();
    const container = document.querySelector('.post-content.markdown');
    renderDynamicComponents(container, {
      'steamgameblock': SteamGameBlock
      // 在这里添加其他组件映射
    });
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
const lastCategory = computed(() => {
  if (metadata.value.categories && metadata.value.categories.length > 0) {
    return metadata.value.categories[metadata.value.categories.length - 1];
  }
  return '';
});
const categoryLink = computed(() => {
  if (metadata.value.categories && metadata.value.categories.length > 0) {
    const fullPath = metadata.value.categories.join('/');
    return { name: 'CategoryPage', params: { fullPath } };
  }
  return '#';
});

const archiveLink = computed(() => ({ name: 'ArchivePage' }));
</script>

<style scoped>
.MarkdownPanel {
  display: flex;
  flex-direction: column;
  color: rgb(10, 10, 10);
  width: 100%;
  background-color: #f8f8f8;
  border-radius: 1rem;
  box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
}

.post-header {
  display: flex;
  justify-content: center;
  /* 水平居中 */
  align-items: center;
  /* 垂直居中 */
  position: relative;
  width: 100%;
  border-top-left-radius: 1rem;
  border-top-right-radius: 1rem;
  overflow: hidden;
  max-height: 30rem;
}

.image-container {
  position: relative;
  width: 100%;
  min-height: 10rem;
  max-height: 30rem;
}

.image-container img {
  display: block;
  margin: 0 auto;
  /* 图片水平居中 */
  max-width: 100%;
  height: auto;
  max-height: 30rem;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  text-align: center;
}

.overlay h1,
.overlay p {
  margin: 0;
}

.post-content {
  padding: 1rem;
}

.category-panel {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  margin: 0.2rem;
}

.category-panel a {
  text-decoration: none;
  display: flex;
  align-items: center;
  text-align: center;
  position: relative;
  color: white;
  transition: color 0.2s ease;
}

.category-panel a::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 2px;
  background-color: currentColor;
  transform: scaleX(0);
  transition: transform 0.2s ease;
}

.category-panel a:hover::after {
  transform: scaleX(1);
}

.date-panel {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  margin: 0.2rem;
}

.date-panel a {
  text-decoration: none;
  display: flex;
  align-items: center;
  text-align: center;
  position: relative;
  transition: color 0.2s ease;
  color: white;
}
</style>