<template>
    <BaseLayout :showTipList="false" :showInfoList="false">
        <template #main>
            <div class="about-page" :style="cssVars">
                <!-- Parallax Hero Section -->
                <section class="hero-section" ref="heroSection">
                    <canvas ref="particleCanvas" class="particle-canvas"></canvas>
                    <div class="hero-grid">
                        <div class="grid-line" v-for="i in 12" :key="'line-' + i"></div>
                    </div>

                    <div class="hero-content">
                        <div class="hero-layout">
                            <!-- Left: Large Title -->
                            <div class="hero-text">
                                <div class="eyebrow">About</div>
                                <h1 class="display-title">
                                    {{ aboutData.name || 'Creative Developer' }}
                                </h1>
                                <p class="hero-description">
                                    {{ aboutData.subtitle || 'Building digital experiences that inspire and engage' }}
                                </p>

                                <!-- Social Links -->
                                <div class="social-links" v-if="aboutData.socials && aboutData.socials.length > 0">
                                    <a v-for="social in aboutData.socials" :key="social.name" :href="social.url"
                                        class="social-link" target="_blank" rel="noopener noreferrer"
                                        :style="{ '--social-index': aboutData.socials.indexOf(social) }">
                                        <span class="link-bg"></span>
                                        <span class="link-text">{{ social.name }}</span>
                                    </a>
                                </div>
                            </div>

                            <!-- Right: Avatar with Ornament -->
                            <div class="hero-visual">
                                <div class="avatar-ornament">
                                    <div class="ornament-ring ring-1"></div>
                                    <div class="ornament-ring ring-2"></div>
                                    <div class="ornament-ring ring-3"></div>
                                </div>
                                <div class="avatar-wrapper">
                                    <img v-if="aboutData.avatar" :src="aboutData.avatar" alt="Avatar"
                                        class="avatar-image" />
                                    <div v-else class="avatar-placeholder">
                                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                            <circle cx="12" cy="7" r="4"></circle>
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Scroll Indicator -->
                    <div class="scroll-indicator">
                        <div class="scroll-line"></div>
                        <span class="scroll-text">Scroll</span>
                    </div>
                </section>

                <!-- Content Grid -->
                <section class="content-section">
                    <!-- Biography Section -->
                    <div class="section-wrapper bio-section">
                        <div class="section-grid">
                            <div class="section-label">
                                <span class="label-number">01</span>
                                <span class="label-text">Biography</span>
                            </div>
                            <div class="section-content">
                                <div v-if="aboutData.content" class="prose-content" v-html="aboutData.content">
                                </div>
                                <div v-else class="prose-content">
                                    <p>欢迎来到我的数字空间。这里是我记录思考、分享创作、探索技术的地方。</p>
                                    <p>我相信好的设计不仅仅是视觉上的美观，更是功能与体验的完美融合。通过这个博客，我希望能与你分享我在创作过程中的发现与思考。</p>
                                    <p>每一次创作都是一次对话，每一个作品都承载着故事。让我们一起探索设计与技术的无限可能。</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Skills Section -->
                    <div class="section-wrapper skills-section" v-if="aboutData.skills && aboutData.skills.length > 0">
                        <div class="section-grid">
                            <div class="section-label">
                                <span class="label-number">02</span>
                                <span class="label-text">Expertise</span>
                            </div>
                            <div class="section-content">
                                <div class="skills-marquee">
                                    <div class="marquee-content" ref="marqueeContent">
                                        <div v-for="(skill, index) in [...aboutData.skills, ...aboutData.skills]"
                                            :key="'skill-' + index" class="skill-tag">
                                            {{ skill.name }}
                                        </div>
                                    </div>
                                </div>
                                <div class="skills-grid-modern">
                                    <div v-for="(skill, index) in aboutData.skills" :key="index" class="skill-card"
                                        :style="{ '--card-index': index }">
                                        <div class="skill-number">{{ String(index + 1).padStart(2, '0') }}</div>
                                        <div class="skill-name">{{ skill.name }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Timeline Section -->
                    <div class="section-wrapper timeline-section"
                        v-if="aboutData.timeline && aboutData.timeline.length > 0">
                        <div class="section-grid">
                            <div class="section-label">
                                <span class="label-number">03</span>
                                <span class="label-text">Journey</span>
                            </div>
                            <div class="section-content">
                                <div class="timeline-modern">
                                    <div v-for="(item, index) in aboutData.timeline" :key="index" class="timeline-entry"
                                        :style="{ '--entry-index': index }">
                                        <div class="entry-year">{{ item.date }}</div>
                                        <div class="entry-divider"></div>
                                        <div class="entry-details">
                                            <h3 class="entry-title">{{ item.title }}</h3>
                                            <p class="entry-description">{{ item.description }}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Contact Section -->
                    <div class="section-wrapper contact-section">
                        <div class="section-grid">
                            <div class="section-label">
                                <span class="label-number">04</span>
                                <span class="label-text">Contact</span>
                            </div>
                            <div class="section-content">
                                <div class="contact-card-modern">
                                    <p class="contact-intro">
                                        {{ aboutData.contactText || '让我们一起创造些什么。' }}
                                    </p>
                                    <a v-if="aboutData.email" :href="'mailto:' + aboutData.email" class="contact-cta">
                                        <span class="cta-text">{{ aboutData.email }}</span>
                                        <span class="cta-arrow">→</span>
                                    </a>
                                    <div v-else class="contact-cta-placeholder">
                                        <span class="cta-text">通过社交媒体联系我</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Footer Spacer -->
                    <div class="footer-spacer"></div>
                </section>
            </div>
        </template>
    </BaseLayout>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import axios from 'axios';
import fm from 'front-matter';
import md from '@/components/MarkdownPanelComps/MarkdownRenender.js';
import BaseLayout from './BaseLayout.vue';
import globalVar from '@/globalVar';
import { parseMarkdownMetadata } from '@/utils';

const aboutData = ref({
    name: '',
    subtitle: '',
    avatar: '',
    content: '',
    email: '',
    contactText: '',
    socials: [],
    skills: [],
    timeline: []
});

// Canvas particles
const particleCanvas = ref(null);
const heroSection = ref(null);
const marqueeContent = ref(null);
let animationFrame = null;
let particles = [];

// 动态颜色系统
const primaryColor = ref({ h: 210, s: 100, l: 50 }); // 明亮的蓝色
const accentColor = ref({ h: 160, s: 100, l: 45 }); // 青绿色

const cssVars = computed(() => {
    const { h, s, l } = primaryColor.value;
    const { h: h2, s: s2, l: l2 } = accentColor.value;

    return {
        '--primary-hue': h,
        '--primary-sat': `${s}%`,
        '--primary-light': `${l}%`,
        '--accent-hue': h2,
        '--accent-sat': `${s2}%`,
        '--accent-light': `${l2}%`,
        '--primary-color': `hsl(${h}, ${s}%, ${l}%)`,
        '--accent-color': `hsl(${h2}, ${s2}%, ${l2}%)`,
    };
});

// Particle system
class Particle {
    constructor(canvas) {
        this.canvas = canvas;
        this.reset();
    }

    reset() {
        this.x = Math.random() * this.canvas.width;
        this.y = Math.random() * this.canvas.height;
        this.size = Math.random() * 2 + 1;
        this.speedX = (Math.random() - 0.5) * 0.5;
        this.speedY = (Math.random() - 0.5) * 0.5;
        this.opacity = Math.random() * 0.5 + 0.2;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x < 0 || this.x > this.canvas.width) this.speedX *= -1;
        if (this.y < 0 || this.y > this.canvas.height) this.speedY *= -1;
    }

    draw(ctx) {
        ctx.fillStyle = `rgba(100, 150, 255, ${this.opacity})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

const initParticles = () => {
    if (!particleCanvas.value) return;

    const canvas = particleCanvas.value;
    const ctx = canvas.getContext('2d');

    // Set canvas size
    const resizeCanvas = () => {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Create particles
    const particleCount = Math.floor((canvas.width * canvas.height) / 15000);
    particles = Array.from({ length: particleCount }, () => new Particle(canvas));

    // Animation loop
    const animate = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(particle => {
            particle.update();
            particle.draw(ctx);
        });

        // Draw connections
        particles.forEach((p1, i) => {
            particles.slice(i + 1).forEach(p2 => {
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 120) {
                    ctx.strokeStyle = `rgba(100, 150, 255, ${0.15 * (1 - distance / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            });
        });

        animationFrame = requestAnimationFrame(animate);
    };
    animate();
};

