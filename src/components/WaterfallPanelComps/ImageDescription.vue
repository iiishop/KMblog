<template>
    <div v-if="hasGalleryDescription(content)" class="modal-description-section">
        <div class="description-header">
            <h2 class="description-title">图片描述</h2>
        </div>
        <div class="description-content">
            <!-- Markdown 渲染 - 使用完整的渲染系统 -->
            <MarkdownContent :content="content" class="markdown-body" />
        </div>

        <!-- 评论区域 -->
        <div class="comments-section">
            <UtterancesComments :issueTitle="`图片: ${image.alt || image.src}`" />
        </div>
    </div></template>

<script setup>
import MarkdownContent from '@/components/MarkdownPanelComps/MarkdownContent.vue';
import UtterancesComments from '@/components/UtterancesComments.vue';
import { hasGalleryDescription } from '@/utils/galleryImage';
defineProps({ content: { type: String, default: '' }, image: { type: Object, required: true } });
</script>

<style scoped>

.modal-description-section {
    flex: 0 0 40%;
    background: #fafafa;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    border-left: 1px solid #e8e8e8;
}

.description-header {
    padding: 2rem 2.5rem 1rem;
    background: linear-gradient(180deg, #fff 0%, #fafafa 100%);
    border-bottom: 1px solid #e8e8e8;
    flex-shrink: 0;
}

.description-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #222;
    letter-spacing: -0.02em;
}

.description-content {
    padding: 2rem 2.5rem;
    flex: 1;
}

.comments-section {
    padding: 0 2.5rem 2rem;
    border-top: 1px solid #e8e8e8;
    margin-top: 1rem;
}

.comments-section :deep(.utterances-comments) {
    margin: 1rem 0 0 0;
    padding: 1.5rem;
    background: #fff;
}

.markdown-body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    font-size: 0.95rem;
    line-height: 1.8;
    color: #333;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3 {
    font-weight: 600;
    color: #222;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
}

.markdown-body h1 {
    font-size: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
}

.markdown-body h2 {
    font-size: 1.3rem;
}

.markdown-body h3 {
    font-size: 1.1rem;
}

.markdown-body p {
    margin-bottom: 1rem;
    color: #333;
}

.markdown-body code {
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    background: #f5f5f5;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-size: 0.9em;
    color: #e83e8c;
}

.markdown-body pre {
    background: #f8f8f8;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 1rem 0;
    border: 1px solid #eee;
}

.markdown-body pre code {
    background: none;
    padding: 0;
    color: #333;
}

.markdown-body a {
    color: #ff2442;
    text-decoration: none;
}

.markdown-body a:hover {
    text-decoration: underline;
}

.markdown-body img {
    max-width: 100%;
    border-radius: 8px;
    margin: 1rem 0;
}

.markdown-body blockquote {
    border-left: 3px solid #ff2442;
    padding-left: 1rem;
    margin: 1rem 0;
    color: #666;
    font-style: italic;
}

.modal-description-section::-webkit-scrollbar {
    width: 6px;
}

.modal-description-section::-webkit-scrollbar-track {
    background: #f5f5f5;
}

.modal-description-section::-webkit-scrollbar-thumb {
    background: #ddd;
    border-radius: 3px;
}

.modal-description-section::-webkit-scrollbar-thumb:hover {
    background: #ccc;
}

.modal-description-section :deep(.bili-embed-neo),
.modal-description-section :deep(.steam-card),
.modal-description-section :deep(.xhs-embed-container),
.modal-description-section :deep(.bangumi-card) {
    margin: 1.5rem 0 !important;
}

.modal-description-section :deep(.bili-card-glass) {
    flex-direction: column !important;
    padding: 0.75rem !important;
    gap: 0.75rem !important;
}

.modal-description-section :deep(.bili-card-glass .media-column) {
    flex: none !important;
    width: 100% !important;
    max-width: 100% !important;
}

.modal-description-section :deep(.bili-card-glass .data-column) {
    width: 100% !important;
}

.modal-description-section :deep(.bili-card-glass .video-title) {
    font-size: 14px !important;
    margin-bottom: 8px !important;
}

.modal-description-section :deep(.bili-card-glass .video-description-deck) {
    padding: 6px 10px !important;
    margin-bottom: 10px !important;
}

