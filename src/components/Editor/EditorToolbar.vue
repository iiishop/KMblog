<template>
    <div class="ethereal-toolbar">
        <!-- 呼吸式背景光晕 -->
        <div class="toolbar-glow" :class="{ 'active': saveStatus === 'saving' }"></div>

        <div class="toolbar-content">
            <div class="toolbar-main">
                <!-- 左侧工具区域 - 自动换行 -->
                <div class="toolbar-tools">
                    <!-- 文件树切换 -->
                    <button @click="$emit('toggle-file-tree')" class="tool-btn tree-toggle" title="切换文件树">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 3h7l2 2h9v14H3z" />
                        </svg>
                        <span class="ripple"></span>
                    </button>

                    <!-- 文件名 -->
                    <div class="file-badge">
                        <div class="file-indicator"></div>
                        <span class="file-name">{{ fileName || '未选择文件' }}</span>
                    </div>

                    <div class="divider"></div>

                    <!-- 文本格式 -->
                    <div class="tool-group">
                        <button @click="insertFormat('bold')" class="tool-btn format-btn" title="粗体">
                            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
                                <path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z" />
                            </svg>
                        </button>
                        <button @click="insertFormat('italic')" class="tool-btn format-btn" title="斜体">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="19" y1="4" x2="10" y2="4" />
                                <line x1="14" y1="20" x2="5" y2="20" />
                                <line x1="15" y1="4" x2="9" y2="20" />
                            </svg>
                        </button>
                        <button @click="insertFormat('strikethrough')" class="tool-btn format-btn" title="删除线">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M17.5 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6.5" />
                                <line x1="3" y1="12" x2="21" y2="12" />
                            </svg>
                        </button>
                        <button @click="insertFormat('underline')" class="tool-btn format-btn" title="下划线">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M6 3v7a6 6 0 0012 0V3" />
                                <line x1="4" y1="21" x2="20" y2="21" />
                            </svg>
                        </button>
                    </div>

                    <div class="divider"></div>

                    <!-- 标题下拉 -->
                    <div class="dropdown" ref="headingDropdownRef">
                        <button @click="toggleHeadingDropdown" class="tool-btn format-btn"
                            :class="{ 'active': headingDropdownVisible }" title="标题">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M4 12h8m-8-6v12m8-12v12m4-6h4m-4-6v12" />
                            </svg>
                            <svg class="mini-arrow" :class="{ 'rotated': headingDropdownVisible }" viewBox="0 0 24 24"
                                fill="currentColor">
                                <path d="M7 10l5 5 5-5z" />
                            </svg>
                        </button>
                        <teleport to="body">
                            <transition name="dropdown-fade">
                                <div v-if="headingDropdownVisible" class="ethereal-dropdown compact-dropdown"
                                    :style="headingDropdownStyle">
                                    <div class="dropdown-backdrop"></div>
                                    <div class="dropdown-content">
                                        <button v-for="level in 6" :key="level" @click="insertHeading(level)"
                                            class="dropdown-item compact-item">
                                            <span class="heading-preview"
                                                :style="{ fontSize: `${20 - level * 2}px` }">H{{
                                                    level }}</span>
                                            <span class="item-label">{{ level }}级标题</span>
                                        </button>
                                    </div>
                                </div>
                            </transition>
                        </teleport>
                    </div>

                    <button @click="insertFormat('quote')" class="tool-btn format-btn" title="引用">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path
                                d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z" />
                        </svg>
                    </button>

                    <div class="divider"></div>

                    <!-- 颜色选择 -->
                    <div class="dropdown" ref="colorDropdownRef">
                        <button @click="toggleColorDropdown" class="tool-btn format-btn"
                            :class="{ 'active': colorDropdownVisible }" title="文字颜色">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
                            </svg>
                            <div class="color-indicator" :style="{ background: selectedColor }"></div>
                        </button>
                        <teleport to="body">
                            <transition name="dropdown-fade">
                                <div v-if="colorDropdownVisible" class="ethereal-dropdown color-dropdown"
                                    :style="colorDropdownStyle">
                                    <div class="dropdown-backdrop"></div>
                                    <div class="dropdown-content">
                                        <div class="color-grid">
                                            <button v-for="color in colorPalette" :key="color.value"
                                                @click="insertColor(color.value)" class="color-swatch"
                                                :style="{ background: color.value }" :title="color.name">
                                                <span v-if="selectedColor === color.value" class="check-mark">✓</span>
                                            </button>
                                        </div>
                                        <div class="custom-color-section">
                                            <input type="color" v-model="customColor" @change="insertColor(customColor)"
                                                class="custom-color-input" />
                                            <span class="custom-color-label">自定义颜色</span>
                                        </div>
                                    </div>
                                </div>
                            </transition>
                        </teleport>
                    </div>

                    <!-- 背景颜色选择 -->
                    <div class="dropdown" ref="bgColorDropdownRef">
                        <button @click="toggleBgColorDropdown" class="tool-btn format-btn"
                            :class="{ 'active': bgColorDropdownVisible }" title="背景颜色">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="18" height="18" rx="2" />
                                <path d="M3 3l18 18" stroke-width="1" />
                            </svg>
                            <div class="color-indicator" :style="{ background: selectedBgColor }"></div>
                        </button>
                        <teleport to="body">
                            <transition name="dropdown-fade">
                                <div v-if="bgColorDropdownVisible" class="ethereal-dropdown color-dropdown"
                                    :style="bgColorDropdownStyle">
                                    <div class="dropdown-backdrop"></div>
                                    <div class="dropdown-content">
                                        <div class="color-grid">
                                            <button v-for="color in bgColorPalette" :key="color.value"
                                                @click="insertBgColor(color.value)" class="color-swatch"
                                                :style="{ background: color.value }" :title="color.name">
                                                <span v-if="selectedBgColor === color.value" class="check-mark">✓</span>
                                            </button>
                                        </div>
                                        <div class="custom-color-section">
                                            <input type="color" v-model="customBgColor"
                                                @change="insertBgColor(customBgColor)" class="custom-color-input" />
                                            <span class="custom-color-label">自定义背景色</span>
                                        </div>
                                    </div>
                                </div>
                            </transition>
                        </teleport>
                    </div>

                    <!-- 字体大小 -->
                    <div class="dropdown" ref="fontSizeDropdownRef">
                        <button @click="toggleFontSizeDropdown" class="tool-btn format-btn"
                            :class="{ 'active': fontSizeDropdownVisible }" title="字体大小">
                            <span class="text-icon">A</span>
                        </button>
                        <teleport to="body">
                            <transition name="dropdown-fade">
                                <div v-if="fontSizeDropdownVisible" class="ethereal-dropdown compact-dropdown"
                                    :style="fontSizeDropdownStyle">
                                    <div class="dropdown-backdrop"></div>
                                    <div class="dropdown-content">
                                        <button v-for="size in fontSizes" :key="size.value"
                                            @click="insertFontSize(size.value)" class="dropdown-item compact-item">
                                            <span class="font-size-preview" :style="{ fontSize: size.value }">A</span>
                                            <span class="item-label">{{ size.name }} ({{ size.value }})</span>
                                        </button>
                                    </div>
                                </div>
                            </transition>
                        </teleport>
                    </div>

                    <button @click="insertFormat('code')" class="tool-btn format-btn" title="代码块">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="16 18 22 12 16 6" />
                            <polyline points="8 6 2 12 8 18" />
                        </svg>
                    </button>

                    <div class="divider"></div>

                    <!-- 链接和图片 -->
                    <div class="tool-group">
                        <button @click="insertFormat('link')" class="tool-btn format-btn" title="链接">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                            </svg>
                        </button>
                        <button @click="insertFormat('image')" class="tool-btn format-btn" title="图片">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="18" height="18" rx="2" />
                                <circle cx="8.5" cy="8.5" r="1.5" />
                                <path d="M21 15l-5-5L5 21" />
                            </svg>
                        </button>
                    </div>

                    <div class="divider"></div>

                    <!-- 列表 -->
                    <div class="tool-group">
                        <button @click="insertFormat('ul')" class="tool-btn format-btn" title="无序列表">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="8" y1="6" x2="21" y2="6" />
                                <line x1="8" y1="12" x2="21" y2="12" />
                                <line x1="8" y1="18" x2="21" y2="18" />
                                <line x1="3" y1="6" x2="3.01" y2="6" />
                                <line x1="3" y1="12" x2="3.01" y2="12" />
                                <line x1="3" y1="18" x2="3.01" y2="18" />
                            </svg>
                        </button>
                        <button @click="insertFormat('ol')" class="tool-btn format-btn" title="有序列表">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="10" y1="6" x2="21" y2="6" />
                                <line x1="10" y1="12" x2="21" y2="12" />
                                <line x1="10" y1="18" x2="21" y2="18" />
                                <path d="M4 6h1v4" />
                                <path d="M4 10h2" />
                                <path d="M6 18H4c0-1 2-2 2-3s-1-1.5-2-1" />
                            </svg>
                        </button>
                        <button @click="insertFormat('task')" class="tool-btn format-btn" title="任务列表">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="18" height="18" rx="2" />
                                <path d="M9 11l3 3L22 4" />
                            </svg>
                        </button>
                    </div>

                    <button @click="insertFormat('table')" class="tool-btn format-btn" title="表格">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" />
                            <line x1="3" y1="9" x2="21" y2="9" />
                            <line x1="3" y1="15" x2="21" y2="15" />
                            <line x1="12" y1="3" x2="12" y2="21" />
                        </svg>
                    </button>

                    <div class="divider"></div>

                    <!-- Block插入 -->
                    <div class="dropdown" ref="dropdownRef">
                        <button @click="toggleDropdown" class="tool-btn block-btn"
                            :class="{ 'active': dropdownVisible }" title="插入Block">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="12" y1="8" x2="12" y2="16" />
                                <line x1="8" y1="12" x2="16" y2="12" />
                            </svg>
                            <span class="label">Block</span>
                            <svg class="arrow" :class="{ 'rotated': dropdownVisible }" viewBox="0 0 24 24"
                                fill="currentColor">
                                <path d="M7 10l5 5 5-5z" />
                            </svg>
                        </button>
                        <teleport to="body">
                            <transition name="dropdown-fade">
                                <div v-if="dropdownVisible" class="ethereal-dropdown" :style="dropdownStyle">
                                    <div class="dropdown-backdrop"></div>
                                    <div class="dropdown-content">
                                        <button v-for="(template, key) in blockTemplates" :key="key"
                                            @click="insertBlock(key)" class="dropdown-item">
                                            <span class="item-icon" v-html="getBlockIcon(key)"></span>
                                            <span class="item-label">{{ getBlockDisplayName(key) }}</span>
                                            <span class="item-hint">{{ getBlockHint(key) }}</span>
                                        </button>
                                    </div>
                                </div>
                            </transition>
                        </teleport>
                    </div>

                    <div class="divider"></div>

                    <!-- 文字对齐 -->
                    <div class="tool-group">
                        <button @click="insertFormat('align-left')" class="tool-btn format-btn" title="左对齐">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="17" y1="10" x2="3" y2="10" />
                                <line x1="21" y1="6" x2="3" y2="6" />
                                <line x1="21" y1="14" x2="3" y2="14" />
                                <line x1="17" y1="18" x2="3" y2="18" />
                            </svg>
                        </button>
                        <button @click="insertFormat('align-center')" class="tool-btn format-btn" title="居中对齐">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="10" x2="6" y2="10" />
                                <line x1="21" y1="6" x2="3" y2="6" />
                                <line x1="21" y1="14" x2="3" y2="14" />
                                <line x1="18" y1="18" x2="6" y2="18" />
                            </svg>
                        </button>
                        <button @click="insertFormat('align-right')" class="tool-btn format-btn" title="右对齐">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="21" y1="10" x2="7" y2="10" />
                                <line x1="21" y1="6" x2="3" y2="6" />
                                <line x1="21" y1="14" x2="3" y2="14" />
                                <line x1="21" y1="18" x2="7" y2="18" />
                            </svg>
                        </button>
                    </div>

                    <div class="divider"></div>

                    <!-- 高级格式 -->
                    <div class="tool-group">
                        <button @click="insertFormat('superscript')" class="tool-btn format-btn" title="上标">
                            <span class="text-icon">X<sup>2</sup></span>
                        </button>
                        <button @click="insertFormat('subscript')" class="tool-btn format-btn" title="下标">
                            <span class="text-icon">X<sub>2</sub></span>
                        </button>
                        <button @click="insertFormat('mark')" class="tool-btn format-btn" title="高亮标记">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="5" width="18" height="14" rx="2" fill="rgba(245, 158, 11, 0.3)" />
                                <line x1="7" y1="10" x2="17" y2="10" />
                                <line x1="7" y1="14" x2="14" y2="14" />
                            </svg>
                        </button>
                    </div>

                    <div class="divider"></div>

                    <!-- 特殊符号 -->
                    <div class="dropdown" ref="symbolDropdownRef">
                        <button @click="toggleSymbolDropdown" class="tool-btn format-btn"
                            :class="{ 'active': symbolDropdownVisible }" title="特殊符号">
                            <span class="text-icon">Ω</span>
                        </button>
                        <teleport to="body">
                            <transition name="dropdown-fade">
                                <div v-if="symbolDropdownVisible" class="ethereal-dropdown symbol-dropdown"
                                    :style="symbolDropdownStyle">
                                    <div class="dropdown-backdrop"></div>
                                    <div class="dropdown-content">
                                        <div class="symbol-grid">
                                            <button v-for="symbol in commonSymbols" :key="symbol"
                                                @click="insertSymbol(symbol)" class="symbol-btn" :title="symbol">
                                                {{ symbol }}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </transition>
                        </teleport>
                    </div>

                    <button @click="insertFormat('hr')" class="tool-btn format-btn" title="分隔线">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="3" y1="12" x2="21" y2="12" />
                        </svg>
                    </button>
                </div>

                <!-- 右侧操作区域 - 固定不换行 -->
                <div class="toolbar-actions">
                    <div class="save-indicator" :class="saveStatusClass">
                        <div class="status-dot"></div>
                        <span class="status-text">{{ saveStatusText }}</span>
                    </div>

                    <!-- Theme Toggle Button -->
                    <button @click="toggleTheme" class="tool-btn theme-toggle-btn"
                        :title="isDarkMode ? '切换到浅色模式' : '切换到深色模式'">
                        <svg v-if="isDarkMode" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="2">
                            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                        </svg>
                        <svg v-else class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="5" />
                            <line x1="12" y1="1" x2="12" y2="3" />
                            <line x1="12" y1="21" x2="12" y2="23" />
                            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                            <line x1="1" y1="12" x2="3" y2="12" />
                            <line x1="21" y1="12" x2="23" y2="12" />
                            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                        </svg>
                    </button>

                    <button @click="$emit('save')" class="tool-btn save-btn"
                        :class="{ 'disabled': saveStatus === 'saved' }" :disabled="saveStatus === 'saved'"
                        title="保存 (Ctrl+S)">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                            <polyline points="17 21 17 13 7 13 7 21" />
                            <polyline points="7 3 7 8 15 8" />
                        </svg>
                        <span class="label">保存</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useTheme } from '@/composables/useTheme';

