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

// 递归函数，用于遍历 JSON 数据并提取所有 Markdown 文件链接
function extractMarkdownLinks(data) {
  let links = [];

  function traverse(obj) {
    for (let key in obj) {
      if (Array.isArray(obj[key])) {
        obj[key].forEach(item => {
          if (item.path && item.id) {
            links.push(item);
          }
        });
      } else if (typeof obj[key] === 'object') {
        traverse(obj[key]);
      }
    }
  }

  traverse(data);
  return links;
}

// 私有函数：解析 PostDirectory.json，过滤掉最顶层 "Markdowns"，并统计其余子项的数量
function parsePostDirectory(postDirectoryData) {
  const result = {};

  for (const key in postDirectoryData) {
    // 跳过最顶层的 "Markdowns" 字段
    if (key === 'Markdowns') {
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

// 解析 Markdown 文档的函数，只解析 meta 数据
export function parseMarkdown(content) {
  const metadataRegex = /^---\n([\s\S]*?)\n---/;
  const match = content.match(metadataRegex);

  if (match) {
    const meta = yaml.parse(match[1]);
    return { meta };
  } else {
    return { meta: {} };
  }
}

// 异步函数，用于加载和解析 PostDirectory.json 文件
export async function loadMarkdownLinks() {
  const data = await loadJsonFile('/src/assets/PostDirectory.json');
  if (data) {
    const markdownLinks = extractMarkdownLinks(data);

    const markdownWithImages = await Promise.all(markdownLinks.map(async (item) => {
      const { path: markdownUrl, id } = item;
      const markdownContent = await loadJsonFile(markdownUrl);
      if (markdownContent) {
        const { meta } = parseMarkdown(markdownContent);
        const imageName = meta.img;
        const imageUrl = imageName ? `/src/Posts/Images/${imageName}` : null;
        return { id, markdownUrl, imageUrl };
      }
      return null;
    }));

    console.log('Markdown with Images:', markdownWithImages);
    return markdownWithImages.filter(item => item !== null);
  }
  return [];
}

// 异步函数，用于加载和解析 Tags.json 文件
export async function loadTags() {
  const data = await loadJsonFile('/src/assets/Tags.json');
  if (data) {
    console.log('Tags loaded successfully:', data);
    return data;
  }
  return {};
}

// 异步函数，用于加载和解析 Categories.json 文件
export async function loadCategories() {
  const data = await loadJsonFile('/src/assets/Categories.json');
  if (data) {
    console.log('Categories loaded successfully:', data);
    return data;
  }
  return {};
}

// 新增的异步函数，用于加载并解析 /src/assets/PostDirectory.json，返回处理后的 Collections
export async function loadCollections() {
  const data = await loadJsonFile('/src/assets/PostDirectory.json');
  if (data) {
    const collections = parsePostDirectory(data);
    console.log('Collections loaded successfully:', collections);
    return collections;
  }
  return {};
}