.modal-description-section :deep(.bili-card-glass .deck-content) {
    font-size: 12px !important;
    -webkit-line-clamp: 2 !important;
}

.modal-description-section :deep(.bili-card-glass .stats-matrix) {
    grid-template-columns: 1fr 1fr !important;
    gap: 6px 10px !important;
    margin-bottom: 12px !important;
}

.modal-description-section :deep(.bili-card-glass .stat-info) {
    font-size: 9px !important;
}

.modal-description-section :deep(.bili-card-glass .data-footer) {
    padding-top: 10px !important;
    gap: 10px !important;
}

.modal-description-section :deep(.bili-card-glass .cyclotron-avatar) {
    width: 36px !important;
    height: 36px !important;
}

.modal-description-section :deep(.bili-card-glass .author-id) {
    font-size: 12px !important;
}

.modal-description-section :deep(.bili-card-glass .creator-bio) {
    font-size: 9px !important;
    max-width: 100% !important;
}

.modal-description-section :deep(.bili-card-glass .feedback-sector) {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 8px !important;
}

.modal-description-section :deep(.steam-card .card-content) {
    flex-direction: column !important;
    padding: 10px !important;
    gap: 12px !important;
}

.modal-description-section :deep(.steam-card .left-col) {
    width: 100% !important;
    max-width: 100% !important;
}

.modal-description-section :deep(.steam-card .right-col) {
    width: 100% !important;
}

.modal-description-section :deep(.steam-card .game-title) {
    font-size: 1.1rem !important;
}

.modal-description-section :deep(.steam-card .meta-row) {
    font-size: 0.75rem !important;
    flex-wrap: wrap !important;
    gap: 6px !important;
}

.modal-description-section :deep(.steam-card .tags-row) {
    gap: 4px !important;
}

.modal-description-section :deep(.steam-card .tag) {
    font-size: 0.65rem !important;
    padding: 1px 5px !important;
}

.modal-description-section :deep(.steam-card .game-desc) {
    font-size: 0.75rem !important;
    -webkit-line-clamp: 2 !important;
}

.modal-description-section :deep(.steam-card .action-row) {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 10px !important;
    padding: 6px 10px !important;
}

.modal-description-section :deep(.steam-card .price-block) {
    justify-content: center !important;
}

.modal-description-section :deep(.steam-card .store-btn) {
    width: 100% !important;
    justify-content: center !important;
    padding: 8px 14px !important;
    font-size: 0.85rem !important;
}

.modal-description-section :deep(.xhs-card) {
    flex-direction: column !important;
    padding: 0.75rem !important;
    gap: 0.75rem !important;
}

.modal-description-section :deep(.xhs-card .media-area) {
    flex: none !important;
    width: 100% !important;
    max-width: 100% !important;
    box-shadow: 8px 8px 0 var(--theme-red-deep) !important;
}

.modal-description-section :deep(.xhs-card .content-area) {
    width: 100% !important;
}

.modal-description-section :deep(.xhs-card .xhs-header) {
    gap: 8px !important;
    margin-bottom: 1rem !important;
}

.modal-description-section :deep(.xhs-card .brand-tag) {
    font-size: 9px !important;
    letter-spacing: 2px !important;
    padding: 2px 6px !important;
}

.modal-description-section :deep(.xhs-card .note-title) {
    font-size: 1.3rem !important;
    margin-bottom: 1rem !important;
}

.modal-description-section :deep(.xhs-card .note-abstract) {
    font-size: 0.8rem !important;
    max-height: 80px !important;
    margin-bottom: 1.5rem !important;
}

.modal-description-section :deep(.xhs-card .chips-left) {
    gap: 8px !important;
}

.modal-description-section :deep(.xhs-card .tag-chip) {
    font-size: 8px !important;
    padding: 2px 8px !important;
}

.modal-description-section :deep(.xhs-card .meta-footer) {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 12px !important;
    margin-top: 1rem !important;
}

.modal-description-section :deep(.xhs-card .user-avatar) {
    width: 24px !important;
    height: 24px !important;
}

.modal-description-section :deep(.xhs-card .user-name) {
    font-size: 0.75rem !important;
}

.modal-description-section :deep(.xhs-card .stats-row) {
    width: 100% !important;
    justify-content: flex-start !important;
    gap: 15px !important;
}

.modal-description-section :deep(.xhs-card .stat-pill) {
    font-size: 9px !important;
    gap: 4px !important;
}

