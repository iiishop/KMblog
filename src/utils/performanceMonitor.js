/**
 * 性能监控工具
 * 用于检测滚动、渲染和动画性能问题
 */

class PerformanceMonitor {
    constructor() {
        this.fps = 0;
        this.lastFrameTime = performance.now();
        this.frameCount = 0;
        this.isMonitoring = false;
        this.scrollEvents = 0;
        this.lastScrollTime = 0;
        this.overlay = null;
        this.longTaskObserver = null;
        this.measurements = [];
    }

    // 开始监控
    start() {
        if (this.isMonitoring) return;
        this.isMonitoring = true;

        console.log('%c🔍 性能监控已启动', 'color: #4CAF50; font-size: 14px; font-weight: bold');

        // 创建监控面板
        this.createOverlay();

        // FPS 监控
        this.monitorFPS();

        // 滚动性能监控
        this.monitorScroll();

        // 长任务监控
        this.monitorLongTasks();

        // DOM 变化监控
        this.monitorDOMMutations();

        // 内存监控（如果支持）
        if (performance.memory) {
            this.monitorMemory();
        }
    }

    // 停止监控
    stop() {
        this.isMonitoring = false;
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
        if (this.longTaskObserver) {
            this.longTaskObserver.disconnect();
        }
        if (this.domObserver) {
            this.domObserver.disconnect();
        }
        console.log('%c⏸️ 性能监控已停止', 'color: #FF9800; font-size: 14px; font-weight: bold');
        this.printSummary();
    }

