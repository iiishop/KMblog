import axios from 'axios';
import yaml from 'yaml';

// 通用的异步函数，用于加载和解析 JSON 文件
async function loadJsonFile(filePath) {
  try {
    const response = await axios.get(filePath);
    return response.data;
  } catch (error) {
    console.error(`Error loading ${filePath}:`, error);
    return null;
  }
}

// 私有函数：解析 PostDirectory.json，过滤掉最顶层 "Markdowns"，并统计其余子项的数量
function parsePostDirectory(postDirectoryData) {
  const result = {};

  for (const key in postDirectoryData) {
    // 跳过最顶层的 "Markdowns" 和 "WaterfallGraph" 字段
    if (key === 'Markdowns' || key === 'WaterfallGraph') {
      continue;
    }

    // 处理其它字段（例如 "Gal", "旮旯给" 等）
    const itemData = postDirectoryData[key];
    const { date, image, Markdowns } = itemData || {};

    // 如果存在 Markdowns 数组，则统计其长度；否则为 0
    const count = Array.isArray(Markdowns) ? Markdowns.length : 0;

    result[key] = {
      date: date || '',
      image: image || '',
      count: Number(count),
    };
  }

  return result;
}

// 导出的函数

export function openLink(url) {
  window.open(url, '_blank');
}

// 异步解析 Markdown 文档的函数，只解析 meta 数据
export async function parseMarkdownMetadata(content) {
  const metadataRegex = /^---\r?\n([\s\S]*?)\r?\n---/;
  const match = content.match(metadataRegex);

  if (match) {
    const meta = yaml.parse(match[1]);
    console.debug('Parsed metadata:', meta); // 添加调试日志
    return { meta };
  } else {
    console.debug('No metadata found'); // 添加调试日志
    return { meta: {} };
  }
}

// 异步函数，加载单文件 Metadata.json（预生成的全部文章摘要，替代 N+1 逐个 fetch）
export async function loadMarkdownLinks() {
  const list = await loadJsonFile('/assets/Metadata.json');
  if (!list || !Array.isArray(list)) return {};

  return list.reduce((acc, item) => {
    const markdownUrl = (item.path || '').replace(/\\/g, '/');
    if (!markdownUrl) return acc;
    acc[markdownUrl] = {
      imageUrl: item.img || null,
      date: item.date || '',
      title: item.title || '',
      pre: item.pre || '',
      tags: item.tags || [],
      categories: item.categories || [],
    };
    return acc;
  }, {});
}

// 异步函数，用于加载和解析 Tags.json 文件
export async function loadTags() {
  const data = await loadJsonFile('/assets/Tags.json');
  if (data) {
    console.log('Tags loaded successfully:', data);
    return data;
  }
  return {};
}

// 异步函数，用于加载和解析 Categories.json 文件
export async function loadCategories() {
  const data = await loadJsonFile('/assets/Categories.json');
  if (data) {
    console.log('Categories loaded successfully:', data);
    return data;
  }
  return {};
}

// 新增的异步函数，用于加载并解析 /assets/PostDirectory.json，返回处理后的 Collections
export async function loadCollections() {
  const data = await loadJsonFile('/assets/PostDirectory.json');
  if (data) {
    const collections = parsePostDirectory(data);
    console.log('Collections loaded successfully:', collections);
    return collections;
  }
  return {};
}