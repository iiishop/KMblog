import { mount, flushPromises } from '@vue/test-utils';
import { afterEach, describe, expect, it, vi } from 'vitest';
import axios from 'axios';
vi.mock('axios', () => ({ default: { get: vi.fn() } }));
vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }) }));
import Post from './Post.vue';

let wrapper;
afterEach(() => wrapper?.unmount());
const render = props => wrapper = mount(Post, { props, global: { stubs: {
    RouterLink: { template: '<a><slot /></a>' }, Tag: { props: ['tagname'], template: '<span>{{ tagname }}</span>' }, IconDate: true, IconCategory: true
} } });

describe('article card draft preview', () => {
    it('renders and updates draft fields without fetching the saved article', async () => {
        render({ markdownUrl: '/Posts/Markdowns/example.md', previewMetadata: { title: '初稿', pre: '首页摘要', tags: ['Vue'], categories: ['技术'], date: new Date('2026-10-22T00:00:00Z') } });
        expect(wrapper.get('.title-text').text()).toBe('初稿');
        expect(wrapper.get('.pre-text').text()).toBe('首页摘要');
        expect(wrapper.text()).toContain('2026-10-22');
        expect(wrapper.text()).toContain('技术');
        await wrapper.setProps({ previewMetadata: { title: '新标题', pre: '修改后的摘要', tags: ['Markdown'] } });
        expect(wrapper.get('.title-text').text()).toBe('新标题');
        expect(wrapper.get('.pre-text').text()).toBe('修改后的摘要');
        expect(axios.get).not.toHaveBeenCalled();
    });
    it('updates and removes a draft cover without remounting', async () => {
        render({ previewMetadata: { title: 'Draft' }, imageUrl: '/Posts/Images/one.png' });
        expect(wrapper.get('.image-panel img').attributes('src')).toBe('/Posts/Images/one.png');
        await wrapper.setProps({ imageUrl: '/Posts/Images/two.png' });
        expect(wrapper.get('.image-panel img').attributes('src')).toBe('/Posts/Images/two.png');
        await wrapper.setProps({ imageUrl: '' });
        expect(wrapper.find('.image-panel').exists()).toBe(false);
    });
    it('continues to fetch metadata for normal homepage cards', async () => {
        axios.get.mockResolvedValueOnce({ data: '---\ntitle: Published\npre: Saved summary\n---\nBody' });
        render({ markdownUrl: 'https://example.test/article.md' });
        await flushPromises();
        expect(axios.get).toHaveBeenCalledWith('https://example.test/article.md');
        expect(wrapper.get('.title-text').text()).toBe('Published');
        expect(wrapper.get('.pre-text').text()).toBe('Saved summary');
    });
});
