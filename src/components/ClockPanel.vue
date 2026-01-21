<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import gsap from 'gsap';

// 模式切换：'clock' 或 'pomodoro'
const mode = ref('clock');

// 动画颜色变量
const themeColors = ref({
    panelBgStart: '#2a2a2a',
    panelBgEnd: '#1a1a1a',
    panelBorder: 'rgba(255, 255, 255, 0.05)',
    panelTopBar: '#2a2a2a',
    modeSwitchBg: 'rgba(0, 0, 0, 0.3)',
    lcdBorder: '#0a1a0f',
    shadowColor: 'rgba(0, 0, 0, 0.6)'
});

// 时间状态
const currentTime = ref(new Date());
const timer = ref(null);

// 时区配置
const availableTimezones = [
    { value: 'Asia/Shanghai', label: '北京 (UTC+8)', offset: '+8' },
    { value: 'America/New_York', label: '纽约 (UTC-5)', offset: '-5' },
    { value: 'Europe/London', label: '伦敦 (UTC+0)', offset: '+0' },
    { value: 'Asia/Tokyo', label: '东京 (UTC+9)', offset: '+9' },
    { value: 'Europe/Paris', label: '巴黎 (UTC+1)', offset: '+1' },
    { value: 'Australia/Sydney', label: '悉尼 (UTC+11)', offset: '+11' },
    { value: 'Asia/Dubai', label: '迪拜 (UTC+4)', offset: '+4' },
    { value: 'America/Los_Angeles', label: '洛杉矶 (UTC-8)', offset: '-8' }
];

// 从localStorage加载保存的时区，如果没有则使用默认值
const savedTimezone = localStorage.getItem('clockPanelTimezone') || 'Asia/Shanghai';
const selectedTimezone = ref(savedTimezone);

// 监听时区变化，自动保存到localStorage
watch(selectedTimezone, (newTimezone) => {
    localStorage.setItem('clockPanelTimezone', newTimezone);
});

// 监听模式变化，使用GSAP做平滑颜色过渡
watch(mode, (newMode) => {
    if (newMode === 'pomodoro') {
        // 切换到番茄钟模式 - 红白配色
        gsap.to(themeColors.value, {
            duration: 0.6,
            ease: 'power2.inOut',
            panelBgStart: '#ffffff',
            panelBgEnd: '#f5f5f5',
            panelBorder: 'rgba(239, 68, 68, 0.3)',
            panelTopBar: '#ef4444',
            modeSwitchBg: 'rgba(239, 68, 68, 0.1)',
            lcdBorder: '#f5f5f5',
            shadowColor: 'rgba(239, 68, 68, 0.4)'
        });
    } else {
        // 切换回时钟模式 - 黑绿配色
        gsap.to(themeColors.value, {
            duration: 0.6,
            ease: 'power2.inOut',
            panelBgStart: '#2a2a2a',
            panelBgEnd: '#1a1a1a',
            panelBorder: 'rgba(255, 255, 255, 0.05)',
            panelTopBar: '#2a2a2a',
            modeSwitchBg: 'rgba(0, 0, 0, 0.3)',
            lcdBorder: '#0a1a0f',
            shadowColor: 'rgba(0, 0, 0, 0.6)'
        });
    }
});

// 番茄钟状态
const pomodoroMinutes = ref(25);
const pomodoroSeconds = ref(0);
const pomodoroRunning = ref(false);
const pomodoroTimer = ref(null);
const pomodoroFlashing = ref(false);

