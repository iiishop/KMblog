/**
 * 前端加密工具 - AES-GCM 解密
 * 与后端 Python 加密逻辑对应
 */

/**
 * 将密码派生为 AES 密钥
 * 使用 PBKDF2-HMAC-SHA256，100,000 次迭代
 */
async function deriveKey(password, salt) {
    // 将密码转换为 ArrayBuffer
    const encoder = new TextEncoder();
    const passwordBuffer = encoder.encode(password);

    // 导入密码作为 CryptoKey
    const baseKey = await crypto.subtle.importKey(
        'raw',
        passwordBuffer,
        'PBKDF2',
        false,
        ['deriveBits', 'deriveKey']
    );

    // 使用 PBKDF2 派生 AES 密钥
    const key = await crypto.subtle.deriveKey(
        {
            name: 'PBKDF2',
            salt: salt,
            iterations: 100000,
            hash: 'SHA-256'
        },
        baseKey,
        {
            name: 'AES-GCM',
            length: 256
        },
        false,
        ['decrypt']
    );

    return key;
}

/**
 * Base64 字符串转 Uint8Array（兼容所有字符）
 * @param {string} base64String - Base64 编码的字符串
 * @returns {Uint8Array} - 解码后的字节数组
 */
function base64ToUint8Array(base64String) {
    // 移除可能的空白字符
    base64String = base64String.replace(/\s/g, '');

    try {
        // 方法1: 尝试使用标准 atob
        const binaryString = atob(base64String);
        const bytes = new Uint8Array(binaryString.length);

        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        return bytes;
    } catch (e) {
        console.warn('atob() 失败，尝试使用备用方法:', e);

        // 方法2: 使用 fetch + data URL（兼容性更好）
        try {
            // 将 base64 转换为 data URL
            const dataUrl = `data:application/octet-stream;base64,${base64String}`;

            // 同步获取并转换（使用 XMLHttpRequest）
            const xhr = new XMLHttpRequest();
            xhr.open('GET', dataUrl, false); // 同步请求
            xhr.overrideMimeType('text/plain; charset=x-user-defined');
            xhr.send();

            const binaryString = xhr.responseText;
            const bytes = new Uint8Array(binaryString.length);

            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i) & 0xff;
            }

            return bytes;
        } catch (e2) {
            console.error('备用方法也失败:', e2);

            // 方法3: 手动解码 Base64（最后的兜底方案）
            return manualBase64Decode(base64String);
        }
    }
}

/**
 * 手动解码 Base64（兜底方案）
 */
function manualBase64Decode(base64String) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    const lookup = new Uint8Array(256);
    for (let i = 0; i < chars.length; i++) {
        lookup[chars.charCodeAt(i)] = i;
    }

    let bufferLength = base64String.length * 0.75;
    if (base64String[base64String.length - 1] === '=') {
        bufferLength--;
        if (base64String[base64String.length - 2] === '=') {
            bufferLength--;
        }
    }

    const bytes = new Uint8Array(bufferLength);
    let p = 0;

    for (let i = 0; i < base64String.length; i += 4) {
        const encoded1 = lookup[base64String.charCodeAt(i)];
        const encoded2 = lookup[base64String.charCodeAt(i + 1)];
        const encoded3 = lookup[base64String.charCodeAt(i + 2)];
        const encoded4 = lookup[base64String.charCodeAt(i + 3)];

        bytes[p++] = (encoded1 << 2) | (encoded2 >> 4);
        bytes[p++] = ((encoded2 & 15) << 4) | (encoded3 >> 2);
        bytes[p++] = ((encoded3 & 3) << 6) | (encoded4 & 63);
    }

    return bytes;
}

/**
 * 解密文章内容（只解密 body 部分，保留 metadata）
 * @param {string} encryptedContent - 加密的文章内容（包含 metadata 明文和加密的 body）
 * @param {string} password - 用户输入的密码
 * @returns {Promise<string>} - 完整的解密后的 markdown（metadata + body）
 */
