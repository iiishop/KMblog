export const extractNoteId = (url) => {
    if (!url) return null;
    try {
        const u = new URL(url);
        // Supports /explore/ID or /discovery/item/ID
        const path = u.pathname.split('/').filter(Boolean);
        const last = path[path.length - 1];
        if (last && /^[a-f0-9]{24}$/i.test(last)) return last;
    } catch (e) { }
    // Fallback: regex for 24 hex chars or typical XHS ID format
    const match = url.match(/[a-f0-9]{24}/i);
    return match ? match[0] : null;
};

export const parseHtmlData = (html, url) => {
    try {
        if (typeof html !== 'string') return null;
        const requestedId = extractNoteId(url);
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        if (/你访问的页面不见了|页面不存在|内容已删除|访问异常|安全验证/.test(doc.title)) return null;

        // 1. Try to find the script tag containing __INITIAL_STATE__
        const scripts = doc.querySelectorAll('script');
        let initialData = null;
        for (const script of scripts) {
            const text = script.textContent;
            if (text.includes('__INITIAL_STATE__')) {
                const state = extractState(text);
                if (state) {
                    try {
                        const cleanJson = state.replace(/"(?:\\.|[^"\\])*"|\bundefined\b/g, token => token === 'undefined' ? 'null' : token);
                        initialData = JSON.parse(cleanJson);
                        break;
                    } catch { /* Try another state script or OG metadata. */ }
                }
            }
        }

        if (initialData && initialData.note) {
            // Check noteDetailMap or direct note field
            const noteMap = initialData.note.noteDetailMap;
            // Get note from map OR fallback to direct note property
            let noteObj = null;
            if (noteMap) {
                // Never substitute a recommended note for the requested note.
                noteObj = requestedId
                    ? noteMap[requestedId]?.note || Object.values(noteMap).find(entry => (entry?.note?.noteId || entry?.note?.id) === requestedId)?.note
                    : Object.values(noteMap).length === 1 ? Object.values(noteMap)[0]?.note : null;
            }
            if (!noteObj) {
                const direct = initialData.note.note;
                if (!requestedId || (direct?.noteId || direct?.id) === requestedId) noteObj = direct;
            }

            if (noteObj && (noteObj.title || noteObj.desc)) {
                // Deep extraction of user info
                const user = noteObj.user || {};
                const nickname = user.nickname || user.nickName || user.name || 'RED.User';
                const avatar = user.avatar || user.avatarContent?.urlDefault || user.image || '';

                return {
                    title: noteObj.title || noteObj.desc?.slice(0, 24) || 'RED.Note',
                    desc: noteObj.desc || '',
                    type: noteObj.type || 'normal',
                    user: { nickname, avatar },
                    stats: {
                        likes: noteObj.interactInfo?.likedCount || noteObj.interactInfo?.likeCount || 0,
                        collects: noteObj.interactInfo?.collectedCount || noteObj.interactInfo?.collectCount || 0,
                        comments: noteObj.interactInfo?.commentCount || 0
                    },
                    cover: noteObj.imageList?.[0]?.urlDefault || noteObj.cover?.urlDefault || '',
                };
            }
        }

        // 2. Fallback: Meta Tags (OG)
        const ogTitle = doc.querySelector('meta[property="og:title"]')?.content ||
            doc.querySelector('meta[name="og:title"]')?.content ||
            doc.querySelector('title')?.textContent;

        const ogImage = doc.querySelector('meta[property="og:image"]')?.content ||
            doc.querySelector('meta[name="og:image"]')?.content;

        const ogDesc = doc.querySelector('meta[property="og:description"]')?.content ||
            doc.querySelector('meta[name="description"]')?.content;

        // Try to find user info from alternative sources in HTML
        const userNickname = doc.querySelector('.nickname')?.textContent ||
            doc.querySelector('.user-name')?.textContent ||
            doc.querySelector('meta[name="author"]')?.content || 'RED.User';

        const canonical = doc.querySelector('meta[property="og:url"]')?.content || doc.querySelector('link[rel="canonical"]')?.href;
        if (requestedId && canonical && extractNoteId(canonical) !== requestedId) return null;
        if (requestedId && initialData?.note?.noteDetailMap && !noteObjMatches(initialData.note.noteDetailMap, requestedId)) return null;
        if (ogTitle && ogImage) {
            return {
                title: ogTitle,
                desc: ogDesc,
                type: 'normal',
                user: { nickname: userNickname, avatar: '' },
                stats: { likes: 0, collects: 0 },
                cover: ogImage
            };
        }
    } catch (e) {
        // Invalid proxy HTML should fall through to the next provider.
    }
    return null;
};


function noteObjMatches(map, id) {
    return Boolean(map[id]?.note || Object.values(map).some(entry => (entry?.note?.noteId || entry?.note?.id) === id));
}

// Read the assigned object without executing scripts or mistaking braces inside text for JSON boundaries.
function extractState(script) {
    const match = /(?:window\.)?__INITIAL_STATE__\s*=\s*\{/.exec(script);
    if (!match) return null;
    const start = match.index + match[0].length - 1;
    let depth = 0;
    let quoted = false;
    let escaped = false;
    for (let i = start; i < script.length; i++) {
        const char = script[i];
        if (quoted) {
            if (escaped) escaped = false;
            else if (char === '\\') escaped = true;
            else if (char === '"') quoted = false;
        } else if (char === '"') quoted = true;
        else if (char === '{') depth++;
        else if (char === '}' && --depth === 0) return script.slice(start, i + 1);
    }
    return null;
}