// 格式化时间
const formatTime = (date, timezone) => {
    return date.toLocaleTimeString('zh-CN', {
        timeZone: timezone,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
};

const formatDate = (date, timezone) => {
    const options = {
        timeZone: timezone,
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    };
    return date.toLocaleDateString('zh-CN', options);
};

// 计算属性
const displayTime = computed(() => {
    if (mode.value === 'clock') {
        return formatTime(currentTime.value, selectedTimezone.value);
    } else {
        const mins = String(pomodoroMinutes.value).padStart(2, '0');
        const secs = String(pomodoroSeconds.value).padStart(2, '0');
        return `${mins}:${secs}`;
    }
});

const displayDate = computed(() => formatDate(currentTime.value, selectedTimezone.value));

const currentTimezoneInfo = computed(() => {
    return availableTimezones.find(tz => tz.value === selectedTimezone.value);
});

// 更新时间
const updateTime = () => {
    currentTime.value = new Date();
};

// 切换模式
const switchMode = (newMode) => {
    if (pomodoroFlashing.value && newMode === 'pomodoro') {
        pomodoroFlashing.value = false;
        pomodoroMinutes.value = 25;
        pomodoroSeconds.value = 0;
    }
    mode.value = newMode;
};



// 番茄钟控制
const startPomodoro = () => {
    if (pomodoroFlashing.value) {
        pomodoroFlashing.value = false;
        pomodoroMinutes.value = 25;
        pomodoroSeconds.value = 0;
        return;
    }

    pomodoroRunning.value = true;
    pomodoroTimer.value = setInterval(() => {
        if (pomodoroSeconds.value > 0) {
            pomodoroSeconds.value--;
        } else if (pomodoroMinutes.value > 0) {
            pomodoroMinutes.value--;
            pomodoroSeconds.value = 59;
        } else {
            clearInterval(pomodoroTimer.value);
            pomodoroRunning.value = false;
            pomodoroFlashing.value = true;
            // 播放提示音
            playNotificationSound();
            // 发送系统通知
            sendSystemNotification();
        }
    }, 1000);
};

const pausePomodoro = () => {
    if (pomodoroTimer.value) {
        clearInterval(pomodoroTimer.value);
        pomodoroRunning.value = false;
    }
};

const resetPomodoro = () => {
    pausePomodoro();
    pomodoroMinutes.value = 25;
    pomodoroSeconds.value = 0;
    pomodoroFlashing.value = false;
};

const adjustPomodoroTime = (minutes) => {
    if (!pomodoroRunning.value && !pomodoroFlashing.value) {
        pomodoroMinutes.value = Math.max(1, Math.min(60, pomodoroMinutes.value + minutes));
        pomodoroSeconds.value = 0;
    }
};

// 播放提示音
const playNotificationSound = () => {
    try {
        // 使用Web Audio API生成提示音
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        // 设置音调和音量
        oscillator.frequency.value = 800; // 频率 (Hz)
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);

        // 播放三声短促的提示音
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);

        setTimeout(() => {
            const osc2 = audioContext.createOscillator();
            const gain2 = audioContext.createGain();
            osc2.connect(gain2);
            gain2.connect(audioContext.destination);
            osc2.frequency.value = 1000;
            gain2.gain.setValueAtTime(0.3, audioContext.currentTime);
            osc2.start(audioContext.currentTime);
            osc2.stop(audioContext.currentTime + 0.1);
        }, 200);

        setTimeout(() => {
            const osc3 = audioContext.createOscillator();
            const gain3 = audioContext.createGain();
            osc3.connect(gain3);
            gain3.connect(audioContext.destination);
            osc3.frequency.value = 1200;
            gain3.gain.setValueAtTime(0.3, audioContext.currentTime);
            osc3.start(audioContext.currentTime);
            osc3.stop(audioContext.currentTime + 0.15);
        }, 400);
    } catch (error) {
        console.error('播放提示音失败:', error);
    }
};

// 发送系统通知
const sendSystemNotification = () => {
    // 检查浏览器是否支持通知
    if (!('Notification' in window)) {
        console.log('此浏览器不支持系统通知');
        return;
    }

    // 检查通知权限
    if (Notification.permission === 'granted') {
        // 已授权，直接发送通知
        new Notification('⏰ 番茄钟提醒', {
            body: '专注时间已结束！该休息一下了~',
            icon: '/favicon.ico',
            badge: '/favicon.ico',
            tag: 'pomodoro-timer',
            requireInteraction: true, // 需要用户交互才关闭
            silent: false
        });
    } else if (Notification.permission !== 'denied') {
        // 未授权，请求权限
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                new Notification('⏰ 番茄钟提醒', {
                    body: '专注时间已结束！该休息一下了~',
                    icon: '/favicon.ico',
                    badge: '/favicon.ico',
                    tag: 'pomodoro-timer',
                    requireInteraction: true,
                    silent: false
                });
            }
        });
    }
};

// 生命周期
onMounted(() => {
    timer.value = setInterval(updateTime, 1000);

    // 页面加载时请求通知权限（不会强制弹窗）
    if ('Notification' in window && Notification.permission === 'default') {
        // 可以在这里提示用户，但不强制请求
        console.log('可以启用通知以接收番茄钟提醒');
    }
});

onUnmounted(() => {
    if (timer.value) clearInterval(timer.value);
    if (pomodoroTimer.value) clearInterval(pomodoroTimer.value);
});
</script>

