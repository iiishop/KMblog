import { mount, flushPromises } from '@vue/test-utils';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import axios from 'axios';
const mocks = vi.hoisted(() => ({ mount: vi.fn(), unmount: vi.fn(), charts: vi.fn() }));
vi.mock('axios', () => ({ default: { get: vi.fn() } }));
vi.mock('mermaid', () => ({ default: { initialize: vi.fn(), run: mocks.charts } }));
vi.mock('./DynamicComponentRenderer.js', () => ({ renderDynamicComponents: mocks.mount, unmountDynamicComponents: mocks.unmount }));
import MarkdownPanel from '@/components/MarkdownPanel.vue';
import MarkdownPreview from '@/components/Editor/MarkdownPreview.vue';
import MarkdownContent from './MarkdownContent.vue';
import ImageDescription from '@/components/WaterfallPanelComps/ImageDescription.vue';
import ImageModal from '@/components/WaterfallPanelComps/ImageModal.vue';

const source = `---
title: 同一篇文章
date: 2026-10-23
img: cover.png
tags: [Vue, Markdown]
categories: [技术, 前端]
---
# 标题

正文 **加粗**，公式 $x^2$。

| 列一 | 列二 |
| --- | --- |
| A | B |

![图片](/Posts/Images/with space.png)

\`\`\`javascript
const answer = 42;
\`\`\`

\`\`\`mermaid
graph TD; A-->B;
\`\`\`

\`\`\`carousel
/Posts/Images/one.png | 第一张
\`\`\`
`;
const wrappers = [];
const render = (component, props) => {
  const wrapper = mount(component, { props, global: { stubs: {
    RouterLink: { template: '<a><slot /></a>' },
    UtterancesComments: { template: '<div class="comments-stub" />' },
    ImageViewer: { name: 'ImageViewer', props: ['visible', 'imageType', 'imageSrc', 'svgContent'], template: '<div />' }
  } } });
  wrappers.push(wrapper);
  return wrapper;
};
const normalized = html => html.replace(/ data-v-[\w-]+=""/g, '').replace(/mermaid-[a-z0-9]+/g, 'mermaid-id');
beforeEach(() => {
  vi.useFakeTimers();
  mocks.charts.mockImplementation(async ({ nodes }) => {
    nodes.forEach(node => { node.innerHTML = '<svg width="900" height="500"><text>A → B</text></svg>'; });
  });
});
afterEach(() => {
  wrappers.splice(0).forEach(wrapper => wrapper.unmount());
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe('published and draft rendering parity', () => {
  it('uses the same full article DOM, styles, diagrams and block registry', async () => {
    axios.get.mockResolvedValue({ data: source });
    const published = render(MarkdownPanel, { markdownUrl: '/article.md' });
    const preview = render(MarkdownPreview, { markdownUrl: '/article.md', content: source });
    await vi.advanceTimersByTimeAsync(180);
    await flushPromises();
    expect(axios.get).toHaveBeenCalledTimes(1);
    expect(normalized(preview.get('.MarkdownPanel').html())).toBe(normalized(published.get('.MarkdownPanel').html()));
    expect(preview.get('.header-image').attributes('src')).toBe('/Posts/Images/cover.png');
    expect(preview.find('.katex').exists()).toBe(true);
    expect(preview.find('table').exists()).toBe(true);
    expect(preview.find('code.language-javascript').exists()).toBe(true);
    expect(preview.find('carouselblock').exists()).toBe(true);
    expect(preview.get('.mermaid svg').element.style.height).toBe('400px');
    expect(Object.keys(mocks.mount.mock.calls[0][1]).sort()).toEqual([
      'bangumiblock', 'bilibilivideoblock', 'carouselblock', 'githubrepoblock', 'steamgameblock', 'xiaohongshunoteblock'
    ]);
    for (const [container] of mocks.mount.mock.calls) expect(container.matches('article.markdown')).toBe(true);
  });

  it('uses the same image and chart viewer for published content and drafts', async () => {
    const article = render(MarkdownContent, { content: source });
    await flushPromises();
    await article.get('img').trigger('click');
    expect(article.findComponent({ name: 'ImageViewer' }).props()).toMatchObject({ visible: true, imageType: 'img' });
    await article.get('.mermaid-wrapper').trigger('click');
    expect(article.findComponent({ name: 'ImageViewer' }).props()).toMatchObject({ visible: true, imageType: 'svg' });
  });

  it('reuses the gallery description including its styles, without fetching over a draft', async () => {
    const image = { src: '/photo.jpg', alt: 'Photo', mdPath: '/photo.md' };
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, headers: { get: () => 'text/markdown' }, text: async () => source }));
    const published = render(ImageModal, { image });
    const preview = render(MarkdownPreview, { content: source, image });
    const draftModal = render(ImageModal, { content: source, image });
    await vi.advanceTimersByTimeAsync(180);
    await flushPromises();
    expect(fetch).toHaveBeenCalledTimes(1);
    const expected = normalized(published.findComponent(ImageDescription).html());
    expect(normalized(preview.findComponent(ImageDescription).html())).toBe(expected);
    expect(normalized(draftModal.findComponent(ImageDescription).html())).toBe(expected);
    await draftModal.setProps({ content: '' });
    await preview.setProps({ content: '' });
    await vi.advanceTimersByTimeAsync(180);
    expect(preview.find('.modal-description-section').exists()).toBe(false);
    expect(draftModal.findComponent(ImageDescription).exists()).toBe(false);
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('renders an empty draft without fetching saved content, and rejects stale loads', async () => {
    let finish;
    axios.get.mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
    const article = render(MarkdownPanel, { markdownUrl: '/old.md' });
    await article.setProps({ content: source });
    await flushPromises();
    finish({ data: '# Stale document' });
    await flushPromises();
    expect(article.get('.post-title').text()).toBe('同一篇文章');
    await article.setProps({ content: '' });
    await flushPromises();
    expect(article.get('article > div').text()).toBe('');
    expect(axios.get).toHaveBeenCalledTimes(1);
  });

  it('waits for pending charts, then renders only the latest draft and cleans up', async () => {
    let finish;
    mocks.charts.mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
    const article = render(MarkdownContent, { content: '```mermaid\ngraph TD; A-->B;\n```' });
    await flushPromises();
    await article.setProps({ content: 'intermediate' });
    await article.setProps({ content: '# Latest' });
    finish();
    await flushPromises();
    expect(article.get('h1').text()).toBe('Latest');
    expect(article.text()).not.toContain('intermediate');
    article.unmount();
    expect(mocks.unmount).toHaveBeenCalled();
  });
});
