<template>
    <div class="crypto-unlock">
        <div class="unlock-card">
            <div class="lock-icon">🔒</div>
            <h2>此文章需要密码访问</h2>
            <p class="hint">这是一篇加密文章，请输入密码以查看内容</p>

            <div class="password-input-group">
                <input v-model="password" type="password" placeholder="请输入密码" @keyup.enter="decrypt"
                    :disabled="isDecrypting" class="password-input" />
                <button @click="decrypt" :disabled="isDecrypting || !password" class="unlock-button">
                    {{ isDecrypting ? '解密中...' : '解锁' }}
                </button>
            </div>

            <div v-if="error" class="error-message">
                {{ error }}
            </div>

            <div v-if="isDecrypting" class="progress-bar">
                <div class="progress-fill"></div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { decryptArticle } from '@/utils/crypto';

const props = defineProps({
    encryptedUrl: {
        type: String,
        required: true
    }
});

const emit = defineEmits(['unlocked']);

const password = ref('');
const isDecrypting = ref(false);
const error = ref('');

const decrypt = async () => {
    if (!password.value) {
        error.value = '请输入密码';
        return;
    }

    isDecrypting.value = true;
    error.value = '';

    try {
        // 获取加密文件内容（现在是文本格式，包含 metadata 和加密的 body）
        const response = await fetch(props.encryptedUrl);
        if (!response.ok) {
            throw new Error('无法加载加密文章');
        }

        const encryptedContent = await response.text();

        // 解密文章（会返回完整的 markdown：metadata + body）
        const decryptedText = await decryptArticle(encryptedContent, password.value);

        // 解密成功，触发事件
        emit('unlocked', decryptedText);

    } catch (err) {
        console.error('解密失败:', err);
        if (err.message.includes('authentication') || err.message.includes('密码错误')) {
            error.value = '密码错误，请重试';
        } else {
            error.value = `解密失败: ${err.message}`;
        }
        password.value = '';
    } finally {
        isDecrypting.value = false;
    }
};
</script>

<style scoped>
.crypto-unlock {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 60vh;
    padding: 2rem;
}

.unlock-card {
    background: white;
    border-radius: 1rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 3rem;
    max-width: 500px;
    width: 100%;
    text-align: center;
}

.lock-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {

    0%,
    100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }
}

h2 {
    color: #333;
    margin-bottom: 0.5rem;
    font-size: 1.5rem;
}

.hint {
    color: #666;
    margin-bottom: 2rem;
    font-size: 0.95rem;
}

.password-input-group {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.password-input {
    flex: 1;
    padding: 0.75rem 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 0.5rem;
    font-size: 1rem;
    transition: border-color 0.3s;
}

.password-input:focus {
    outline: none;
    border-color: #4CAF50;
}

.password-input:disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
}

.unlock-button {
    padding: 0.75rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 0.5rem;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}

.unlock-button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.unlock-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.error-message {
    color: #f44336;
    padding: 0.75rem;
    background: #ffebee;
    border-radius: 0.5rem;
    font-size: 0.9rem;
    margin-top: 1rem;
}

.progress-bar {
    height: 4px;
    background: #e0e0e0;
    border-radius: 2px;
    overflow: hidden;
    margin-top: 1rem;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    animation: progress 1.5s ease-in-out infinite;
}

@keyframes progress {
    0% {
        width: 0%;
    }

    50% {
        width: 70%;
    }

    100% {
        width: 100%;
    }
}
</style>