<template>
    <div class="ClockPanel" :class="{ 'flashing': pomodoroFlashing, 'pomodoro-mode': mode === 'pomodoro' }" :style="{
        '--panel-bg-start': themeColors.panelBgStart,
        '--panel-bg-end': themeColors.panelBgEnd,
        '--panel-border': themeColors.panelBorder,
        '--panel-top-bar': themeColors.panelTopBar,
        '--mode-switch-bg': themeColors.modeSwitchBg,
        '--lcd-border': themeColors.lcdBorder,
        '--shadow-color': themeColors.shadowColor
    }">
        <!-- 模式切换按钮 -->
        <div class="mode-switch">
            <button class="mode-btn" :class="{ active: mode === 'clock' }" @click="switchMode('clock')">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path fill-rule="evenodd"
                        d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 6a.75.75 0 0 0-1.5 0v6c0 .414.336.75.75.75h4.5a.75.75 0 0 0 0-1.5h-3.75V6Z"
                        clip-rule="evenodd" />
                </svg>
                时钟
            </button>
            <button class="mode-btn" :class="{ active: mode === 'pomodoro' }" @click="switchMode('pomodoro')">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                    <path fill-rule="evenodd"
                        d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25ZM12.75 6a.75.75 0 0 0-1.5 0v6c0 .414.336.75.75.75h4.5a.75.75 0 0 0 0-1.5h-3.75V6Z"
                        clip-rule="evenodd" />
                </svg>
                番茄钟
            </button>
        </div>

        <!-- 主显示区域 - 电子表LCD屏幕 -->
        <div class="lcd-screen" :class="{ 'alert': pomodoroFlashing, 'pomodoro-mode': mode === 'pomodoro' }">
            <div class="lcd-inner">
                <!-- 数码管数字显示 -->
                <div class="digit-display">{{ displayTime }}</div>

                <!-- 信息显示区域（固定高度） -->
                <div class="info-area">
                    <div v-if="mode === 'clock'" class="clock-info">
                        <div class="lcd-date">{{ displayDate }}</div>
                        <select class="timezone-select" v-model="selectedTimezone">
                            <option v-for="tz in availableTimezones" :key="tz.value" :value="tz.value">
                                {{ tz.label }}
                            </option>
                        </select>
                    </div>
                    <div v-else class="pomodoro-info">
                        <div class="lcd-status">
                            {{ pomodoroFlashing ? '时间到！' : pomodoroRunning ? '专注中' : '就绪' }}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 控制按钮区域（固定高度） -->
        <div class="controls-area">
            <!-- 时钟模式占位 -->
            <div v-if="mode === 'clock'" class="clock-controls"></div>

            <!-- 番茄钟模式控制 -->
            <div v-else class="pomodoro-controls">
                <div class="time-adjust" v-if="!pomodoroRunning && !pomodoroFlashing">
                    <button class="adjust-btn" @click="adjustPomodoroTime(-5)">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M4.25 12a.75.75 0 0 1 .75-.75h14a.75.75 0 0 1 0 1.5H5a.75.75 0 0 1-.75-.75Z"
                                clip-rule="evenodd" />
                        </svg>
                        5分钟
                    </button>
                    <button class="adjust-btn" @click="adjustPomodoroTime(5)">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M12 3.75a.75.75 0 0 1 .75.75v6.75h6.75a.75.75 0 0 1 0 1.5h-6.75v6.75a.75.75 0 0 1-1.5 0v-6.75H4.5a.75.75 0 0 1 0-1.5h6.75V4.5a.75.75 0 0 1 .75-.75Z"
                                clip-rule="evenodd" />
                        </svg>
                        5分钟
                    </button>
                </div>

                <div class="action-buttons">
                    <button class="action-btn primary" @click="pomodoroRunning ? pausePomodoro() : startPomodoro()"
                        :class="{ 'stop-flash': pomodoroFlashing }">
                        <svg v-if="!pomodoroRunning && !pomodoroFlashing" xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24" fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M4.5 5.653c0-1.427 1.529-2.33 2.779-1.643l11.54 6.347c1.295.712 1.295 2.573 0 3.286L7.28 19.99c-1.25.687-2.779-.217-2.779-1.643V5.653Z"
                                clip-rule="evenodd" />
                        </svg>
                        <svg v-else-if="pomodoroRunning" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                            fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M6.75 5.25a.75.75 0 0 1 .75-.75H9a.75.75 0 0 1 .75.75v13.5a.75.75 0 0 1-.75.75H7.5a.75.75 0 0 1-.75-.75V5.25Zm7.5 0A.75.75 0 0 1 15 4.5h1.5a.75.75 0 0 1 .75.75v13.5a.75.75 0 0 1-.75.75H15a.75.75 0 0 1-.75-.75V5.25Z"
                                clip-rule="evenodd" />
                        </svg>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M5.25 9a6.75 6.75 0 0 1 13.5 0v.75c0 2.123.8 4.057 2.118 5.52a.75.75 0 0 1-.297 1.206c-1.544.57-3.16.99-4.831 1.243a3.75 3.75 0 1 1-7.48 0 24.585 24.585 0 0 1-4.831-1.244.75.75 0 0 1-.298-1.205A8.217 8.217 0 0 0 5.25 9.75V9Zm4.502 8.9a2.25 2.25 0 1 0 4.496 0 25.057 25.057 0 0 1-4.496 0Z"
                                clip-rule="evenodd" />
                        </svg>
                        {{ pomodoroFlashing ? '停止提醒' : pomodoroRunning ? '暂停' : '开始' }}
                    </button>
                    <button class="action-btn secondary" @click="resetPomodoro">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                            <path fill-rule="evenodd"
                                d="M4.755 10.059a7.5 7.5 0 0 1 12.548-3.364l1.903 1.903h-3.183a.75.75 0 1 0 0 1.5h4.992a.75.75 0 0 0 .75-.75V4.356a.75.75 0 0 0-1.5 0v3.18l-1.9-1.9A9 9 0 0 0 3.306 9.67a.75.75 0 1 0 1.45.388Zm15.408 3.352a.75.75 0 0 0-.919.53 7.5 7.5 0 0 1-12.548 3.364l-1.902-1.903h3.183a.75.75 0 0 0 0-1.5H2.984a.75.75 0 0 0-.75.75v4.992a.75.75 0 0 0 1.5 0v-3.18l1.9 1.9a9 9 0 0 0 15.059-4.035.75.75 0 0 0-.53-.918Z"
                                clip-rule="evenodd" />
                        </svg>
                        重置
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.ClockPanel {
    display: flex;
    flex-direction: column;
    background: linear-gradient(145deg, var(--panel-bg-start), var(--panel-bg-end));
    padding: 1.25rem;
    width: 100%;
    border-radius: 24px;
    box-shadow:
        0 8px 32px var(--shadow-color),
        inset 0 1px 0 rgba(255, 255, 255, 0.1),
        inset 0 -1px 2px rgba(0, 0, 0, 0.5);
    gap: 1rem;
    color: var(--clock-panel-text-color, #e5e5e5);
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid var(--panel-border);
    position: relative;
    overflow: hidden;
}

.ClockPanel::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--panel-top-bar), var(--panel-bg-start), var(--panel-top-bar));
    transition: background 0.6s ease;
}

