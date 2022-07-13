<template>
    <div class="mt-4 ml-6 info-text">
        This table will display up to 1000 of the most recent document purchases in the last 14 days
    </div>
    <div class="mt-6">
        <document-access-request-history />
    </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import DocumentAccessRequestHistory from '@/components/BusinessInfo/DocumentAccessRequestHistory.vue'
import { useDocumentAccessRequest } from '@/composables'

const { loadAccessRequestHistory } = useDocumentAccessRequest()

onMounted(async () => {
    await loadAccessRequestHistory()
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.info-text {
  font-size: 0.875rem;
  color: $gray7
}
</style>