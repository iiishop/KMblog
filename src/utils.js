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

// 异步函数，用于加载和解析 PostDirectory.json 文件
export async function loadMarkdownLinks() {
  const data = await loadJsonFile('/src/assets/PostDirectory.json');
  if (data) {
    const markdownLinks = extractMarkdownLinks(data);

    const markdownWithImages = await Promise.all(markdownLinks.map(async (item) => {
      const { path: markdownUrl } = item;
      const normalizedMarkdownUrl = markdownUrl.replace(/\\/g, '/'); // 将反斜杠替换为正斜杠
      console.debug('Loading Markdown file:', normalizedMarkdownUrl); // 输出 Markdown 文件路径
      const markdownContent = await loadJsonFile(normalizedMarkdownUrl);
      if (markdownContent) {
        const { meta } = await parseMarkdownMetadata(markdownContent); // 使用异步解析函数
        const imageName = meta.img;
        const imageUrl = imageName ? `/src/Posts/Images/${imageName}` : null;
        return { markdownUrl: normalizedMarkdownUrl, imageUrl, date: meta.date, title: meta.title, pre: meta.pre, tags: meta.tags, categories: meta.categories };
      }
      return null;
    }));

    // Filter out null values and sort by date
    const sortedMarkdownWithImages = markdownWithImages
      .filter(item => item !== null)
      .sort((a, b) => new Date(b.date) - new Date(a.date));

    // Create a dictionary
    const markdownDict = sortedMarkdownWithImages.reduce((acc, { markdownUrl, imageUrl, date, title, pre, tags, categories }) => {
      acc[markdownUrl] = { imageUrl, date, title, pre, tags, categories }; // 包含所有 metadata 信息
      return acc;
    }, {});

    console.log('Markdown Dictionary:', markdownDict);
    return markdownDict;
  }
  return {};
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