.ClockPanel:hover {
    transform: translateY(-2px);
    box-shadow:
        0 12px 40px var(--shadow-color),
        inset 0 1px 0 rgba(255, 255, 255, 0.15),
        inset 0 -1px 2px rgba(0, 0, 0, 0.5);
}

/* 番茄钟模式 - 动态样式调整 */
.ClockPanel.pomodoro-mode {
    box-shadow:
        0 8px 32px var(--shadow-color),
        inset 0 1px 0 rgba(255, 255, 255, 0.9),
        inset 0 -1px 2px rgba(239, 68, 68, 0.2);
}

.ClockPanel.pomodoro-mode:hover {
    box-shadow:
        0 12px 40px var(--shadow-color),
        inset 0 1px 0 rgba(255, 255, 255, 0.9),
        inset 0 -1px 2px rgba(239, 68, 68, 0.3);
}

.ClockPanel.pomodoro-mode .mode-btn {
    background: linear-gradient(145deg, #ffffff, #f5f5f5);
    border-color: rgba(239, 68, 68, 0.2);
    color: #999;
    transition: all 0.3s ease;
}

.ClockPanel.pomodoro-mode .mode-btn:hover {
    background: linear-gradient(145deg, #fef2f2, #fee2e2);
    color: #ef4444;
}

.ClockPanel.pomodoro-mode .mode-btn.active {
    background: linear-gradient(145deg, #fca5a5, #f87171);
    color: #ffffff;
    border-color: rgba(239, 68, 68, 0.5);
    box-shadow:
        0 4px 16px rgba(239, 68, 68, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

/* 闪烁动画 */
.ClockPanel.flashing {
    animation: flash 0.6s ease-in-out infinite;
}

@keyframes flash {

    0%,
    100% {
        box-shadow: 0 0 40px rgba(239, 68, 68, 0.8), 0 0 80px rgba(239, 68, 68, 0.4);
    }

    50% {
        box-shadow: 0 0 60px rgba(239, 68, 68, 1), 0 0 120px rgba(239, 68, 68, 0.6);
    }
}

/* 模式切换 */
.mode-switch {
    display: flex;
    gap: 0.5rem;
    padding: 0.375rem;
    background: var(--mode-switch-bg);
    border-radius: 16px;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.6);
    transition: background 0.6s ease;
}

.mode-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: linear-gradient(145deg, #2a2a2a, #1f1f1f);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 600;
    color: #666;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.mode-btn svg {
    width: 18px;
    height: 18px;
}

.mode-btn:hover {
    background: linear-gradient(145deg, #333, #252525);
    color: #888;
}

.mode-btn.active {
    background: linear-gradient(145deg, #3a3a3a, #2a2a2a);
    color: #4ade80;
    border-color: rgba(74, 222, 128, 0.3);
    box-shadow:
        0 4px 16px rgba(74, 222, 128, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* LCD 屏幕 - 拟物化电子表显示 */
.lcd-screen {
    background:
        linear-gradient(145deg, #1a2820, #132118),
        radial-gradient(ellipse at top, rgba(74, 222, 128, 0.05), transparent);
    border: 3px solid var(--lcd-border);
    border-radius: 16px;
    padding: 1.5rem 1rem;
    box-shadow:
        inset 0 3px 8px rgba(0, 0, 0, 0.8),
        inset 0 -1px 2px rgba(74, 222, 128, 0.1),
        0 4px 12px rgba(0, 0, 0, 0.5);
    position: relative;
    overflow: hidden;
    /* 固定高度确保一致性 */
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    /* 添加渐变过渡 */
    transition: all 0.6s ease;
}

/* 番茄钟模式红白配色 */
.lcd-screen.pomodoro-mode {
    background:
        linear-gradient(145deg, #2a1a1a, #1a1212),
        radial-gradient(ellipse at top, rgba(239, 68, 68, 0.05), transparent);
    border-color: #f5f5f5;
    /* 白色边框 */
    border-width: 3px;
    box-shadow:
        inset 0 3px 8px rgba(0, 0, 0, 0.8),
        inset 0 -1px 2px rgba(239, 68, 68, 0.1),
        0 4px 12px rgba(239, 68, 68, 0.3),
        0 0 20px rgba(255, 255, 255, 0.3);
    /* 白色外发光 */
}

.lcd-screen.pomodoro-mode .digit-display {
    color: #f87171;
    text-shadow:
        0 0 10px rgba(248, 113, 113, 0.8),
        0 0 20px rgba(248, 113, 113, 0.6),
        0 0 30px rgba(248, 113, 113, 0.4),
        0 2px 4px rgba(0, 0, 0, 0.8);
}

.lcd-screen.pomodoro-mode .lcd-status {
    color: #fca5a5;
    text-shadow: 0 0 5px rgba(252, 165, 165, 0.6);
}

.lcd-screen.pomodoro-mode .lcd-date {
    color: rgba(248, 113, 113, 0.7);
    text-shadow: 0 0 8px rgba(248, 113, 113, 0.5);
}

/* LCD 网格纹理效果 */
.lcd-screen::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
        repeating-linear-gradient(0deg,
            rgba(74, 222, 128, 0.03) 0px,
            transparent 1px,
            transparent 2px),
        repeating-linear-gradient(90deg,
            rgba(74, 222, 128, 0.03) 0px,
            transparent 1px,
            transparent 2px);
    pointer-events: none;
    z-index: 1;
}

/* LCD 反光效果 */
.lcd-screen::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 40%;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.05), transparent);
    pointer-events: none;
    z-index: 2;
}

.lcd-inner {
    position: relative;
    z-index: 3;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

.lcd-screen.alert {
    animation: lcdFlash 0.6s ease-in-out infinite;
    border-color: #ff4444;
}

@keyframes lcdFlash {

    0%,
    100% {
        background: linear-gradient(145deg, #2a1818, #1a0808);
        box-shadow:
            inset 0 3px 8px rgba(0, 0, 0, 0.8),
            inset 0 0 20px rgba(255, 68, 68, 0.3),
            0 0 30px rgba(255, 68, 68, 0.5);
    }

    50% {
        background: linear-gradient(145deg, #3a1a1a, #250a0a);
        box-shadow:
            inset 0 3px 8px rgba(0, 0, 0, 0.8),
            inset 0 0 30px rgba(255, 68, 68, 0.5),
            0 0 50px rgba(255, 68, 68, 0.8);
    }
}

/* 七段数码管数字显示 */
.digit-display {
    font-family: 'Orbitron', 'SF Mono', monospace;
    font-size: 3.2rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    color: #4ade80;
    text-shadow:
        0 0 10px rgba(74, 222, 128, 0.8),
        0 0 20px rgba(74, 222, 128, 0.6),
        0 0 30px rgba(74, 222, 128, 0.4),
        0 2px 4px rgba(0, 0, 0, 0.8);
    filter: brightness(1.2) contrast(1.1);
    line-height: 1;
    font-variant-numeric: tabular-nums;
    /* 数码管未点亮的段显示 */
    position: relative;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: clip;
}

.digit-display::before {
    content: attr(data-text);
    position: absolute;
    top: 0;
    left: 0;
    color: rgba(74, 222, 128, 0.08);
    text-shadow: none;
    z-index: -1;
}

.lcd-screen.alert .digit-display {
    color: #ff4444;
    text-shadow:
        0 0 15px rgba(255, 68, 68, 1),
        0 0 25px rgba(255, 68, 68, 0.8),
        0 0 35px rgba(255, 68, 68, 0.6),
        0 2px 4px rgba(0, 0, 0, 0.8);
}

/* 信息显示区域 - 固定高度确保一致性 */
.info-area {
    width: 100%;
    min-height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.clock-info,
.pomodoro-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
}

.lcd-date {
    font-size: 0.85rem;
    font-weight: 500;
    color: rgba(74, 222, 128, 0.7);
    text-shadow: 0 0 8px rgba(74, 222, 128, 0.5);
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

/* 原生select时区选择器 */
.timezone-select {
    background: rgba(74, 222, 128, 0.1);
    border: 1px solid rgba(74, 222, 128, 0.3);
    border-radius: 8px;
    color: #4ade80;
    padding: 6px 12px;
    font-size: 0.85rem;
    font-family: 'Orbitron', 'SF Mono', monospace;
    cursor: pointer;
    outline: none;
    text-shadow: 0 0 5px rgba(74, 222, 128, 0.5);
    transition: all 0.3s ease;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.5);
}

.timezone-select:hover {
    background: rgba(74, 222, 128, 0.15);
    border-color: rgba(74, 222, 128, 0.5);
    box-shadow:
        inset 0 1px 2px rgba(0, 0, 0, 0.5),
        0 0 10px rgba(74, 222, 128, 0.3);
}

.timezone-select:focus {
    border-color: rgba(74, 222, 128, 0.6);
    box-shadow: 0 0 12px rgba(74, 222, 128, 0.4);
}

/* 番茄钟模式下的select样式 */
.lcd-screen.pomodoro-mode .timezone-select {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.3);
    color: #f87171;
    text-shadow: 0 0 5px rgba(248, 113, 113, 0.5);
}

.lcd-screen.pomodoro-mode .timezone-select:hover {
    background: rgba(239, 68, 68, 0.15);
    border-color: rgba(239, 68, 68, 0.5);
    box-shadow:
        inset 0 1px 2px rgba(0, 0, 0, 0.5),
        0 0 10px rgba(239, 68, 68, 0.3);
}

.lcd-status {
    font-size: 1.1rem;
    font-weight: 600;
    color: rgba(74, 222, 128, 0.8);
    text-shadow: 0 0 8px rgba(74, 222, 128, 0.5);
    letter-spacing: 0.1em;
}

/* 控制按钮区域 - 统一高度 */
.controls-area {
    margin-top: 15px;
    min-height: 100px;
}

.clock-controls {
    /* 空占位保持高度 */
    height: 100px;
}

.pomodoro-controls {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.time-adjust {
    display: flex;
    gap: 0.5rem;
}

.adjust-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem;
    background: linear-gradient(145deg, #2a2a2a, #1f1f1f);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    color: #4ade80;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.adjust-btn:hover {
    background: linear-gradient(145deg, #333, #252525);
    box-shadow: 0 4px 12px rgba(74, 222, 128, 0.2);
    border-color: rgba(74, 222, 128, 0.3);
}

.adjust-btn svg {
    width: 16px;
    height: 16px;
}

.action-buttons {
    display: flex;
    gap: 0.5rem;
}

.action-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.875rem 1.25rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    font-size: 0.9rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.action-btn svg {
    width: 18px;
    height: 18px;
}

.action-btn.primary {
    background: linear-gradient(145deg, #4ade80, #22c55e);
    color: #0a1a0f;
    border-color: rgba(74, 222, 128, 0.3);
    box-shadow:
        0 4px 16px rgba(74, 222, 128, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

/* 番茄钟模式下的按钮样式 */
.ClockPanel.pomodoro-mode .action-btn.primary {
    background: linear-gradient(145deg, #fca5a5, #f87171);
    color: #ffffff;
    border-color: rgba(239, 68, 68, 0.3);
    box-shadow:
        0 4px 16px rgba(239, 68, 68, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.ClockPanel.pomodoro-mode .action-btn.primary:hover {
    background: linear-gradient(145deg, #f87171, #ef4444);
    box-shadow:
        0 6px 20px rgba(239, 68, 68, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.ClockPanel.pomodoro-mode .adjust-btn {
    background: linear-gradient(145deg, #ffffff, #f5f5f5);
    border-color: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

.ClockPanel.pomodoro-mode .adjust-btn:hover {
    background: linear-gradient(145deg, #fef2f2, #fee2e2);
    border-color: rgba(239, 68, 68, 0.4);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.ClockPanel.pomodoro-mode .action-btn.secondary {
    background: linear-gradient(145deg, #ffffff, #f5f5f5);
    color: #ef4444;
    border-color: rgba(239, 68, 68, 0.2);
}

.ClockPanel.pomodoro-mode .action-btn.secondary:hover {
    background: linear-gradient(145deg, #fef2f2, #fee2e2);
    border-color: rgba(239, 68, 68, 0.3);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.action-btn.primary:hover {
    background: linear-gradient(145deg, #5aee90, #32d56e);
    transform: translateY(-2px);
    box-shadow:
        0 6px 20px rgba(74, 222, 128, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.action-btn.primary.stop-flash {
    background: linear-gradient(145deg, #fbbf24, #f59e0b);
    color: #1a1a1a;
    border-color: rgba(251, 191, 36, 0.3);
    animation: btnPulse 1s ease-in-out infinite;
}

@keyframes btnPulse {

    0%,
    100% {
        transform: scale(1);
        box-shadow: 0 4px 16px rgba(251, 191, 36, 0.4);
    }

    50% {
        transform: scale(1.05);
        box-shadow: 0 6px 24px rgba(251, 191, 36, 0.6);
    }
}

.action-btn.secondary {
    background: linear-gradient(145deg, #2a2a2a, #1f1f1f);
    color: #888;
}

.action-btn.secondary:hover {
    background: linear-gradient(145deg, #333, #252525);
    color: #4ade80;
    border-color: rgba(74, 222, 128, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(74, 222, 128, 0.2);
}

.action-btn:active {
    transform: translateY(0) !important;
}

.action-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none !important;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

/* 响应式 */
@media (max-width: 768px) {
    .ClockPanel {
        padding: 1rem;
    }

    .digit-display {
        font-size: 2.5rem;
    }

    .lcd-screen {
        padding: 1.25rem 0.75rem;
        height: 180px;
    }

    .mode-btn {
        font-size: 0.85rem;
        padding: 0.625rem 0.75rem;
    }

    .action-buttons {
        flex-direction: column;
    }

    .action-btn {
        width: 100%;
    }

    .controls-area {
        min-height: 90px;
    }

    .clock-controls {
        height: 90px;
    }
}

@media (max-width: 480px) {
    .digit-display {
        font-size: 2rem;
    }

    .lcd-date,
    .lcd-status {
        font-size: 0.75rem;
    }

    .lcd-screen {
        height: 160px;
        padding: 1rem 0.5rem;
    }

    .timezone-select {
        font-size: 0.75rem;
        padding: 4px 8px;
    }

    .controls-area {
        min-height: 80px;
    }

    .clock-controls {
        height: 80px;
    }
}
</style>
