/** Stable full-spectrum identity color, independent of order, count and theme. */
export function tagHue(tag) {
    let hash = 2166136261;
    for (const character of String(tag).normalize('NFC')) {
        hash = Math.imul(hash ^ character.codePointAt(0), 16777619);
    }
    return (hash >>> 0) % 360;
}
