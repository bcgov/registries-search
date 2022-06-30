<template>
    <div>
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