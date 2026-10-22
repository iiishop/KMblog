import axios from 'axios';

// Keep the existing browser-side proxy strategy; validate each response before accepting it.
const client = axios.create({ withCredentials: false });
const proxies = [
    ['AllOrigins', 'https://api.allorigins.win/raw?url='],
    ['CorsProxy', 'https://corsproxy.io/?url='],
    ['CodeTabs', 'https://api.codetabs.com/v1/proxy?quest='],
];

export async function fetchBlockData(target, { signal, parse, timeout = 8000 }) {
    const failures = [];
    for (const [name, prefix] of proxies) {
        if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
        try {
            const response = await client.get(prefix + encodeURIComponent(target), {
                signal, timeout,
                headers: { 'X-Auth-Token': null, Authorization: null },
            });
            if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
            const result = parse(response.data);
            if (!result) throw new Error('未获取到有效内容');
            return result;
        } catch (error) {
            if (signal?.aborted || axios.isCancel(error) || error.name === 'AbortError') throw error;
            const status = error.response?.status;
            const reason = status ? `代理 HTTP ${status}`
                : ['ECONNABORTED', 'ETIMEDOUT'].includes(error.code) ? '请求超时'
                : error.isAxiosError ? '网络或跨域请求失败' : error.message;
            failures.push(`${name}：${reason}`);
        }
    }
    throw new Error(failures.join('；'));
}

export function parseBilibili(data) {
    if (typeof data === 'string') {
        try { data = JSON.parse(data); } catch { throw new Error('代理未返回 Bilibili 数据'); }
    }
    if (data?.code !== 0 || !data.data) {
        throw new Error(data?.code != null ? `Bilibili 接口错误（${data.code}）` : '代理未返回 Bilibili 数据');
    }
    return data.data;
}