const props = defineProps({
    saveStatus: {
        type: String,
        default: 'saved',
        validator: (value) => ['saved', 'saving', 'unsaved'].includes(value)
    },
    fileName: {
        type: String,
        default: ''
    },
    lastSaveTime: {
        type: Number,
        default: null
    }
});

const emit = defineEmits(['save', 'insert-format', 'insert-block', 'toggle-file-tree']);

// Theme management
const { currentMode, isDarkMode, toggleTheme } = useTheme();

// Dropdown states
const dropdownVisible = ref(false);
const dropdownRef = ref(null);
const dropdownStyle = ref({});

const headingDropdownVisible = ref(false);
const headingDropdownRef = ref(null);
const headingDropdownStyle = ref({});

const colorDropdownVisible = ref(false);
const colorDropdownRef = ref(null);
const colorDropdownStyle = ref({});
const selectedColor = ref('#000000');
const customColor = ref('#000000');

const bgColorDropdownVisible = ref(false);
const bgColorDropdownRef = ref(null);
const bgColorDropdownStyle = ref({});
const selectedBgColor = ref('#FFFF00');
const customBgColor = ref('#FFFF00');

const fontSizeDropdownVisible = ref(false);
const fontSizeDropdownRef = ref(null);
const fontSizeDropdownStyle = ref({});

