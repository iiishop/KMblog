import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
const { get } = vi.hoisted(() => ({ get: vi.fn() }));
vi.mock('axios', () => ({ default: { create: () => ({ get }), isCancel: error => error.code === 'ERR_CANCELED' } }));
import { fetchBlockData, parseBilibili } from './blockProxy';
import { parseHtmlData } from './xiaohongshuData';
import Bilibili from '../components/MarkdownPanelComps/BilibiliVideoBlock.vue';
import Xiaohongshu from '../components/MarkdownPanelComps/XiaohongshuNoteBlock.vue';

const id = '69765621000000000e00c91e';
const noteUrl = `https://www.xiaohongshu.com/explore/${id}?xsec_token=a+b/=&xsec_source=pc_feed`;
const noteHtml = title => `<script>window.__INITIAL_STATE__=${JSON.stringify({ note: { noteDetailMap: { other: { note: { title: 'wrong' } }, [id]: { note: { title, desc: 'undefined remains }; intact', user: {}, extra: 'placeholder' } } } } }).replace('"placeholder"', 'undefined')};window.after=true;</script>`;
const video = title => ({ code: 0, data: { title, owner: { mid: 123, name: 'Creator' }, stat: {}, duration: 10, pubdate: 1 } });
beforeEach(() => { get.mockReset(); });

describe('existing proxy transport', () => {
    it('falls back after timeout and HTTP-200 upstream errors, preserving full query', async () => {
        get.mockRejectedValueOnce({ code: 'ECONNABORTED' })
            .mockResolvedValueOnce({ data: { code: -404 } })
            .mockResolvedValueOnce({ data: video('ok') });
        expect((await fetchBlockData(noteUrl, { parse: parseBilibili })).title).toBe('ok');
        expect(get).toHaveBeenCalledTimes(3);
        for (const [url, options] of get.mock.calls) {
            expect(decodeURIComponent(url.split(/url=|quest=/)[1])).toBe(noteUrl);
            expect(options.timeout).toBe(8000);
        }
    });
    it('reports actual provider failures rather than a fabricated 404', async () => {
        get.mockRejectedValue({ response: { status: 401 } });
        await expect(fetchBlockData(noteUrl, { parse: parseBilibili })).rejects.toThrow('代理 HTTP 401');
    });
    it('stops trying providers after cancellation', async () => {
        const controller = new AbortController();
        get.mockImplementationOnce(() => { controller.abort(); return Promise.reject({ code: 'ERR_CANCELED' }); });
        await expect(fetchBlockData(noteUrl, { signal: controller.signal, parse: parseBilibili })).rejects.toBeDefined();
        expect(get).toHaveBeenCalledTimes(1);
    });
});

describe('Xiaohongshu parsing', () => {
    it('selects requested note and preserves undefined and braces inside strings', () => {
        const note = parseHtmlData(noteHtml('Requested'), noteUrl);
        expect(note.title).toBe('Requested');
        expect(note.desc).toBe('undefined remains }; intact');
    });
    it('does not render unavailable-page metadata as a note', () => {
        expect(parseHtmlData('<title>小红书 - 你访问的页面不见了</title><meta property="og:image" content="logo.jpg">', noteUrl)).toBeNull();
    });
    it('rejects another note even when generic OG tags are present', () => {
        expect(parseHtmlData(noteHtml('other').replaceAll(id, 'aaaaaaaaaaaaaaaaaaaaaaaa') + '<meta property="og:title" content="wrong"><meta property="og:image" content="wrong.jpg">', noteUrl)).toBeNull();
    });
    it('retains OG-only fallback', () => {
        expect(parseHtmlData('<meta property="og:title" content="Note"><meta property="og:image" content="cover.jpg">', noteUrl)?.title).toBe('Note');
    });
});

describe('shared cards lifecycle', () => {
    it('shows video before optional creator lookup completes; aborts on unmount', async () => {
        get.mockResolvedValueOnce({ data: video('Loaded video') }).mockImplementation(() => new Promise(() => {}));
        const wrapper = mount(Bilibili, { props: { videourl: 'https://www.bilibili.com/video/BV1fthDeyE6V' } });
        await flushPromises();
        expect(wrapper.text()).toContain('Loaded video');
        expect(wrapper.classes()).not.toContain('is-loading');
        const signal = get.mock.calls[1][1].signal;
        wrapper.unmount();
        expect(signal.aborted).toBe(true);
    });
    it('invalid empty props finish loading and offer retry', async () => {
        for (const Component of [Bilibili, Xiaohongshu]) {
            const wrapper = mount(Component);
            await flushPromises();
            expect(wrapper.classes()).toContain('is-error');
            expect(wrapper.classes()).not.toContain('is-loading');
            expect(wrapper.find('button').text()).toBe('重试');
            wrapper.unmount();
        }
        expect(get).not.toHaveBeenCalled();
    });
    it('ignores stale responses after changing a note link', async () => {
        let resolveOld;
        get.mockImplementationOnce(() => new Promise(resolve => { resolveOld = resolve; }))
            .mockResolvedValueOnce({ data: noteHtml('new note') });
        const wrapper = mount(Xiaohongshu, { props: { noteurl: noteUrl } });
        const oldSignal = get.mock.calls[0][1].signal;
        await wrapper.setProps({ noteurl: noteUrl + '&new=1' });
        await flushPromises();
        resolveOld({ data: noteHtml('stale note') });
        await flushPromises();
        expect(oldSignal.aborted).toBe(true);
        expect(wrapper.text()).toContain('new note');
        expect(wrapper.text()).not.toContain('stale note');
        wrapper.unmount();
    });
    it('retries after all providers fail', async () => {
        get.mockRejectedValue({ response: { status: 403 } });
        const wrapper = mount(Xiaohongshu, { props: { noteurl: noteUrl } });
        await flushPromises();
        expect(wrapper.text()).toContain('代理 HTTP 403');
        get.mockResolvedValue({ data: noteHtml('recovered') });
        await wrapper.find('button').trigger('click');
        await flushPromises();
        expect(wrapper.text()).toContain('recovered');
        wrapper.unmount();
    });
});