// 查找 About 文章
const findAboutArticle = async () => {
    try {
        // 遍历所有文章，找到 title 为 About 的文章
        const markdowns = globalVar.markdowns;

        if (!markdowns || Object.keys(markdowns).length === 0) {
            console.log('No markdowns found in globalVar');
            loadDefaultContent();
            return;
        }

        let aboutArticleUrl = null;

        // 遍历所有文章URL，加载并检查 title
        for (const url in markdowns) {
            try {
                const response = await axios.get(url);
                const markdown = response.data;
                const { meta } = await parseMarkdownMetadata(markdown);

                if (meta.title && meta.title.toLowerCase() === 'about') {
                    aboutArticleUrl = url;
                    break;
                }
            } catch (err) {
                console.error(`Failed to check article ${url}:`, err);
                continue;
            }
        }

        if (aboutArticleUrl) {
            // 加载文章内容
            const response = await axios.get(aboutArticleUrl);
            const markdown = response.data;
            const { body } = fm(markdown);
            const { meta } = await parseMarkdownMetadata(markdown);

            // 解析内容
            aboutData.value.name = meta.name || meta.title || 'About Me';
            aboutData.value.subtitle = meta.subtitle || meta.description || '';
            aboutData.value.avatar = meta.avatar ? `/Posts/Images/${meta.avatar}` : '';
            aboutData.value.content = md.render(body);
            aboutData.value.email = meta.email || '';
            aboutData.value.contactText = meta.contactText || '';
            aboutData.value.socials = meta.socials || [];
            aboutData.value.skills = meta.skills || [];
            aboutData.value.timeline = meta.timeline || [];

            console.log('About page loaded successfully:', meta.title);
        } else {
            // 使用默认内容
            console.log('No About article found, using default content');
            loadDefaultContent();
        }
    } catch (error) {
        console.error('Error loading about article:', error);
        loadDefaultContent();
    }
};

