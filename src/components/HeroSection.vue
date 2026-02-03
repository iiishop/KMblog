<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import config from '@/config.js';
import { themeManager } from '@/composables/useTheme';
import '../color.css';

const scrollY = ref(0);
const heroHeight = ref(0);
const particlesInitialized = ref(false);
const particleCanvas = ref(null);
let particleAnimationFrame = null;
let particles = [];

// 获取当前主题
const currentTheme = computed(() => themeManager.currentTheme.value);

// 滚动监听
const handleScroll = () => {
  scrollY.value = window.scrollY;
};

// 计算背景遮挡和模糊效果
const backgroundStyle = computed(() => {
  const maxScroll = heroHeight.value;
  const scrollProgress = Math.min(scrollY.value / maxScroll, 1);
  
  const blur = config.BackgroundImgBlur * scrollProgress;
  
  return {
    filter: `blur(${blur}px)`
  };
});

const overlayStyle = computed(() => {
  const maxScroll = heroHeight.value;
  const scrollProgress = Math.min(scrollY.value / maxScroll, 1);
  const opacity = config.BackgroundImgOpacity * scrollProgress;
  
  return {
    opacity: opacity
  };
});

// 大标题颜色提取（简化版，从背景图片色系提取）
const titleColors = ref({
  main: '#ffffff',
  shadow: '#000000'
});

// 粒子类
class Particle {
  constructor(canvasWidth, canvasHeight) {
    this.x = Math.random() * canvasWidth;
    this.y = Math.random() * canvasHeight;
    this.size = Math.random() * 4 + 2; // 增大粒子 (2-6)
    this.speedX = Math.random() * 1.5 - 0.75; // 稍快速度
    this.speedY = Math.random() * 1.5 - 0.75;
    this.opacity = Math.random() * 0.4 + 0.6; // 更高透明度 (0.6-1.0)
  }

  update(canvasWidth, canvasHeight) {
    this.x += this.speedX;
    this.y += this.speedY;

    if (this.x > canvasWidth) this.x = 0;
    if (this.x < 0) this.x = canvasWidth;
    if (this.y > canvasHeight) this.y = 0;
    if (this.y < 0) this.y = canvasHeight;
  }

  draw(ctx, color) {
    // 添加发光效果
    ctx.shadowBlur = 15;
    ctx.shadowColor = color;
    
    ctx.fillStyle = color;
    ctx.globalAlpha = this.opacity;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
    
    // 重置阴影
    ctx.shadowBlur = 0;
    ctx.globalAlpha = 1;
  }
}

onMounted(() => {
  heroHeight.value = window.innerHeight;
  window.addEventListener('scroll', handleScroll);
  
  // 提取背景图片颜色
  extractColorsFromImage();
  
  // 延迟初始化粒子效果
  setTimeout(() => {
    initializeCanvasParticles();
    animateParticles();
  }, 300);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
  if (particleAnimationFrame) {
    cancelAnimationFrame(particleAnimationFrame);
  }
});

// 初始化canvas粒子
const initializeCanvasParticles = () => {
  if (!particleCanvas.value || particlesInitialized.value) return;
  
  const canvas = particleCanvas.value;
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  
  particles = [];
  // 大幅增加粒子数量
  const particleCount = window.innerWidth < 768 ? 60 : 120;
  
  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle(canvas.width, canvas.height));
  }
  
  particlesInitialized.value = true;
};

// 动画粒子
const animateParticles = () => {
  if (!particleCanvas.value) return;
  
  const canvas = particleCanvas.value;
  const ctx = canvas.getContext('2d');
  
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // 根据主题和提取的颜色智能选择粒子颜色 - 使用更鲜艳的颜色
  let particleColor;
  let glowColor;
  const currentThemeValue = currentTheme.value;
  
  if (titleColors.value.main !== '#ffffff' && titleColors.value.main !== '#000000') {
    // 使用提取的背景色，但透明度更高
    particleColor = titleColors.value.main.includes('rgb') 
      ? titleColors.value.main.replace('rgb', 'rgba').replace(')', ', 0.9)')
      : titleColors.value.main + 'E6';
    glowColor = titleColors.value.main;
  } else {
    // 使用主题色 - 更鲜艳
    if (currentThemeValue === 'dark' || currentThemeValue === 'night') {
      particleColor = 'rgba(167, 139, 250, 0.9)'; // 紫色
      glowColor = 'rgb(167, 139, 250)';
    } else {
      particleColor = 'rgba(102, 126, 234, 0.9)'; // 蓝紫色
      glowColor = 'rgb(102, 126, 234)';
    }
  }
  
  particles.forEach(particle => {
    particle.update(canvas.width, canvas.height);
    particle.draw(ctx, particleColor);
  });
  
  // 绘制连线 - 更明显
  particles.forEach((p1, i) => {
    particles.slice(i + 1).forEach(p2 => {
      const dx = p1.x - p2.x;
      const dy = p1.y - p2.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      if (distance < 200) { // 增加连线距离
        ctx.strokeStyle = particleColor;
        ctx.lineWidth = 1.5; // 更粗的线
        ctx.globalAlpha = (1 - distance / 200) * 0.5; // 更明显的连线
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
        ctx.globalAlpha = 1;
      }
    });
  });
  
  particleAnimationFrame = requestAnimationFrame(animateParticles);
};

