<script setup lang="ts">
const docAccess = useDocAccessStore()
const { docAccessHistory, docAccessErrors, docAccessLoading } = storeToRefs(docAccess)

const { t } = useNuxtApp().$i18n

const filterActive = ref(false)
const resetFiltersTrigger = ref(false)

const documentDescription = (type: DocAccessType): string => {
  return t(`docAccess.${type}`)
}

const buttonTextForStatus = (status: string): string => {
  if (
    status.toLowerCase().indexOf('paid') === 0
    || status.toLowerCase().indexOf('completed') === 0
  ) {
    return t('label.viewDocuments')
  } else if (status.toLowerCase().indexOf('error') === 0) {
    return t('text.tryAgain')
  }
  return ''
}

const colorForStatus = (status: string): 'success' | 'error' | 'neutral' => {
  if (
    status.toLowerCase().indexOf('paid') === 0
    || status.toLowerCase().indexOf('completed') === 0
  ) {
    return 'success'
  } else if (status.toLowerCase().indexOf('pending') === 0) {
    return 'neutral'
  } else if (status.toLowerCase().indexOf('error') === 0) {
    return 'error'
  }
  return 'neutral'
}

const textForStatus = (status: string): string => {
  if (
    status.toLowerCase().indexOf('paid') === 0
    || status.toLowerCase().indexOf('completed') === 0
  ) {
    return t('label.paid').toUpperCase()
  } else if (status.toLowerCase().indexOf('pending') === 0) {
    return t('label.paymentPending').toUpperCase()
  } else if (status.toLowerCase().indexOf('error') === 0) {
    return t('label.paymentFailed').toUpperCase()
  } else {
    return ''
  }
}

const actionButton = (item: DocAccess) => {
  if (['PAID', 'COMPLETED'].includes(item.status)) {
    const localePath = useLocalePath()
    useRouter().push(localePath(`/open/${item.businessIdentifier}/${item.id}`))
  } else if (item.status === 'ERROR') {
    const identifier = item.businessIdentifier

    // can't get an item in this list unless it's modernized
    goToOpenBusiness(identifier, true)
  }
}

onMounted(() => {
  docAccess.init()
})
</script>

<template>
  <div class="px-[30px] py-12 bg-white rounded-t" data-testid="search-docAccess">
    <p data-testid="search-docAccess-info">
      {{ t('text.tableInfo') }}
    </p>
    <BaseTable
      class="rounded-t border border-gray-200 mt-5"
      height="100%"
      item-key="submissionDate"
      :loading="docAccessLoading"
      :no-results-text="t('text.noPurchases')"
      :reset-filters-trigger="resetFiltersTrigger"
      reset-on-item-change
      :set-headers="getDocHistoryHeaders()"
      :set-items="docAccessHistory"
      :title="t('label.documents')"
      :total-items="docAccessHistory.length"
      data-testid="search-docAccess-table"
      @filter-active="filterActive = $event"
    >
      <template #header-filter-slot-action>
        <SearchTableCommonHeadersClearFilters
          v-if="filterActive"
          class="flex grow justify-center mb-4"
          @click="resetFiltersTrigger = !resetFiltersTrigger"
        />
      </template>
      <template #item-slot-name="{ item }">
        <SearchTableCommonItemsName icon="i-mdi-domain" :item="{ legalName: item.businessName }" />
      </template>
      <template #item-slot-documents="{ item }">
        <ul class="basic-list">
          <li
            v-for="(document, index) in item.documents"
            :key="index"
          >
            <span>{{ documentDescription(document.documentType) }}</span>
          </li>
          <li>
            <UBadge
              :color="colorForStatus(item.status)"
              :label="textForStatus(item.status)"
            />
          </li>
        </ul>
      </template>
      <template #item-slot-action="{ item }">
        <div class="p-1">
          <UButton
            class="py-2 w-full"
            color="primary"
            :loading="item.status.toLowerCase().indexOf('pending') === 0"
            loading-icon="i-mdi-loading"
            :disabled="item.status.toLowerCase().indexOf('pending') === 0"
            @click="actionButton(item)"
          >
            <span>{{ buttonTextForStatus(item.status) }}</span>
          </UButton>
        </div>
      </template>
      <template v-if="docAccessErrors.length > 0" #body-empty>
        <ErrorRetry
          class="my-5"
          :action="docAccess.init"
          :message="t('text.docAccess.errorRetry')"
        />
      </template>
    </BaseTable>
  </div>
</template>
