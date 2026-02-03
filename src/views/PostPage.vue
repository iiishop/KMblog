<script setup>
import { defineAsyncComponent, ref, computed, onMounted } from 'vue';
import { isArticleEncrypted } from '@/utils/crypto';
import config from '@/config';
import axios from 'axios';

// 使用 Vite 的代码分割功能进行动态导入
const BaseLayout = defineAsyncComponent(() => import('@/views/BaseLayout.vue'));
const MarkdownPanel = defineAsyncComponent(() => import('@/components/MarkdownPanel.vue'));
const CryptoUnlock = defineAsyncComponent(() => import('@/components/CryptoUnlock.vue'));
const TOCPanel = defineAsyncComponent(() => import('@/components/TOCPanel.vue'));

const props = defineProps({
  markdownUrl: {
    type: String,
    required: true,
  },
});

const tagsData = ref({});
const isEncrypted = ref(false);
const isUnlocked = ref(false);
const decryptedContent = ref('');
const isLoading = ref(true); // 添加加载状态

// 加载 Tags.json 并检查文章是否加密
onMounted(async () => {
  try {
    const response = await axios.get('/assets/Tags.json');
    tagsData.value = response.data;

    // 检查当前文章是否需要解密
    isEncrypted.value = isArticleEncrypted(
      props.markdownUrl,
      config.CryptoTag,
      tagsData.value
    );

    console.log(`文章 ${props.markdownUrl} 是否加密: ${isEncrypted.value}`);
  } catch (error) {
    console.error('加载 Tags.json 失败:', error);
  } finally {
    isLoading.value = false; // 加载完成
  }
});

// 解锁成功的处理函数
const handleUnlocked = (content) => {
  decryptedContent.value = content;
  isUnlocked.value = true;
  console.log('文章解密成功');
};

// 计算实际显示的内容URL
const displayUrl = computed(() => {
  return props.markdownUrl;
});
</script>

<template>
  <BaseLayout :showTipList="true">
    <template #main>
      <!-- 加载中状态 -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在加载...</p>
      </div>

      <!-- 加密文章且未解锁：显示解锁界面 -->
      <CryptoUnlock v-else-if="isEncrypted && !isUnlocked" :encrypted-url="displayUrl" @unlocked="handleUnlocked" />

      <!-- 已解锁或非加密文章：显示内容 -->
      <MarkdownPanel v-else :markdown-url="displayUrl" :decrypted-content="isUnlocked ? decryptedContent : null" />
    </template>

    <template #float-tip>
      <TOCPanel content-selector=".post-content.markdown" />
    </template>
  </BaseLayout>
</template>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  color: var(--theme-body-text);
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--theme-panel-bg);
  border-top: 4px solid var(--theme-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}
</style>