const symbolDropdownVisible = ref(false);
const symbolDropdownRef = ref(null);
const symbolDropdownStyle = ref({});

// Color palette
const colorPalette = [
    { name: '黑色', value: '#000000' },
    { name: '深灰', value: '#4B5563' },
    { name: '灰色', value: '#9CA3AF' },
    { name: '红色', value: '#EF4444' },
    { name: '橙色', value: '#F97316' },
    { name: '黄色', value: '#F59E0B' },
    { name: '绿色', value: '#10B981' },
    { name: '青色', value: '#06B6D4' },
    { name: '蓝色', value: '#3B82F6' },
    { name: '靛蓝', value: '#6366F1' },
    { name: '紫色', value: '#8B5CF6' },
    { name: '粉色', value: '#EC4899' }
];

// Background color palette
const bgColorPalette = [
    { name: '黄色高亮', value: '#FFFF00' },
    { name: '绿色高亮', value: '#90EE90' },
    { name: '蓝色高亮', value: '#ADD8E6' },
    { name: '粉色高亮', value: '#FFB6C1' },
    { name: '橙色高亮', value: '#FFD700' },
    { name: '紫色高亮', value: '#DDA0DD' },
    { name: '浅灰', value: '#F0F0F0' },
    { name: '浅红', value: '#FFE4E1' },
    { name: '浅绿', value: '#F0FFF0' },
    { name: '浅蓝', value: '#F0F8FF' },
    { name: '浅黄', value: '#FFFACD' },
    { name: '浅紫', value: '#F8F0FF' }
];

