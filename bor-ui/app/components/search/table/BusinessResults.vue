<script setup lang="ts">
defineProps<{ headers: BaseTableHeader[], resultsDesc: string }>()

const search = useSearchStore()
const { searchBusiness } = storeToRefs(search)

const clearFilters = () => {
  resetFiltersTrigger.value = !resetFiltersTrigger.value
  // search on reset filters
  search.filterSearch([], undefined, true)
}

// filter clearing
const resetFiltersTrigger = ref(false)
</script>

<template>
  <BaseTable
    class="business-results rounded-t"
    height="100%"
    item-key="identifier"
    :loading="searchBusiness.loading"
    overflow="scroll"
    :reset-filters-trigger="resetFiltersTrigger"
    :results-description="resultsDesc"
    :set-headers="headers"
    :set-items="searchBusiness.results"
    :title="$t('label.searchResults')"
    :title-extras="true"
    :total-items="searchBusiness.resultsTotal"
  >
    <template #header-filter-slot-action>
      <SearchTableCommonHeadersClearFilters
        v-if="searchBusiness.filterActive"
        class="flex justify-center"
        @action="clearFilters()"
      />
    </template>
    <template #item-slot-name="{ item }">
      <SearchTableCommonItemsName
        icon="i-mdi-domain"
        :item="{ legalName: item.name }"
      />
    </template>
    <template #item-slot-action="{ item }">
      <SearchTableCommonItemsAction
        class="flex justify-center"
        :show-btn="item.modernized"
        :tooltip-msg="$t('text.accessBusinesstooltip')"
        @action="goToOpenBusiness(item.identifier, item.modernized)"
      />
    </template>
    <template #item-slot-significant-individuals="{ item }">
      <p
        v-for="party in item.parties"
        :key="party.partyName"
        class="mb-2"
      >
        {{ party.partyName }}
      </p>
      <p v-if="!item.parties || item.parties.length === 0" class="mb-2 italic">
        {{ $t('text.noSI') }}
      </p>
    </template>
    <template v-if="searchBusiness.error" #body-empty>
      <ErrorRetry
        class="my-5"
        :action="search.getSearchResults"
        :action-args="[searchBusiness.val]"
        :message="$t('text.errorRetrySearch')"
      />
    </template>
  </BaseTable>
</template>
