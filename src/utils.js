import axios from 'axios';
import yaml from 'yaml';
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

export function openLink(url) {
  window.open(url, '_blank');
}

// 异步函数，用于加载和解析 JSON 文件
export async function loadMarkdownLinks() {
  try {
    // 加载 PostDirectory.json 文件
    const response = await axios.get('/src/assets/PostDirectory.json');
    const data = response.data;

    // 解析 JSON 文件，提取所有 Markdown 文件的链接
    const markdownLinks = extractMarkdownLinks(data);

    // 获取每个 Markdown 文件中的元数据
    const markdownWithImages = await Promise.all(markdownLinks.map(async (item) => {
      const { path: markdownUrl, id } = item;
      const markdownContent = await axios.get(markdownUrl);
      const { meta } = parseMarkdown(markdownContent.data);
      const imageName = meta.img;
      const imageUrl = imageName ? `/src/Posts/Images/${imageName}` : null;
      return { id, markdownUrl, imageUrl };
    }));

    console.log('Markdown with Images:', markdownWithImages);
    return markdownWithImages;
  } catch (error) {
    console.error('Error loading PostDirectory.json:', error);
    return [];
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

// 异步函数，用于加载和解析 Tags.json 文件
export async function loadTags() {
  try {
    // 使用 axios 读取 Tags.json 文件
    const response = await axios.get('/src/assets/Tags.json');

    // 解析响应为 JSON
    const data = response.data;

    console.log('Tags loaded successfully:', data);
    return data;
  } catch (error) {
    console.error('Error loading tags:', error);
    return {};
  }
}