export async function decryptArticle(encryptedContent, password) {
    try {
        console.log('[Crypto] 开始解密，原始内容长度:', encryptedContent.length);

        // 先统一换行符为 \n（处理 Windows 的 \r\n）
        const normalizedContent = encryptedContent.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

        // 分离 metadata 和加密数据
        // 支持 --- 前后可能有空白的情况
        const metadataRegex = /^---\n([\s\S]*?)\n---\n/;
        const match = normalizedContent.match(metadataRegex);

        let metadata = '';
        let encryptedPart = normalizedContent;

        if (match) {
            metadata = match[0]; // 包含完整的 ---metadata---
            encryptedPart = normalizedContent.substring(match[0].length);
            console.log('[Crypto] 已提取 metadata，剩余内容长度:', encryptedPart.length);
        } else {
            console.warn('[Crypto] 未能提取 metadata，将处理整个内容');
        }

        // 移除加密标记注释
        encryptedPart = encryptedPart.replace(/<!--\s*ENCRYPTED\s*CONTENT\s*-->/gi, '');

        // 只保留 Base64 有效字符（A-Z, a-z, 0-9, +, /, =）
        // 移除所有其他字符（包括换行、空格等）
        encryptedPart = encryptedPart.replace(/[^A-Za-z0-9+/=]/g, '');

        console.log('[Crypto] 清理后的 Base64 字符串长度:', encryptedPart.length);
        console.log('[Crypto] Base64 前50个字符:', encryptedPart.substring(0, 50));

        if (!encryptedPart || encryptedPart.length < 40) {
            throw new Error('加密数据为空或过短');
        }

        // Base64 解码加密数据（使用安全的方法）
        const encryptedData = base64ToUint8Array(encryptedPart);

        console.log('[Crypto] 解码后的字节数组长度:', encryptedData.length);

        if (encryptedData.length < 28) { // 16 (salt) + 12 (nonce) = 28
            throw new Error(`加密数据格式无效，长度仅 ${encryptedData.length} 字节，需要至少 28 字节`);
        }

        // 提取 Salt (前16字节)
        const salt = encryptedData.slice(0, 16);

        // 提取 Nonce (接下来12字节)
        const nonce = encryptedData.slice(16, 28);

        // 提取密文和认证标签 (剩余部分)
        const ciphertext = encryptedData.slice(28);

        console.log('[Crypto] Salt:', Array.from(salt.slice(0, 4)).map(b => b.toString(16).padStart(2, '0')).join(''));
        console.log('[Crypto] Nonce:', Array.from(nonce.slice(0, 4)).map(b => b.toString(16).padStart(2, '0')).join(''));
        console.log('[Crypto] Ciphertext 长度:', ciphertext.length);

        // 派生密钥
        const key = await deriveKey(password, salt);

        // 使用 AES-GCM 解密
        const decryptedBuffer = await crypto.subtle.decrypt(
            {
                name: 'AES-GCM',
                iv: nonce,
                tagLength: 128 // GCM 认证标签长度为 128 位
            },
            key,
            ciphertext
        );

        // 将解密后的 ArrayBuffer 转换为字符串
        const decoder = new TextDecoder('utf-8');
        const bodyText = decoder.decode(decryptedBuffer);

        // 组合 metadata 和解密后的 body
        const fullMarkdown = metadata + bodyText;

        return fullMarkdown;

    } catch (error) {
        console.error('解密错误:', error);

        // 如果是认证失败，说明密码错误
        if (error.name === 'OperationError') {
            throw new Error('密码错误或文件已损坏 (authentication failed)');
        }

        throw error;
    }
}

/**
 * 检查文章是否需要加密
 * @param {string} articlePath - 文章路径
 * @param {string} cryptoTag - 加密标签
 * @param {Object} tagsData - Tags.json 数据
 * @returns {boolean} - 是否需要解密
 */
export function isArticleEncrypted(articlePath, cryptoTag, tagsData) {
    // 检查 Tags.json 中是否存在加密标签
    if (!tagsData[cryptoTag]) {
        return false;
    }

    // 检查文章是否在加密标签的列表中
    return tagsData[cryptoTag].includes(articlePath);
}