// Font sizes
const fontSizes = [
    { name: '极小', value: '12px', html: '<span style="font-size: 12px">' },
    { name: '小', value: '14px', html: '<span style="font-size: 14px">' },
    { name: '正常', value: '16px', html: '<span style="font-size: 16px">' },
    { name: '中', value: '18px', html: '<span style="font-size: 18px">' },
    { name: '大', value: '20px', html: '<span style="font-size: 20px">' },
    { name: '特大', value: '24px', html: '<span style="font-size: 24px">' },
    { name: '超大', value: '28px', html: '<span style="font-size: 28px">' }
];

// Common symbols
const commonSymbols = [
    '→', '←', '↑', '↓', '↔', '↕',
    '✓', '✗', '★', '☆', '♥', '♦',
    '©', '®', '™', '§', '¶', '†',
    '°', '±', '×', '÷', '≈', '≠',
    '≤', '≥', '∞', '∑', '∏', '√',
    'α', 'β', 'γ', 'δ', 'π', 'Ω'
];

// Block templates
const blockTemplates = {
    'carousel': '```carousel\n/path/to/image1.jpg | 图片1描述\n/path/to/image2.jpg | 图片2描述\n/path/to/image3.jpg | 图片3描述\n```',
    'bilibili-video': '```bilibili-video\nhttps://www.bilibili.com/video/BV...\n```',
    'steam-game': '```steam-game\nhttps://store.steampowered.com/app/...\n```',
    'bangumi-card': '```bangumi-card\nhttps://bgm.tv/subject/...\n```',
    'github-repo': '```github-repo\nhttps://github.com/user/repo\n```',
    'xiaohongshu-note': '```xiaohongshu-note\nhttps://www.xiaohongshu.com/explore/...\n```',
    'mermaid': '```mermaid\ngraph TD\n  A[开始] --> B[结束]\n```'
};

