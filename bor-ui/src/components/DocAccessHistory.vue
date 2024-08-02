<template>
  <div class="px-[30px] py-12 bg-white rounded-t" data-cy="search-docAccess">
    <p data-cy="search-docAccess-info">
      {{ t('text.docAccess.tableInfo') }}
    </p>
    <base-table
      class="rounded-t border-[1px] border-gray-200 mt-5"
      height="100%"
      item-key="submissionDate"
      :loading="docAccessLoading"
      :no-results-text="t('text.docAccess.noResults')"
      :reset-filters-trigger="resetFiltersTrigger"
      reset-on-item-change
      :set-headers="getDocHistoryHeaders()"
      :set-items="docAccessHistory"
      :title="t('label.docAccess.documents')"
      :total-items="docAccessHistory.length"
      data-cy="search-docAccess-table"
      @filter-active="filterActive = $event"
    >
      <template #header-filter-slot-action>
        <SearchTableCommonHeadersClearFilters
          v-if="filterActive"
          class="flex grow justify-center mb-4"
          @click="resetFiltersTrigger = !resetFiltersTrigger"
        />
      </template>
      <template #item-slot-name="{ item } : { item: DocAccessI }">
        <SearchTableCommonItemsName icon="i-mdi-domain" :item="{ legalName: item.businessName }" />
      </template>
      <template #item-slot-documents="{ item } : { item: DocAccessI }">
        <ul class="basic-list">
          <li v-for="(document, index) in item.documents" :key="index" class="doc-list-item">
            <span>{{ documentDescription(document.documentType) }}</span>
          </li>
        </ul>
      </template>
      <template #item-slot-action="{ item } : { item: DocAccessI }">
        <UButton
          class="px-7 py-2"
          color="primary"
          :label="t('label.docAccess.viewDocuments')"
          @click="goToOpenDocAccess(item)"
        />
      </template>
      <template v-if="docAccessErrors.length > 0" #body-empty>
        <bcros-error-retry
          class="my-5"
          :action="docAccess.loadDocAccessHistory"
          :message="t('text.docAccess.errorRetry')"
        />
      </template>
    </base-table>
  </div>
</template>

<script setup lang="ts">
import type { DocAccessI, DocAccessTypeE } from '#imports'

const docAccess = useBcrosDocAccess()
const { docAccessHistory, docAccessErrors, docAccessLoading } = storeToRefs(docAccess)

const { t } = useNuxtApp().$i18n

const filterActive = ref(false)
const resetFiltersTrigger = ref(false)

const documentDescription = (type: DocAccessTypeE): string => {
  return t(`label.docAccess.${type}`)
}

onMounted(() => { docAccess.loadDocAccessHistory() })
</script>

<style lang="scss" scoped>
</style>
