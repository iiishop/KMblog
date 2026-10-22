<template>
    <div class="decision-backdrop" @keydown.esc.prevent="$emit('answer', 'cancel')" @keydown.tab="trapFocus">
        <section ref="dialog" class="decision-dialog" role="dialog" aria-modal="true" aria-labelledby="leave-title">
            <h2 id="leave-title">保存后离开？</h2>
            <p><strong>{{ fileName }}</strong> 有尚未保存到文件的修改。</p>
            <p class="decision-note">保存失败时会留在当前文件，你可以重试或下载副本。</p>
            <div class="decision-actions">
                <button @click="$emit('answer', 'discard')">放弃修改</button>
                <button ref="cancelButton" @click="$emit('answer', 'cancel')">继续编辑</button>
                <button class="primary" @click="$emit('answer', 'save')">保存并继续</button>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';
defineProps<{ fileName: string }>();
defineEmits<{ answer: [choice: 'save' | 'discard' | 'cancel'] }>();
const dialog = ref<HTMLElement | null>(null);
const cancelButton = ref<HTMLButtonElement | null>(null);
let previousFocus: HTMLElement | null = null;
onMounted(() => { previousFocus = document.activeElement as HTMLElement; cancelButton.value?.focus(); });
onBeforeUnmount(() => previousFocus?.focus());
function trapFocus(event: KeyboardEvent) {
    const buttons = dialog.value?.querySelectorAll('button');
    if (!buttons?.length) return;
    const first = buttons[0];
    const last = buttons[buttons.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
}
</script>

<style scoped>
.decision-backdrop { position: fixed; inset: 0; z-index: 2000; background: #0008; display: grid; place-items: center; padding: 20px; }
.decision-dialog { width: min(460px, 100%); box-sizing: border-box; padding: 28px; border-radius: 12px; background: var(--theme-panel-bg, white); color: var(--theme-body-text, #222); box-shadow: 0 20px 80px #0003; }
h2 { margin: 0 0 16px; font-size: 20px; }
p { line-height: 1.7; overflow-wrap: anywhere; }
.decision-note { font-size: 13px; color: var(--theme-meta-text, #666); }
.decision-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; margin-top: 24px; }
button { padding: 9px 14px; border: 1px solid var(--theme-panel-border, #ddd); background: transparent; color: inherit; border-radius: 6px; cursor: pointer; }
button.primary { background: var(--theme-primary, #6366f1); color: white; border-color: transparent; }
button:focus-visible { outline: 2px solid var(--theme-primary, #6366f1); outline-offset: 3px; }
</style>