// 加载默认内容
const loadDefaultContent = () => {
    aboutData.value = {
        name: 'Creative Developer',
        subtitle: 'Building digital experiences that inspire',
        avatar: '',
        content: '',
        email: 'hello@example.com',
        contactText: '让我们一起创造些什么。',
        socials: [
            { name: 'GitHub', url: '#' },
            { name: 'Twitter', url: '#' },
            { name: 'Email', url: 'mailto:hello@example.com' }
        ],
        skills: [
            { name: 'Frontend Development' },
            { name: 'UI/UX Design' },
            { name: 'Creative Coding' },
            { name: 'Visual Design' },
            { name: 'Typography' },
            { name: 'Motion Graphics' }
        ],
        timeline: []
    };
};

onMounted(async () => {
    await findAboutArticle();
    await nextTick();
    initParticles();
});

onUnmounted(() => {
    if (animationFrame) {
        cancelAnimationFrame(animationFrame);
    }
});
</script>


<style scoped>
/* === CSS Variables === */
:root {
    --spacing-unit: 1rem;
    --max-width: 1400px;
}

/* === Typography Imports === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:wght@400;500;600;700;800;900&display=swap');

/* === Global Reset === */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.about-page {
    width: 100%;
    min-height: 100vh;
    background: var(--theme-body-bg);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: var(--theme-body-text);
    overflow-x: hidden;
}