const getBlockIcon = (key) => {
    const icons = {
        'carousel': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="14" rx="2"/><path d="M7 3v14"/><path d="M17 3v14"/><circle cx="12" cy="10" r="2"/></svg>`,
        'bilibili-video': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="15" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/></svg>`,
        'steam-game': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4l-3 3"/><path d="M12 8v4l3-3"/></svg>`,
        'bangumi-card': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>`,
        'github-repo': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>`,
        'xiaohongshu-note': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`,
        'mermaid': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`
    };
    return icons[key] || `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/></svg>`;
};

const getBlockDisplayName = (key) => {
    const names = {
        'carousel': '图片轮播',
        'bilibili-video': 'Bilibili视频',
        'steam-game': 'Steam游戏',
        'bangumi-card': 'Bangumi卡片',
        'github-repo': 'GitHub仓库',
        'xiaohongshu-note': '小红书笔记',
        'mermaid': 'Mermaid图表'
    };
    return names[key] || key;
};

const getBlockHint = (key) => {
    const hints = {
        'carousel': '图片轮播展示',
        'bilibili-video': '嵌入视频播放器',
        'steam-game': '展示游戏信息',
        'bangumi-card': '动漫/影视卡片',
        'github-repo': '仓库信息卡片',
        'xiaohongshu-note': '笔记内容展示',
        'mermaid': '流程图/图表'
    };
    return hints[key] || '';
};

// Computed
const saveStatusClass = computed(() => {
    return {
        'status-saved': props.saveStatus === 'saved',
        'status-saving': props.saveStatus === 'saving',
        'status-unsaved': props.saveStatus === 'unsaved'
    };
});