    // 创建监控面板
    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.id = 'perf-monitor';
        this.overlay.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.9);
            color: #00ff00;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            z-index: 999999;
            min-width: 280px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            backdrop-filter: blur(10px);
        `;
        this.overlay.innerHTML = `
            <div style="margin-bottom: 10px; color: #4CAF50; font-weight: bold; border-bottom: 1px solid #333; padding-bottom: 5px;">
                ⚡ 性能监控面板
            </div>
            <div id="perf-fps">FPS: --</div>
            <div id="perf-scroll">滚动事件: 0/s</div>
            <div id="perf-memory">内存: --</div>
            <div id="perf-dom">DOM 节点: --</div>
            <div id="perf-tasks">长任务: 0</div>
            <div id="perf-warnings" style="margin-top: 10px; color: #ff6b6b; font-size: 11px;"></div>
        `;
        document.body.appendChild(this.overlay);
    }

    // FPS 监控
    monitorFPS() {
        const measure = () => {
            if (!this.isMonitoring) return;

            const now = performance.now();
            const delta = now - this.lastFrameTime;
            this.frameCount++;

            if (delta >= 1000) {
                this.fps = Math.round((this.frameCount * 1000) / delta);
                this.frameCount = 0;
                this.lastFrameTime = now;

                const fpsEl = document.getElementById('perf-fps');
                if (fpsEl) {
                    const color = this.fps >= 55 ? '#00ff00' : this.fps >= 30 ? '#ffaa00' : '#ff0000';
                    fpsEl.style.color = color;
                    fpsEl.textContent = `FPS: ${this.fps}`;

                    if (this.fps < 30) {
                        this.addWarning('⚠️ FPS 过低！检查动画和重绘');
                    }
                }
            }

            requestAnimationFrame(measure);
        };
        requestAnimationFrame(measure);
    }

    // 滚动性能监控
    monitorScroll() {
        let scrollEventCount = 0;
        let lastUpdate = performance.now();

        const scrollHandler = () => {
            scrollEventCount++;
            const now = performance.now();

            if (now - lastUpdate >= 1000) {
                this.scrollEvents = scrollEventCount;
                scrollEventCount = 0;
                lastUpdate = now;

                const scrollEl = document.getElementById('perf-scroll');
                if (scrollEl) {
                    scrollEl.textContent = `滚动事件: ${this.scrollEvents}/s`;
                    if (this.scrollEvents > 100) {
                        this.addWarning('⚠️ 滚动事件过于频繁，检查是否有节流');
                    }
                }
            }
        };

        window.addEventListener('scroll', scrollHandler, { passive: true });
    }

    // 长任务监控
    monitorLongTasks() {
        if (!('PerformanceObserver' in window)) {
            console.warn('浏览器不支持 PerformanceObserver');
            return;
        }

        try {
            let longTaskCount = 0;
            this.longTaskObserver = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.duration > 50) {
                        longTaskCount++;
                        console.warn(
                            `🐌 检测到长任务: ${entry.duration.toFixed(2)}ms`,
                            entry
                        );

                        const tasksEl = document.getElementById('perf-tasks');
                        if (tasksEl) {
                            tasksEl.textContent = `长任务: ${longTaskCount} (${entry.duration.toFixed(0)}ms)`;
                            tasksEl.style.color = '#ff6b6b';
                        }

                        if (entry.duration > 100) {
                            this.addWarning(`🔴 极长任务: ${entry.duration.toFixed(0)}ms - ${entry.name}`);
                        }
                    }
                }
            });

            this.longTaskObserver.observe({ entryTypes: ['longtask', 'measure'] });
        } catch (e) {
            console.warn('长任务监控不可用:', e);
        }
    }

    // DOM 变化监控
    monitorDOMMutations() {
        let mutationCount = 0;
        let lastUpdate = performance.now();

        this.domObserver = new MutationObserver((mutations) => {
            mutationCount += mutations.length;

            const now = performance.now();
            if (now - lastUpdate >= 1000) {
                const domEl = document.getElementById('perf-dom');
                if (domEl) {
                    const nodeCount = document.querySelectorAll('*').length;
                    domEl.textContent = `DOM 节点: ${nodeCount} (变化: ${mutationCount}/s)`;

                    if (mutationCount > 100) {
                        this.addWarning(`⚠️ DOM 频繁变化: ${mutationCount}/s`);
                    }
                }

                mutationCount = 0;
                lastUpdate = now;
            }
        });

        this.domObserver.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
        });
    }

    // 内存监控
    monitorMemory() {
        setInterval(() => {
            if (!this.isMonitoring || !performance.memory) return;

            const memoryEl = document.getElementById('perf-memory');
            if (memoryEl) {
                const used = (performance.memory.usedJSHeapSize / 1048576).toFixed(2);
                const total = (performance.memory.totalJSHeapSize / 1048576).toFixed(2);
                memoryEl.textContent = `内存: ${used}MB / ${total}MB`;

                const usage = performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit;
                if (usage > 0.9) {
                    this.addWarning('⚠️ 内存使用率过高！可能存在内存泄漏');
                }
            }
        }, 2000);
    }

    // 添加警告信息
    addWarning(message) {
        const warningsEl = document.getElementById('perf-warnings');
        if (!warningsEl) return;

        const existingWarnings = warningsEl.textContent.split('\n').filter(w => w);
        if (!existingWarnings.includes(message)) {
            existingWarnings.push(message);
            if (existingWarnings.length > 3) {
                existingWarnings.shift();
            }
            warningsEl.textContent = existingWarnings.join('\n');
        }
    }

    // 打印性能摘要
    printSummary() {
        console.group('%c📊 性能监控摘要', 'color: #2196F3; font-size: 16px; font-weight: bold');
        console.log(`最终 FPS: ${this.fps}`);
        console.log(`最后滚动事件频率: ${this.scrollEvents}/s`);

        if (performance.memory) {
            console.log(`内存使用: ${(performance.memory.usedJSHeapSize / 1048576).toFixed(2)}MB`);
        }

        // 性能建议
        console.group('💡 性能优化建议:');
        if (this.fps < 30) {
            console.log('• FPS 过低，检查动画、重绘和回流');
        }
        if (this.scrollEvents > 100) {
            console.log('• 滚动事件过于频繁，建议添加节流');
        }
        console.log('• 使用 Chrome DevTools Performance 面板录制详细分析');
        console.log('• 检查 Network 面板是否有资源加载阻塞');
        console.groupEnd();

        console.groupEnd();
    }
}

// 创建全局实例
const perfMonitor = new PerformanceMonitor();

// 导出
export default perfMonitor;

// 也添加到 window 以便控制台调用
if (typeof window !== 'undefined') {
    window.perfMonitor = perfMonitor;
}