.modal-description-section :deep(.bangumi-card .card-content) {
    flex-direction: column !important;
    padding: 0.75rem !important;
    gap: 0.75rem !important;
}

.modal-description-section :deep(.bangumi-card .cover-column) {
    width: 100% !important;
    max-width: 160px !important;
    margin: 0 auto !important;
    gap: 0.75rem !important;
}

.modal-description-section :deep(.bangumi-card .cover-wrapper) {
    border-radius: 10px !important;
}

.modal-description-section :deep(.bangumi-card .cover-img) {
    min-height: 120px !important;
    border-radius: 10px !important;
}

.modal-description-section :deep(.bangumi-card .action-btn) {
    padding: 6px 8px !important;
    font-size: 0.75rem !important;
    gap: 4px !important;
}

.modal-description-section :deep(.bangumi-card .btn-icon svg) {
    width: 12px !important;
    height: 12px !important;
}

.modal-description-section :deep(.bangumi-card .info-column) {
    width: 100% !important;
}

.modal-description-section :deep(.bangumi-card .header-section) {
    flex-direction: column !important;
    align-items: center !important;
    text-align: center !important;
    gap: 0.75rem !important;
}

.modal-description-section :deep(.bangumi-card .title) {
    font-size: 1.1rem !important;
}

.modal-description-section :deep(.bangumi-card .rating-badge) {
    text-align: center !important;
    width: 100% !important;
}

.modal-description-section :deep(.bangumi-card .score-box) {
    justify-content: center !important;
}

.modal-description-section :deep(.bangumi-card .score-val) {
    font-size: 1.5rem !important;
}

.modal-description-section :deep(.bangumi-card .score-suffix) {
    font-size: 0.8rem !important;
}

.modal-description-section :deep(.bangumi-card .score-count) {
    font-size: 0.65rem !important;
}

.modal-description-section :deep(.bangumi-card .distribution-bar) {
    height: 4px !important;
}

.modal-description-section :deep(.bangumi-card .tags-container) {
    justify-content: center !important;
    gap: 5px !important;
}

.modal-description-section :deep(.bangumi-card .tag-pill) {
    font-size: 0.65rem !important;
    padding: 2px 6px !important;
}

.modal-description-section :deep(.bangumi-card .summary-text) {
    font-size: 0.8rem !important;
    text-align: left !important;
}

.modal-description-section :deep(.bangumi-card .summary-text.collapsed) {
    -webkit-line-clamp: 2 !important;
    line-clamp: 2 !important;
}

.modal-description-section :deep(.bangumi-card .infobox-grid) {
    grid-template-columns: 1fr !important;
    gap: 6px !important;
    padding-top: 0.75rem !important;
    text-align: left !important;
}

.modal-description-section :deep(.bangumi-card .info-item) {
    font-size: 0.7rem !important;
}

.modal-description-section :deep(.bangumi-card .info-key) {
    font-size: 0.65rem !important;
}

.modal-description-section :deep(.github-repo-card) {
    padding: 0.75rem !important;
}

.modal-description-section :deep(.github-repo-card .repo-title) {
    font-size: 1rem !important;
}

.modal-description-section :deep(.github-repo-card .repo-description) {
    font-size: 0.8rem !important;
}

@media (max-width: 968px) {

    .modal-description-section {
        width: 100%;
        max-width: none;
        height: 40%;
        border-left: none;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    .description-header {
        padding: 1.5rem 1.5rem 0.75rem;
    }

    .description-title {
        font-size: 1.1rem;
    }

    .description-content {
        padding: 1.5rem;
    }
    .modal-description-section :deep(.bili-embed-neo),
    .modal-description-section :deep(.steam-card),
    .modal-description-section :deep(.xhs-embed-container),
    .modal-description-section :deep(.bangumi-card) {
        margin: 1rem 0 !important;
    }
}

@media (max-width: 480px) {
    .description-header {
        padding: 1rem 1rem 0.5rem;
    }

    .description-title {
        font-size: 1rem;
    }

    .description-content {
        padding: 1rem;
    }
    .markdown-body {
        font-size: 0.9rem;
    }

    .markdown-body h1 {
        font-size: 1.3rem;
    }

    .markdown-body h2 {
        font-size: 1.15rem;
    }

    .markdown-body h3 {
        font-size: 1rem;
    }
}
</style>