const saveStatusText = computed(() => {
    if (props.lastSaveTime && props.saveStatus === 'saved') {
        const now = Date.now();
        const diff = now - props.lastSaveTime;

        if (diff < 60000) { // 小于1分钟
            return '刚刚保存';
        } else if (diff < 3600000) { // 小于1小时
            const minutes = Math.floor(diff / 60000);
            return `${minutes}分钟前`;
        } else if (diff < 86400000) { // 小于1天
            const hours = Math.floor(diff / 3600000);
            return `${hours}小时前`;
        } else {
            const date = new Date(props.lastSaveTime);
            return date.toLocaleString('zh-CN', {
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }

    switch (props.saveStatus) {
        case 'saved':
            return '已保存';
        case 'saving':
            return '保存中';
        case 'unsaved':
            return '未保存';
        default:
            return '';
    }
});

// Methods
const insertFormat = (format) => {
    emit('insert-format', format);
};

const insertBlock = (blockType) => {
    emit('insert-block', blockType);
    dropdownVisible.value = false;
};

const insertHeading = (level) => {
    emit('insert-format', `heading-${level}`);
    headingDropdownVisible.value = false;
};

const insertColor = (color) => {
    selectedColor.value = color;
    emit('insert-format', `color:${color}`);
    colorDropdownVisible.value = false;
};

const insertBgColor = (color) => {
    selectedBgColor.value = color;
    emit('insert-format', `bgcolor:${color}`);
    bgColorDropdownVisible.value = false;
};

const insertFontSize = (size) => {
    emit('insert-format', `fontsize:${size}`);
    fontSizeDropdownVisible.value = false;
};

const insertSymbol = (symbol) => {
    emit('insert-format', `symbol:${symbol}`);
    symbolDropdownVisible.value = false;
};

const updateDropdownPosition = (ref, style, minWidth = '280px') => {
    if (!ref.value) return;

    const button = ref.value.querySelector('button');
    if (!button) return;

    const rect = button.getBoundingClientRect();
    style.value = {
        position: 'fixed',
        top: `${rect.bottom + 8}px`,
        left: `${rect.left}px`,
        minWidth
    };
};

const toggleDropdown = () => {
    dropdownVisible.value = !dropdownVisible.value;
    if (dropdownVisible.value) {
        updateDropdownPosition(dropdownRef, dropdownStyle);
    }
};

const toggleHeadingDropdown = () => {
    headingDropdownVisible.value = !headingDropdownVisible.value;
    if (headingDropdownVisible.value) {
        updateDropdownPosition(headingDropdownRef, headingDropdownStyle, '180px');
    }
};

const toggleColorDropdown = () => {
    colorDropdownVisible.value = !colorDropdownVisible.value;
    if (colorDropdownVisible.value) {
        updateDropdownPosition(colorDropdownRef, colorDropdownStyle, '240px');
    }
};

const toggleBgColorDropdown = () => {
    bgColorDropdownVisible.value = !bgColorDropdownVisible.value;
    if (bgColorDropdownVisible.value) {
        updateDropdownPosition(bgColorDropdownRef, bgColorDropdownStyle, '240px');
    }
};

const toggleFontSizeDropdown = () => {
    fontSizeDropdownVisible.value = !fontSizeDropdownVisible.value;
    if (fontSizeDropdownVisible.value) {
        updateDropdownPosition(fontSizeDropdownRef, fontSizeDropdownStyle, '180px');
    }
};

const toggleSymbolDropdown = () => {
    symbolDropdownVisible.value = !symbolDropdownVisible.value;
    if (symbolDropdownVisible.value) {
        updateDropdownPosition(symbolDropdownRef, symbolDropdownStyle, '280px');
    }
};

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
    const dropdownMenus = document.querySelectorAll('.ethereal-dropdown');
    const clickedInsideDropdown = Array.from(dropdownMenus).some(menu => menu.contains(event.target));

    if (clickedInsideDropdown) return;

    if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
        dropdownVisible.value = false;
    }
    if (headingDropdownRef.value && !headingDropdownRef.value.contains(event.target)) {
        headingDropdownVisible.value = false;
    }
    if (colorDropdownRef.value && !colorDropdownRef.value.contains(event.target)) {
        colorDropdownVisible.value = false;
    }
    if (bgColorDropdownRef.value && !bgColorDropdownRef.value.contains(event.target)) {
        bgColorDropdownVisible.value = false;
    }
    if (fontSizeDropdownRef.value && !fontSizeDropdownRef.value.contains(event.target)) {
        fontSizeDropdownVisible.value = false;
    }
    if (symbolDropdownRef.value && !symbolDropdownRef.value.contains(event.target)) {
        symbolDropdownVisible.value = false;
    }
};

// Lifecycle
onMounted(() => {
    document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
    document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.ethereal-toolbar {
    position: relative;
    background: var(--theme-panel-bg);
    border-bottom: 1px solid var(--theme-panel-border);
    backdrop-filter: blur(20px) saturate(180%);
    isolation: isolate;
    z-index: 100;
    transition: var(--theme-transition-colors);
}

.toolbar-glow {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 0%, rgba(245, 158, 11, 0.08) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;
}

.toolbar-glow.active {
    opacity: 1;
    animation: breathe 2s ease-in-out infinite;
}

@keyframes breathe {

    0%,
    100% {
        opacity: 0.6;
    }

    50% {
        opacity: 1;
    }
}

.toolbar-content {
    padding: 13px 21px;
    position: relative;
}

.toolbar-main {
    display: flex;
    align-items: flex-start;
    gap: 13px;
}

.toolbar-tools {
    flex: 1;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    min-width: 0;
}

.toolbar-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
}

.tool-btn {
    position: relative;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 13px;
    border: none;
    background: var(--theme-surface-default);
    color: var(--theme-panel-text);
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    font-family: 'Inter', -apple-system, sans-serif;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    white-space: nowrap;
    overflow: hidden;
    box-shadow: 0 1px 2px var(--theme-shadow-sm);
}

.tool-btn:hover {
    background: var(--theme-surface-hover);
    color: var(--theme-heading-text);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px var(--theme-shadow-md);
}

.tool-btn:active {
    transform: translateY(0);
    box-shadow:
        0 1px 3px rgba(0, 0, 0, 0.1),
        inset 0 1px 2px rgba(0, 0, 0, 0.05);
}

.tool-btn .icon {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.tool-btn:hover .icon {
    transform: scale(1.1);
}

.tool-btn .label {
    font-size: 13px;
    letter-spacing: -0.01em;
}

.text-icon {
    font-size: 14px;
    font-weight: 600;
    line-height: 1;
}

.format-btn {
    padding: 8px;
    min-width: 34px;
    justify-content: center;
}

.format-btn:hover {
    background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
    color: #ffffff;
}

.format-btn:hover .icon {
    filter: drop-shadow(0 2px 4px rgba(245, 158, 11, 0.3));
}

.tree-toggle {
    position: relative;
    overflow: hidden;
}

.tree-toggle .ripple {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle, rgba(245, 158, 11, 0.3) 0%, transparent 70%);
    opacity: 0;
    transform: scale(0);
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.tree-toggle:active .ripple {
    opacity: 1;
    transform: scale(2);
    transition: all 0s;
}

.file-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 13px;
    background: var(--theme-nav-active-bg);
    border-radius: 8px;
    border: 1px solid var(--theme-border-light);
    max-width: 240px;
    transition: var(--theme-transition-colors);
}

.file-indicator {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
    box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {

    0%,
    100% {
        opacity: 1;
        transform: scale(1);
    }

    50% {
        opacity: 0.6;
        transform: scale(0.9);
    }
}

.file-name {
    font-size: 13px;
    font-weight: 600;
    color: var(--theme-heading-text);
    letter-spacing: -0.01em;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: var(--theme-transition-colors);
}

.divider {
    width: 1px;
    height: 21px;
    background: var(--theme-divider);
    margin: 0 4px;
    transition: var(--theme-transition-colors);
}

.tool-group {
    display: flex;
    gap: 4px;
    padding: 4px;
    background: var(--theme-surface-hover);
    border-radius: 10px;
    border: 1px solid var(--theme-border-light);
    transition: var(--theme-transition-colors);
}

.mini-arrow {
    width: 12px;
    height: 12px;
    margin-left: -4px;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mini-arrow.rotated {
    transform: rotate(180deg);
}

.color-indicator {
    position: absolute;
    bottom: 2px;
    left: 50%;
    transform: translateX(-50%);
    width: 16px;
    height: 3px;
    border-radius: 2px;
    transition: all 0.3s;
}

.block-btn {
    background: var(--theme-nav-active-bg);
    border: 1px solid var(--theme-border-light);
    color: var(--theme-primary);
    transition: var(--theme-transition-colors);
}

.block-btn:hover {
    background: var(--theme-gradient);
    color: #ffffff;
    border-color: transparent;
}

.block-btn.active {
    background: var(--theme-gradient);
    color: #ffffff;
    border-color: transparent;
}

/* Theme Toggle Button */
.theme-toggle-btn {
    background: var(--theme-nav-active-bg);
    border: 1px solid var(--theme-border-light);
    color: var(--theme-primary);
    transition: var(--theme-transition-colors);
}

.theme-toggle-btn:hover {
    background: var(--theme-gradient);
    color: #ffffff;
    border-color: transparent;
}

.block-btn .arrow {
    width: 16px;
    height: 16px;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.block-btn .arrow.rotated {
    transform: rotate(180deg);
}

/* Dropdown styles */
.ethereal-dropdown {
    position: fixed;
    z-index: 10000;
    filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.12));
}

.dropdown-backdrop {
    position: absolute;
    inset: -8px;
    background: var(--theme-panel-bg);
    border-radius: 16px;
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--theme-panel-border);
    transition: var(--theme-transition-colors);
}

.dropdown-content {
    position: relative;
    padding: 8px;
    max-height: 400px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: rgba(148, 163, 184, 0.3) transparent;
}

.dropdown-content::-webkit-scrollbar {
    width: 6px;
}

.dropdown-content::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.3);
    border-radius: 3px;
}

