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