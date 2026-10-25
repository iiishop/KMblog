// 获取当前主题
function getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'day';
}

// 根据主题返回 Mermaid 配置
function getMermaidThemeConfig(theme) {
    const isDark = theme === 'dark' || theme === 'night';
    const palette = getComputedStyle(document.documentElement);
    const ink = palette.getPropertyValue('--theme-index').trim() || (isDark ? '#b2becb' : '#475569');
    const reading = palette.getPropertyValue('--theme-reading').trim() || (isDark ? '#8ad3b9' : '#246b58');
    const surface = palette.getPropertyValue('--theme-surface-active').trim() || (isDark ? '#333333' : '#f3f4f6');

    if (isDark) {
        // 深色主题配置 - 极致优雅
        return {
            theme: 'dark',
            themeVariables: {
                // 基础颜色 - 深色模式
                primaryColor: '#1e293b',
                primaryTextColor: '#f1f5f9',
                primaryBorderColor: ink,
                lineColor: '#94a3b8',
                secondaryColor: surface,
                tertiaryColor: '#1e1e1e',

                // 流程图
                mainBkg: '#1e293b',
                nodeBorder: ink,
                clusterBkg: '#0f172a',
                clusterBorder: '#475569',

                // 序列图
                actorBkg: surface,
                actorBorder: ink,
                actorTextColor: '#f1f5f9',
                signalColor: '#cbd5e1',
                signalTextColor: '#f1f5f9',
                labelBoxBkgColor: '#1e293b',
                labelBoxBorderColor: '#475569',
                labelTextColor: '#f1f5f9',

                // Gantt 图专属配置
                gridColor: '#334155',
                todayLineColor: reading,

                // 任务条颜色
                taskBkgColor: '#3b82f6',
                taskBorderColor: '#2563eb',
                taskTextColor: '#ffffff',
                taskTextOutsideColor: '#f1f5f9',
                taskTextLightColor: '#1e293b',
                taskTextDarkColor: '#f1f5f9',

                // Section 颜色
                sectionBkgColor: '#1e293b',
                sectionBkgColor2: surface,
                altSectionBkgColor: '#0f172a',

                // 已完成任务
                doneTaskBkgColor: '#10b981',
                doneTaskBorderColor: '#059669',

                // 进行中任务
                activeTaskBkgColor: '#3b82f6',
                activeTaskBorderColor: '#2563eb',

                // 重要任务
                critBkgColor: '#ef4444',
                critBorderColor: '#dc2626',

                // 文字颜色
                textColor: '#f1f5f9',
                fontSize: '16px',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji"'
            }
        };
    } else {
        // 浅色主题配置 - 极致优雅
        return {
            theme: 'base',
            themeVariables: {
                // 基础颜色 - 浅色模式
                primaryColor: surface,
                primaryTextColor: '#1e293b',
                primaryBorderColor: ink,
                lineColor: '#64748b',
                secondaryColor: surface,
                tertiaryColor: '#ffffff',

                // 流程图
                mainBkg: surface,
                nodeBorder: ink,
                clusterBkg: '#f9fafb',
                clusterBorder: '#d1d5db',

                // 序列图
                actorBkg: surface,
                actorBorder: ink,
                actorTextColor: '#1e293b',
                signalColor: '#475569',
                signalTextColor: '#0f172a',
                labelBoxBkgColor: '#ffffff',
                labelBoxBorderColor: '#e5e7eb',
                labelTextColor: '#1e293b',

                // Gantt 图专属配置
                gridColor: '#e2e8f0',
                todayLineColor: reading,

                // 任务条颜色
                taskBkgColor: '#3b82f6',
                taskBorderColor: '#2563eb',
                taskTextColor: '#ffffff',
                taskTextOutsideColor: '#1e293b',
                taskTextLightColor: '#ffffff',
                taskTextDarkColor: '#1e293b',

                // Section 颜色
                sectionBkgColor: '#f8fafc',
                sectionBkgColor2: '#f1f5f9',
                altSectionBkgColor: '#ffffff',

                // 已完成任务
                doneTaskBkgColor: '#10b981',
                doneTaskBorderColor: '#059669',

                // 进行中任务
                activeTaskBkgColor: '#3b82f6',
                activeTaskBorderColor: '#2563eb',

                // 重要任务
                critBkgColor: '#ef4444',
                critBorderColor: '#dc2626',

                // 文字颜色
                textColor: '#1e293b',
                fontSize: '16px',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji"'
            }
        };
    }
}

// 初始化 mermaid
export function initializeMermaid(mermaid) {
    const currentTheme = getCurrentTheme();
    const themeConfig = getMermaidThemeConfig(currentTheme);

    mermaid.initialize({
        startOnLoad: false,
        securityLevel: 'loose',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
        // 宽度适配配置
        maxWidth: '100%',
        useMaxWidth: true,
        ...themeConfig,
        flowchart: {
            curve: 'basis',
            htmlLabels: true,
            useMaxWidth: true,
            padding: 20
        },
        gantt: {
            useWidth: undefined,
            axisFormat: '%m-%d',
            topPadding: 50,
            sidePadding: 75,
            gridLineStartPadding: 10,
            fontSize: 14,
            sectionFontSize: 16,
            numberSectionStyles: 4,
            // 任务高度和间距
            barHeight: 32,
            barGap: 8,
            topAxis: true,
            // 左侧标签宽度
            leftPadding: 200
        },
        sequence: {
            diagramMarginX: 50,
            diagramMarginY: 30,
            actorMargin: 80,
            width: 200,
            height: 65,
            boxMargin: 15,
            boxTextMargin: 8,
            noteMargin: 15,
            messageMargin: 50
        },
        pie: {
            textPosition: 0.65
        },
        class: {
            padding: 20
        }
    });
}
