// List views only need the generated metadata index, never article bodies.
export function isAnnouncement(post) {
    return (Array.isArray(post.tags) ? post.tags : [post.tags]).includes('公告');
}

export function isListedPost(path, post) {
    return !path.replace(/\\/g, '/').toLowerCase().includes('/waterfallgraph/')
        && !isAnnouncement(post)
        && String(post.title || '').trim().toLowerCase() !== 'about';
}

export function newestFirst(a, b) {
    return (Date.parse(b.date) || 0) - (Date.parse(a.date) || 0);
}

export function selectPosts(index, paths = null) {
    // null means all posts; an empty filter means no matches.
    const allowed = paths === null ? null : new Set(paths);
    return Object.entries(index)
        .filter(([path, post]) => (!allowed || allowed.has(path)) && isListedPost(path, post))
        .map(([url, post]) => ({ ...post, url }))
        .sort(newestFirst);
}