/* === Hero Section === */
.hero-section {
    position: relative;
    width: 100%;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--theme-panel-bg);
    overflow: hidden;
}

.particle-canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
}

.hero-grid {
    position: absolute;
    inset: 0;
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 0;
    opacity: 0.03;
    z-index: 2;
}

.grid-line {
    border-right: 1px solid var(--theme-panel-text);
}

.hero-content {
    position: relative;
    z-index: 3;
    width: 100%;
    max-width: var(--max-width);
    padding: 0 4rem;
}

.hero-layout {
    display: grid;
    grid-template-columns: 1.2fr 0.8fr;
    gap: 6rem;
    align-items: center;
}

.hero-text {
    color: var(--theme-body-text);
}

.eyebrow {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--primary-color);
    margin-bottom: 1.5rem;
    opacity: 0;
    animation: fadeSlideUp 0.8s ease-out 0.2s forwards;
}

.display-title {
    font-family: 'Playfair Display', 'Noto Serif SC', Georgia, serif;
    font-size: clamp(3rem, 8vw, 6rem);
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 1.5rem;
    letter-spacing: -0.02em;
    opacity: 0;
    animation: fadeSlideUp 0.8s ease-out 0.4s forwards;
}

.hero-description {
    font-size: 1.125rem;
    line-height: 1.8;
    color: var(--theme-panel-text);
    opacity: 0.7;
    max-width: 500px;
    margin-bottom: 3rem;
    animation: fadeSlideUp 0.8s ease-out 0.6s forwards;
}

@keyframes fadeSlideUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* === Social Links === */
.social-links {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}

.social-link {
    position: relative;
    display: inline-block;
    padding: 0.75rem 1.5rem;
    color: var(--theme-body-text);
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    overflow: hidden;
    opacity: 0;
    animation: fadeSlideUp 0.6s ease-out calc(0.8s + var(--social-index) * 0.1s) forwards;
}

.link-bg {
    position: absolute;
    inset: 0;
    background: var(--theme-panel-bg);
    opacity: 0.5;
    border: 1px solid var(--theme-panel-border);
    transition: all 0.3s ease;
}

.social-link:hover .link-bg {
    background: var(--primary-color);
    border-color: var(--primary-color);
    transform: translateX(-4px) translateY(-4px);
}

.social-link::before {
    content: '';
    position: absolute;
    inset: 0;
    border: 1px solid var(--theme-panel-border);
    transform: translateX(4px) translateY(4px);
    transition: all 0.3s ease;
}

.social-link:hover::before {
    border-color: var(--primary-color);
}

.link-text {
    position: relative;
    z-index: 1;
}

/* === Hero Visual === */
.hero-visual {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    animation: fadeScale 1s ease-out 0.8s forwards;
}

