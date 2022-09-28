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
    id="doc-access-req-table"
    class="mt-30px soft-corners-top"
    height="100%"
    :itemKey="'submissionDate'"
    :loading="documentAccessRequest._loading"
    resetOnItemChange
    :resetFilters="resetFilters"
    :resultsDescription="resultsDescription"
    :setHeaders="PurchaseHistoryHeaders"
    :setItems="documentAccessRequest.requests"
    title="Documents"
    :totalItems="totalRequestsLength"
    :noResultsText="noResultsText"
    @filterActive="filterActive = $event"
    @resetFilters="resetFilters = false"
  >
    <template v-slot:item-slot-name="{ item }">
      <search-table-name icon="mdi-domain" :name="item.businessName" />
    </template>
    <template v-slot:header-filter-slot-action>
      <v-btn
        v-if="filterActive"
        class="btn-basic-outlined mx-auto clear-btn"
        :append-icon="'mdi-window-close'"
        @click="resetFilters = true"
      >
        Clear Filters
      </v-btn>
    </template>
    <template v-slot:item-slot-documents="{ item }">
      <ul class="basic-list">
        <li v-for="(document, index) in item.documents" :key="index" class="doc-list-item">
          <span>{{ documentDescription(document.documentType) }}</span>
        </li>
      </ul>
    </template>
    <template v-slot:item-slot-action="{ item }">
      <v-btn
        class="btn-basic view-doc-btn"
        color="primary"
        large
        @click="openRequest(item)"
      >
        View Documents
      </v-btn>
    </template>
    <template v-if="documentAccessRequest._error" v-slot:body-empty>
      <error-retry
        class="my-3"
        :action="loadAccessRequestHistory"
        message="We were unable to retrieve your recent purchases. Please try again later."
      />
    </template>
  </base-table>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
// local
import { BaseTable, ErrorRetry } from '@/components'
import { SearchTableName } from '@/components/search/common'
import { useDocumentAccessRequest, useEntity, useFilingHistory } from '@/composables'
import { RouteNames } from '@/enums'
import { DocumentDetailsI } from '@/interfaces'
import { DocumentTypeDescriptions } from '@/resources'
import { PurchaseHistoryHeaders } from '@/resources/table-headers'
 

// composables
const { documentAccessRequest, loadAccessRequestHistory } = useDocumentAccessRequest()
const { loadEntity } = useEntity()
const { clearFilingHistory, loadFilingHistory } = useFilingHistory()
const router = useRouter()

const loading = ref(false)

const filterActive = ref(false)
const resetFilters = ref(false)

const totalRequestsLength = computed(() => documentAccessRequest.requests?.length || 0)
const resultsDescription = computed(() => totalRequestsLength.value === 1 ? 'Purchase' : 'Purchases')

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
  router.push({ name: RouteNames.DOCUMENT_REQUEST, params: { identifier: item.businessIdentifier } })
  loading.value = false
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#doc-access-req-table {
  border: solid 1px $gray2;

  @media (max-width: 1242px) {
    :deep(.base-table__header__item__title.v-btn.v-btn--density-default) {
      height: 60px;
    }
  }
}

.clear-btn {
  font-size: 14px;
  height: 36px;
  padding: 0 12px !important;
  width: 90%;
}

.view-doc-btn {
  height: 36px;
  margin-top: -9px;
  width: 90%;

  :deep(.v-btn__content) {
    min-width: 7.5rem;
  }
}
</style>
