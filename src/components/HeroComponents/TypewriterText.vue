<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';

const props = defineProps({
  texts: {
    type: Array,
    required: true,
    default: () => ['']
  },
  color: {
    type: String,
    default: '#ffffff'
  },
  typingSpeed: {
    type: Number,
    default: 100
  },
  deletingSpeed: {
    type: Number,
    default: 50
  },
  pauseDuration: {
    type: Number,
    default: 2000
  }
});

const displayText = ref('');
const currentIndex = ref(0);
const isDeleting = ref(false);
const charIndex = ref(0);
let timeoutId = null;

const currentFullText = computed(() => {
  return props.texts[currentIndex.value] || '';
});

const typeWriter = () => {
  const fullText = currentFullText.value;
  
  if (!isDeleting.value) {
    // 打字阶段
    if (charIndex.value < fullText.length) {
      displayText.value = fullText.substring(0, charIndex.value + 1);
      charIndex.value++;
      timeoutId = setTimeout(typeWriter, props.typingSpeed);
    } else {
      // 打完一行，暂停
      timeoutId = setTimeout(() => {
        if (props.texts.length > 1) {
          // 如果有多行，开始删除
          isDeleting.value = true;
          typeWriter();
        } else {
          // 如果只有一行，保持显示
          return;
        }
      }, props.pauseDuration);
    }
  } else {
    // 删除阶段
    if (charIndex.value > 0) {
      charIndex.value--;
      displayText.value = fullText.substring(0, charIndex.value);
      timeoutId = setTimeout(typeWriter, props.deletingSpeed);
    } else {
      // 删除完毕，切换到下一行
      isDeleting.value = false;
      currentIndex.value = (currentIndex.value + 1) % props.texts.length;
      timeoutId = setTimeout(typeWriter, 500);
    }
  }
};

onMounted(() => {
  typeWriter();
});

onUnmounted(() => {
  if (timeoutId) {
    clearTimeout(timeoutId);
  }
});
</script>

<template>
  <div class="typewriter-text">
    <span 
      class="text-content" 
      :style="{ color: color }"
    >
      {{ displayText }}
    </span>
    <span class="cursor" :style="{ backgroundColor: color }">|</span>
  </div>
</template>

<style scoped>
.typewriter-text {
  font-size: clamp(1.2rem, 3vw, 2rem);
  font-weight: 300;
  text-align: center;
  font-family: 'Courier New', Courier, monospace;
  letter-spacing: 0.05em;
}

.text-content {
  text-shadow: 
    1px 1px 2px rgba(0,0,0,0.5),
    0 0 10px currentColor;
}

.cursor {
  display: inline-block;
  width: 2px;
  margin-left: 4px;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

@media (max-width: 768px) {
  .typewriter-text {
    font-size: clamp(1rem, 4vw, 1.5rem);
  }
}
</style>
