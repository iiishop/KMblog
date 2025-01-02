<script setup>
import { onMounted, onBeforeUnmount } from 'vue';
import { eventBus } from '@/eventBus';

function getPostInfo() {
    return {
        title: 'Post Title',
        content: 'Post Content'
    }
}

onMounted(() => {
    eventBus.$on('request-info', () => {
        const info = getPostInfo()
        eventBus.$emit('send-info', info);
    });
});

onBeforeUnmount(() => {
    eventBus.$off('request-info');
});

</script>