.dropdown-item {
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 13px;
    border: none;
    background: transparent;
    color: var(--theme-panel-text);
    text-align: left;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    border-radius: 10px;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    width: 100%;
    position: relative;
    overflow: hidden;
}

.dropdown-item::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--theme-nav-active-bg);
    opacity: 0;
    transition: opacity 0.2s;
}

.dropdown-item:hover::before {
    opacity: 1;
}

.dropdown-item:hover {
    color: var(--theme-heading-text);
    transform: translateX(4px);
}

.item-icon {
    font-size: 20px;
    flex-shrink: 0;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-item:hover .item-icon {
    transform: scale(1.2) rotate(5deg);
}

.item-label {
    flex: 1;
    font-weight: 600;
    letter-spacing: -0.01em;
}

.item-hint {
    font-size: 11px;
    color: var(--theme-meta-text);
    font-weight: 400;
    transition: var(--theme-transition-colors);
}

/* Compact dropdown for headings */
.compact-dropdown .dropdown-content {
    padding: 6px;
}

.compact-item {
    padding: 10px 13px;
    gap: 10px;
}

.heading-preview {
    font-weight: 700;
    color: var(--theme-primary);
    min-width: 32px;
    text-align: center;
    transition: var(--theme-transition-colors);
}

.font-size-preview {
    font-weight: 700;
    color: var(--theme-primary);
    min-width: 32px;
    text-align: center;
    line-height: 1;
    transition: var(--theme-transition-colors);
}

/* Color dropdown */
.color-dropdown .dropdown-content {
    padding: 12px;
}

.color-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 8px;
    margin-bottom: 12px;
}