@keyframes fadeScale {
    from {
        opacity: 0;
        transform: scale(0.8);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

.avatar-ornament {
    position: absolute;
    inset: -40px;
}

.ornament-ring {
    position: absolute;
    inset: 0;
    border: 1px solid var(--theme-panel-border);
    border-radius: 50%;
    animation: rotate 20s linear infinite;
}

.ring-1 {
    animation-duration: 30s;
    border-style: dashed;
}

.ring-2 {
    inset: -20px;
    animation-duration: 40s;
    animation-direction: reverse;
}

.ring-3 {
    inset: -40px;
    animation-duration: 50s;
    border-style: dotted;
}

@keyframes rotate {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.avatar-wrapper {
    position: relative;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    overflow: hidden;
    border: 2px solid var(--theme-panel-border);
    box-shadow: 0 0 60px var(--theme-primary);
}

.avatar-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.avatar-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--theme-panel-bg);
    backdrop-filter: blur(20px);
}

.avatar-placeholder svg {
    width: 120px;
    height: 120px;
    color: var(--theme-panel-text);
    opacity: 0.4;
}

/* === Scroll Indicator === */
.scroll-indicator {
    position: absolute;
    bottom: 3rem;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    color: var(--theme-panel-text);
    opacity: 0.5;
    z-index: 3;
    animation: fadeIn 1s ease-out 1.5s forwards, float 2s ease-in-out 2s infinite;
}

@keyframes fadeIn {
    to {
        opacity: 1;
    }
}

@keyframes float {

    0%,
    100% {
        transform: translateX(-50%) translateY(0);
    }

    50% {
        transform: translateX(-50%) translateY(10px);
    }
}

.scroll-line {
    width: 1px;
    height: 40px;
    background: linear-gradient(to bottom, transparent, var(--theme-panel-text));
    opacity: 0.5;
}

.scroll-text {
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

/* === Content Section === */
.content-section {
    width: 100%;
    max-width: var(--max-width);
    margin: 0 auto;
    padding: 8rem 4rem;
}

/* === Section Wrapper === */
.section-wrapper {
    margin-bottom: 8rem;
    opacity: 0;
    animation: fadeSlideUp 0.8s ease-out forwards;
    animation-timeline: view();
    animation-range: entry 0% cover 30%;
}

.section-grid {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 4rem;
    align-items: start;
}

/* === Section Label === */
.section-label {
    position: sticky;
    top: 2rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.label-number {
    font-size: 3rem;
    font-weight: 200;
    color: var(--primary-color);
    line-height: 1;
}

.label-text {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #999999;
}

/* === Section Content === */
.section-content {
    min-height: 200px;
}

/* === Biography === */
.prose-content {
    font-size: 1.125rem;
    line-height: 1.8;
    color: var(--theme-body-text);
}

.prose-content p {
    margin-bottom: 1.5rem;
}

.prose-content p:last-child {
    margin-bottom: 0;
}

/* === Skills Marquee === */
.skills-marquee {
    width: 100%;
    overflow: hidden;
    padding: 2rem 0;
    margin-bottom: 3rem;
    border-top: 1px solid var(--theme-panel-border);
    border-bottom: 1px solid var(--theme-panel-border);
}

.marquee-content {
    display: flex;
    gap: 2rem;
    animation: marquee 30s linear infinite;
}

@keyframes marquee {
    from {
        transform: translateX(0);
    }

    to {
        transform: translateX(-50%);
    }
}

.skill-tag {
    flex-shrink: 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--theme-panel-text);
    opacity: 0.3;
    white-space: nowrap;
    font-family: 'Playfair Display', serif;
}

/* === Skills Grid Modern === */
.skills-grid-modern {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 2rem;
}

.skill-card {
    padding: 2rem;
    background: var(--theme-panel-bg);
    border: 1px solid var(--theme-panel-border);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    opacity: 0;
    animation: fadeSlideUp 0.6s ease-out calc(var(--card-index) * 0.1s) forwards;
}

.skill-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 2px;
    background: var(--primary-color);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.3s ease;
}

.skill-card:hover::before {
    transform: scaleX(1);
}

.skill-card:hover {
    background: var(--theme-body-bg);
    border-color: var(--theme-primary);
    transform: translateY(-4px);
}

.skill-number {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--theme-primary);
    margin-bottom: 1rem;
}

.skill-name {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--theme-body-text);
}

/* === Timeline Modern === */
.timeline-modern {
    display: flex;
    flex-direction: column;
    gap: 3rem;
}

.timeline-entry {
    display: grid;
    grid-template-columns: 120px 1px 1fr;
    gap: 2rem;
    opacity: 0;
    animation: fadeSlideUp 0.6s ease-out calc(var(--entry-index) * 0.15s) forwards;
}

