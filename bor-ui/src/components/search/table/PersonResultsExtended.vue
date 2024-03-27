<template>
  <base-table
    class="person-results-extended rounded-top"
    height="100%"
    :item-key="'legalName'"
    :loading="loading"
    overflow="scroll"
    :reset-filters-trigger="resetFiltersTrigger"
    :results-description="resultsDesc"
    :set-headers="headers"
    :set-items="results"
    :table-width="'1600px'"
    title="Search Results"
    :title-extras="true"
    :total-items="totalResults"
  >
    <template #title-extras>
      <CommonTitleExport />
    </template>
    <template #header-item-slot-actions>
      <div class="h-[76.5px] w-full pt-8 shadow-action-col-header">
        <b>Actions</b>
      </div>
    </template>
    <template #header-filter-slot-date>
      <CommonHeadersDateRangeFilter :date-range-reset="dateRangeReset" />
    </template>
    <template #header-filter-slot-actions>
      <div class="h-[81px] w-full pl-3 pt-5 shadow-action-col-header">
        <CommonHeadersActionFilter
          v-if="isFilteringActive"
          @clear="clearFilters()"
        />
      </div>
    </template>
    <template #item-slot-name="{ item } : { item: SearchResultI }">
      <CommonItemsName :item="item" />
    </template>
    <template #item-slot-information="{ item } : { item: SearchResultI }">
      <CommonItemsInformation :item="item" />
    </template>
    <template #item-slot-details="{ item } : { item: SearchResultI }">
      <CommonItemsBusinessDetails :item="item" />
    </template>
    <template #item-slot-actions="{ item } : { item: SearchResultI }">
      <div class="h-full w-full px-3 pt-3 shadow-action-col-item">
        <CommonItemsAction show-btn @action="console.info('clicked open on', item.legalName)" />
      </div>
    </template>
    <template v-if="searchError" #body-empty>
      <bcros-error-retry
        class="my-5"
        :action="search.getSearchResults"
        :action-args="[searchValue]"
        message="We are unable to display your search results. Please try again later."
      />
    </template>
  </base-table>
</template>

<script setup lang="ts">
import {
  CommonHeadersActionFilter, CommonItemsAction, CommonItemsBusinessDetails,
  CommonHeadersDateRangeFilter, CommonItemsName, CommonTitleExport, CommonItemsInformation
} from './common'
import { getPersonHeadersExtended } from '@/utils'

const props = defineProps<{
  resultsDesc: string,
  updateTableHeaderFilters:(val: BaseTableHeaderI[]) => void,
}>()

// composables
const search = useBcrosSearch()
const {
  isFilteringActive,
  loading,
  results,
  totalResults,
  searchError,
  searchValue
} = storeToRefs(search)

// search table config (headers)
const headers = getPersonHeadersExtended()
// set table filters to session saved ones
onMounted(() => { props.updateTableHeaderFilters(headers) })

// filter clearing
const resetFiltersTrigger = ref(false)
const dateRangeReset = ref(false)
const clearFilters = () => {
  resetFiltersTrigger.value = !resetFiltersTrigger.value
  dateRangeReset.value = !dateRangeReset.value
  // search on reset filters
  search.filterSearch(null, null, true)
}
</script>