.color-swatch {
    width: 32px;
    height: 32px;
    border: 2px solid var(--theme-border-light);
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    color: white;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.color-swatch:hover {
    transform: scale(1.15);
    border-color: var(--theme-primary);
    box-shadow: 0 4px 12px var(--theme-shadow-md);
}

.custom-color-section {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-top: 12px;
    border-top: 1px solid var(--theme-border-light);
    transition: var(--theme-transition-colors);
}

.custom-color-input {
    width: 40px;
    height: 32px;
    border: 2px solid var(--theme-border-light);
    border-radius: 6px;
    cursor: pointer;
    transition: var(--theme-transition-colors);
}

.custom-color-label {
    font-size: 12px;
    color: var(--theme-meta-text);
    font-weight: 500;
    transition: var(--theme-transition-colors);
}

/* Symbol dropdown */
.symbol-dropdown .dropdown-content {
    padding: 12px;
}

.symbol-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 6px;
}

.symbol-btn {
    width: 36px;
    height: 36px;
    border: 1px solid var(--theme-border-light);
    background: var(--theme-surface-default);
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    color: var(--theme-panel-text);
}

.symbol-btn:hover {
    background: var(--theme-gradient);
    color: white;
    transform: scale(1.1);
    border-color: transparent;
}

/* Dropdown animations */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-fade-enter-from {
    opacity: 0;
    transform: translateY(-8px) scale(0.95);
}

.dropdown-fade-leave-to {
    opacity: 0;
    transform: translateY(8px) scale(0.95);
}

/* Save indicator */
.save-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 13px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: -0.01em;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.status-saved {
    background: rgba(34, 197, 94, 0.1);
    color: #16a34a;
}

.status-saved .status-dot {
    background: #22c55e;
    box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
}

.status-saving {
    background: rgba(245, 158, 11, 0.1);
    color: #d97706;
}

.status-saving .status-dot {
    background: #f59e0b;
    box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
    animation: saving-pulse 1s ease-in-out infinite;
}

@keyframes saving-pulse {

    0%,
    100% {
        transform: scale(1);
        opacity: 1;
    }

    50% {
        transform: scale(1.3);
        opacity: 0.7;
    }
}

.status-unsaved {
    background: rgba(239, 68, 68, 0.1);
    color: #dc2626;
}

.status-unsaved .status-dot {
    background: #ef4444;
    box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

.save-btn {
    background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
    color: #ffffff;
    font-weight: 600;
    box-shadow:
        0 4px 12px rgba(245, 158, 11, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.save-btn:hover {
    background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
    box-shadow:
        0 6px 20px rgba(245, 158, 11, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.save-btn.disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

.save-btn.disabled:hover {
    background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
    box-shadow:
        0 4px 12px rgba(245, 158, 11, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    transform: none;
}

@media (max-width: 768px) {
    .toolbar-content {
        padding: 8px 13px;
    }

    .toolbar-main {
        flex-direction: column;
        gap: 8px;
    }

    .toolbar-actions {
        width: 100%;
        justify-content: space-between;
    }

    .tool-btn .label {
        display: none;
    }

    .file-badge {
        max-width: 120px;
    }

    .tool-group {
        gap: 2px;
        padding: 2px;
    }

    .format-btn {
        padding: 6px;
        min-width: 28px;
    }

    .item-hint {
        display: none;
    }
}
</style>