// 监听窗口大小变化
window.addEventListener('resize', () => {
  if (particleCanvas.value) {
    particleCanvas.value.width = window.innerWidth;
    particleCanvas.value.height = window.innerHeight;
  }
});

// 监听主题变化，重新初始化粒子颜色
watch(currentTheme, () => {
  // 主题变化时，粒子会在下一帧自动使用新的主题色
});

// 从背景图片提取颜色
const extractColorsFromImage = () => {
  const img = new Image();
  img.crossOrigin = 'Anonymous';
  img.src = config.HeroBackgroundImg || config.BackgroundImg;
  
  img.onload = () => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    
    try {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imageData.data;
      
      let r = 0, g = 0, b = 0;
      let count = 0;
      
      // 采样中心区域
      for (let i = 0; i < data.length; i += 4 * 10) {
        r += data[i];
        g += data[i + 1];
        b += data[i + 2];
        count++;
      }
      
      r = Math.floor(r / count);
      g = Math.floor(g / count);
      b = Math.floor(b / count);
      
      // 使用亮色作为主色
      const brightness = (r * 299 + g * 587 + b * 114) / 1000;
      if (brightness < 128) {
        titleColors.value.main = `rgb(${Math.min(255, r + 100)}, ${Math.min(255, g + 100)}, ${Math.min(255, b + 100)})`;
        titleColors.value.shadow = `rgb(${r}, ${g}, ${b})`;
      } else {
        titleColors.value.main = `rgb(${r}, ${g}, ${b})`;
        titleColors.value.shadow = `rgb(${Math.max(0, r - 100)}, ${Math.max(0, g - 100)}, ${Math.max(0, b - 100)})`;
      }
    } catch (e) {
      console.warn('无法提取背景图片颜色，使用默认颜色', e);
    }
  };
  
  img.onerror = () => {
    console.warn('背景图片加载失败，使用默认颜色');
  };
};
</script>

<template>
  <div class="hero-section" :data-theme="currentTheme">
    <!-- 全局背景的模糊层 -->
    <div class="hero-background-blur" :style="backgroundStyle"></div>
    
    <!-- 主题色遮挡层 -->
    <div class="hero-overlay" :style="overlayStyle"></div>
    
    <!-- Canvas粒子效果 -->
    <canvas ref="particleCanvas" class="particles-canvas"></canvas>
    
    <!-- 内容区域 -->
    <div class="hero-content">
      <!-- 大标题 -->
      <h1 
        class="hero-title" 
        :style="{ 
          color: titleColors.main,
          textShadow: `
            0 0 10px ${titleColors.shadow},
            0 0 20px ${titleColors.shadow},
            0 0 30px ${titleColors.shadow},
            0 0 40px ${titleColors.shadow},
            2px 2px 4px rgba(0,0,0,0.8),
            -2px -2px 4px rgba(255,255,255,0.3)
          `
        }"
      >
        {{ config.HeroTitle || config.BlogName }}
      </h1>
      
      <!-- 小标题（打字机效果） -->
      <div class="hero-subtitle-container">
        <TypewriterText 
          :texts="config.HeroSubtitles || [config.ShortDesc]"
          :color="titleColors.main"
        />
      </div>
    </div>
    
    <!-- 底部Panel区域 -->
    <div class="hero-bottom-panels" v-if="config.HeroPanels && config.HeroPanels.length > 0">
      <component 
        v-for="(panel, index) in config.HeroPanels" 
        :key="index"
        :is="panel"
      />
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import TypewriterText from './HeroComponents/TypewriterText.vue';

export default defineComponent({
  name: 'HeroSection',
  components: {
    TypewriterText
  }
});
</script>

<style scoped>
.hero-section {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.hero-background-blur {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-image: var(--background-image-url, none);
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  transition: filter 0.1s ease-out;
  will-change: filter;
  z-index: 0;
  pointer-events: none;
}

.hero-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: var(--theme-body-bg);
  transition: opacity 0.1s ease-out;
  will-change: opacity;
  pointer-events: none;
  z-index: 0;
}

.particles-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 75vh;
  padding: 0 2rem;
}

.hero-title {
  font-family: 'Titan One', Impact, 'Arial Black', sans-serif;
  font-size: clamp(3rem, 10vw, 8rem);
  font-weight: 900;
  margin: 0;
  padding: 0;
  text-align: center;
  letter-spacing: 0.05em;
  animation: titleFloat 3s ease-in-out infinite;
  
  /* 描边效果 */
  -webkit-text-stroke: 2px rgba(0, 0, 0, 0.3);
  paint-order: stroke fill;
  
  /* 溢出发光效果 */
  filter: drop-shadow(0 0 20px currentColor);
}

@keyframes titleFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.hero-subtitle-container {
  margin-top: 2rem;
  min-height: 3rem;
}

.hero-bottom-panels {
  position: absolute;
  bottom: 5vh;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 1400px;
  height: 20vh;
  z-index: 3;
  display: flex;
  flex-direction: row;
  gap: 1rem;
  align-items: stretch;
  padding: 0 1rem;
}

.hero-bottom-panels > * {
  flex: 1;
  min-width: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: clamp(2rem, 8vw, 4rem);
    -webkit-text-stroke: 1px rgba(0, 0, 0, 0.3);
  }
  
  .hero-bottom-panels {
    width: 95%;
    height: 15vh;
    bottom: 3vh;
    flex-direction: column;
    overflow-y: auto;
  }
  
  .hero-content {
    height: 70vh;
  }
}
</style>
