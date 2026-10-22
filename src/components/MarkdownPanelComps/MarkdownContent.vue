<template>
  <article class="markdown" ref="contentRef" @click="openImage">
    <p v-if="renderError" class="render-error" role="status">{{ renderError }}</p>
    <div v-html="htmlContent"></div>
    <Teleport to="body">
      <ImageViewer v-model:visible="viewerVisible" :image-src="viewerImageSrc" :image-alt="viewerImageAlt"
        :image-type="viewerImageType" :svg-content="viewerSvgContent" />
    </Teleport>
  </article>
</template>

<script setup>
import { ref, watch, nextTick, onBeforeUnmount, defineAsyncComponent } from 'vue';
import fm from 'front-matter';
import md from './MarkdownRenender.js';
import './MarkdownStyle.css';
import mermaid from 'mermaid';
import { renderDynamicComponents, unmountDynamicComponents } from './DynamicComponentRenderer.js';
import ImageViewer from '@/components/ImageViewer.vue';

const components = {
  steamgameblock: defineAsyncComponent(() => import('./SteamGameBlock.vue')),
  bangumiblock: defineAsyncComponent(() => import('./BangumiBlock.vue')),
  bilibilivideoblock: defineAsyncComponent(() => import('./BilibiliVideoBlock.vue')),
  githubrepoblock: defineAsyncComponent(() => import('./GithubRepoBlock.vue')),
  xiaohongshunoteblock: defineAsyncComponent(() => import('./XiaohongshuNoteBlock.vue')),
  carouselblock: defineAsyncComponent(() => import('./CarouselBlock.vue'))
};
const props = defineProps({ content: { type: String, default: '' } });
const emit = defineEmits(['rendered']);
const contentRef = ref(null);
const htmlContent = ref('');
const renderError = ref('');
const viewerVisible = ref(false);
const viewerImageSrc = ref('');
const viewerImageAlt = ref('');
const viewerImageType = ref('img');
const viewerSvgContent = ref('');
let revision = 0;
let rendering = false;
let disposed = false;

// One renderer for published articles, gallery descriptions and editor drafts.
// Finish an in-flight chart before replacing its DOM; then render the latest draft.
async function render() {
  if (rendering || disposed || !contentRef.value) return;
  rendering = true;
  const current = revision;
  const container = contentRef.value;
  try {
    const { body } = fm(props.content);
    const html = md.render(body.replace(/!\[([^\]]*)\]\(([^)<>]+\s+[^)<>]+)\)/g, '![$1](<$2>)'));
    unmountDynamicComponents(container);
    htmlContent.value = html;
    renderError.value = '';
    viewerVisible.value = false;
    emit('rendered', html);
    await nextTick();
    if (disposed || current !== revision) return;
    renderDynamicComponents(container, components);
    const nodes = container.querySelectorAll('.mermaid');
    if (nodes.length) {
      try {
        await mermaid.run({ nodes });
      } catch {
        if (!disposed && current === revision) renderError.value = '图表语法暂时不完整，请检查图表内容。';
      }
      if (disposed || current !== revision) return;
      container.querySelectorAll('.mermaid svg').forEach(svg => {
        svg.removeAttribute('width');
        svg.removeAttribute('height');
        Object.assign(svg.style, { width: '100%', height: '400px', maxWidth: '100%', maxHeight: '400px', display: 'block', margin: '0 auto' });
      });
    }
    container.querySelectorAll('img').forEach(img => img.classList.add('clickable-image'));
    container.querySelectorAll('.mermaid-wrapper').forEach(el => el.classList.add('clickable-mermaid'));
  } catch (error) {
    if (!disposed && current === revision) renderError.value = `预览暂未更新，请检查文章头部格式：${error.message}`;
  } finally {
    rendering = false;
    if (!disposed && current !== revision) void render();
  }
}

function openImage(event) {
  const diagram = event.target.closest('.mermaid-wrapper');
  const svg = diagram?.querySelector('svg');
  if (svg) {
    viewerImageType.value = 'svg';
    viewerSvgContent.value = svg.outerHTML;
    viewerImageAlt.value = 'Mermaid 图表';
  } else if (event.target.matches('img.clickable-image')) {
    viewerImageType.value = 'img';
    viewerImageSrc.value = event.target.src;
    viewerImageAlt.value = event.target.alt || '';
  } else return;
  viewerVisible.value = true;
}

watch(() => props.content, () => { revision++; void render(); }, { flush: 'post' });
watch(contentRef, () => { void render(); });
onBeforeUnmount(() => {
  disposed = true;
  revision++;
  unmountDynamicComponents(contentRef.value);
});
</script>

<style scoped>
.render-error { padding: 10px; border-left: 3px solid #c24b36; font-size: 13px; line-height: 1.6; }
</style>
