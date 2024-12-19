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
          <li>
            <BaseBadge
              :color="colorForStatus(item.status)"
              :text="textForStatus(item.status)"
              :text-color="textColorForStatus(item.status)"
            />
          </li>
        </ul>
      </template>
      <template #item-slot-action="{ item } : { item: DocAccessI }">
        <UButton
          class="px-7 py-2"
          color="primary"
          :disabled="item.status.toLowerCase().indexOf('pending') !== -1"
          @click="actionButton(item)"
        >
          <span
            v-if="item.status.toLowerCase().indexOf('pending') === -1"
          >
            {{ buttonTextForStatus(item.status) }}
          </span>
          <UIcon
            v-if="item.status.toLowerCase().indexOf('pending') !== -1"
            class="text-3xl animate-spin"
            name="i-mdi-loading"
            data-cy="loading-icon"
          />
        </UButton>
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

const buttonTextForStatus = (status: string): string => {
  if ((status.toLowerCase().indexOf('paid') === 0) ||
    (status.toLowerCase().indexOf('completed') === 0)
  ) {
    return t('label.docAccess.viewDocuments')
  } else if (status.toLowerCase().indexOf('error') === 0) {
    return t('text.docAccess.tryAgain')
  }
  return ''
}

const colorForStatus = (status: string): string => {
  if ((status.toLowerCase().indexOf('paid') === 0) ||
    (status.toLowerCase().indexOf('completed') === 0)
  ) {
    return 'green-success'
  } else if (status.toLowerCase().indexOf('pending') === 0) {
    return 'grey-550'
  } else if (status.toLowerCase().indexOf('error') === 0) {
    return 'red-600'
  }
  return 'grey-550'
}

const textForStatus = (status: string): string => {
  if ((status.toLowerCase().indexOf('paid') === 0) ||
    (status.toLowerCase().indexOf('completed') === 0)
  ) {
    return 'PAID'
  } else if (status.toLowerCase().indexOf('pending') === 0) {
    return 'PAYMENT PENDING'
  } else if (status.toLowerCase().indexOf('error') === 0) {
    return 'PATMENT FAILED'
  }
}

const actionButton = (item: DocAccessI) => {
  if ((status.toLowerCase().indexOf('paid') === 0) ||
    (status.toLowerCase().indexOf('completed') === 0)
  ) {
    goToOpenDocAccess(item)
  } else if (item.status.toLowerCase().indexOf('error') === 0) {
    const identifier = item.businessIdentifier

    // NOTE This is obviously not the legal type, but we don't have legal type
    // and you can't get an item in this list unless it's modernized
    goToOpenBusiness(identifier, BusinessTypeE.BENEFIT_COMPANY)
  }
}

const textColorForStatus = (status: string): string => {
  if (status.toLowerCase().indexOf('pending') === 0) {
    return 'black'
  }
  return 'white'
}

onMounted(() => { docAccess.loadDocAccessHistory() })
</script>

<style lang="scss" scoped>
</style>
