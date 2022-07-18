<template>
  <v-fade-transition>
    <div class="loading-container" v-if="loading">
      <div class="loading__content">
        <v-progress-circular color="primary" size="50" indeterminate />
        <div class="loading-msg" v-if="loading">Loading</div>
      </div>
    </div>
  </v-fade-transition>
  <base-table
    class="mt-10"
    filterClass="mt-4"
    height="100%"
    :itemKey="'submissionDate'"
    :loading="documentAccessRequest._loading"
    :setHeaders="PurchaseHistoryHeaders"
    :setItems="documentAccessRequest.requests"
    :totalItems="totalRequestsLength"
    :noResultsText="noResultsText"
  >
    <template v-slot:item-slot-documents="{ item }">
      <ul class="basic-list">
        <li v-for="(document, index) in item.documents" :key="index" class="doc-list-item">
          <span>{{ documentDescription(document.documentType) }}</span>
        </li>
      </ul>
    </template>
    <template v-slot:item-slot-button="{ item }">
      <v-btn
        class="btn-basic min-width-120 mx-auto"
        color="primary"
        large
        @click="openRequest(item)"
      >
        View Documents
      </v-btn>
    </template>
  </base-table>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
// local
import { BaseTable } from '@/components'
import { useDocumentAccessRequest, useEntity, useFilingHistory } from '@/composables'
import { RouteNames } from '@/enums'
import { DocumentDetailsI } from '@/interfaces'
import { DocumentTypeDescriptions } from '@/resources'
import { PurchaseHistoryHeaders } from '@/resources/table-headers'
 

// composables
const { documentAccessRequest } = useDocumentAccessRequest()
const { loadEntity } = useEntity()
const { clearFilingHistory, loadFilingHistory } = useFilingHistory()
const router = useRouter()

const loading = ref(false)

const totalRequestsLength = computed(() => documentAccessRequest.requests?.length || 0)

const noResultsText = "No purchases in the last 14 days"

const documentDescription = (type: string): string => {
  return DocumentTypeDescriptions[type]
}

const openRequest = async (item: DocumentDetailsI) => {
  loading.value = true
  clearFilingHistory()
  documentAccessRequest.currentRequest = item
  await loadEntity(item.businessIdentifier)
  await loadFilingHistory(item.businessIdentifier, item.submissionDate)
  router.push({ name: RouteNames.DOCUMENT_REQUEST })
  loading.value = false
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.min-width-120 {
  min-width: 7.5rem !important;
}
:deep(.v-btn__content) {
  min-width: 7.5rem;
}
</style>