.entry-year {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--primary-color);
    letter-spacing: 0.1em;
}

.entry-divider {
    width: 1px;
    background: linear-gradient(to bottom, var(--primary-color), transparent);
}

.entry-details {
    padding-bottom: 2rem;
}

.entry-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--theme-body-text);
    margin-bottom: 0.75rem;
    font-family: 'Playfair Display', serif;
}

.entry-description {
    font-size: 1rem;
    line-height: 1.7;
    color: var(--theme-panel-text);
    opacity: 0.7;
}

/* === Contact Card Modern === */
.contact-card-modern {
    padding: 3rem;
    background: var(--theme-panel-bg);
    color: var(--theme-body-text);
}

.contact-intro {
    font-size: 1.5rem;
    line-height: 1.6;
    margin-bottom: 2rem;
    color: var(--theme-panel-text);
    opacity: 0.8;
}

.contact-cta {
    display: inline-flex;
    align-items: center;
    gap: 1rem;
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary-color);
    text-decoration: none;
    transition: all 0.3s ease;
    font-family: 'Playfair Display', serif;
}

.contact-cta:hover {
    gap: 1.5rem;
}

.cta-text {
    border-bottom: 2px solid var(--primary-color);
}

.cta-arrow {
    font-size: 2.5rem;
    transition: transform 0.3s ease;
}

.contact-cta:hover .cta-arrow {
    transform: translateX(10px);
}

.contact-cta-placeholder {
    font-size: 1.5rem;
    color: var(--theme-panel-text);
    opacity: 0.5;
}

/* === Footer Spacer === */
.footer-spacer {
    height: 4rem;
}

/* === Responsive Design === */
@media (max-width: 1200px) {
    .hero-layout {
        grid-template-columns: 1fr;
        gap: 4rem;
    }

    .hero-visual {
        justify-content: center;
    }

    .avatar-wrapper {
        width: 240px;
        height: 240px;
    }

    .section-grid {
        grid-template-columns: 150px 1fr;
        gap: 3rem;
    }
}

@media (max-width: 968px) {
    .hero-content {
        padding: 0 2rem;
    }

    .content-section {
        padding: 6rem 2rem;
    }

    .section-wrapper {
        margin-bottom: 6rem;
    }

    .section-grid {
        grid-template-columns: 1fr;
        gap: 2rem;
    }

    .section-label {
        position: static;
        flex-direction: row;
        align-items: baseline;
        gap: 1rem;
    }

    .label-number {
        font-size: 2rem;
    }

    .skills-grid-modern {
        grid-template-columns: 1fr;
    }

    .timeline-entry {
        grid-template-columns: 100px 1px 1fr;
        gap: 1.5rem;
    }

    .contact-card-modern {
        padding: 2rem;
    }

    .contact-cta {
        font-size: 1.5rem;
    }

    .cta-arrow {
        font-size: 2rem;
    }
}

@media (max-width: 640px) {
    .hero-content {
        padding: 0 1.5rem;
    }

    .display-title {
        font-size: 2.5rem;
    }

    .hero-description {
        font-size: 1rem;
    }

    .avatar-wrapper {
        width: 200px;
        height: 200px;
    }

    .content-section {
        padding: 4rem 1.5rem;
    }

    .section-wrapper {
        margin-bottom: 4rem;
    }

    .prose-content {
        font-size: 1rem;
    }

    .skill-tag {
        font-size: 1.25rem;
    }

    .skills-grid-modern {
        gap: 1rem;
    }

    .skill-card {
        padding: 1.5rem;
    }

    .timeline-entry {
        grid-template-columns: 80px 1px 1fr;
        gap: 1rem;
    }

    .entry-title {
        font-size: 1.25rem;
    }

    .contact-intro {
        font-size: 1.25rem;
    }

    .contact-cta {
        font-size: 1.25rem;
    }
}
</style>