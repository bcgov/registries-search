<template>
  <base-table
    class="person-results rounded-top"
    height="100%"
    :item-key="'legalName'"
    :loading="loading"
    overflow="scroll"
    :reset-filters-trigger="resetFiltersTrigger"
    :results-description="resultsDesc"
    :set-headers="headers"
    :set-items="results"
    title="Search Results"
    :title-extras="true"
    :total-items="totalResults"
  >
    <template #title-extras>
      <CommonTitleExport />
    </template>
    <template #header-filter-slot-date>
      <CommonHeadersDateRangeFilter :date-range-reset="dateRangeReset" />
    </template>
    <template #header-filter-slot-actions>
      <CommonHeadersActionFilter
        v-if="isFilteringActive"
        @clear="clearFilters()"
      />
    </template>
    <template #item-slot-name="{ item }">
      <CommonItemsName
        :icon="item.entityType.toUpperCase() === EntityTypeE.PERSON ? 'mdi-account' : 'mdi-domain'"
        :item="item"
      />
    </template>
    <template #item-slot-details="{ item } : { item: SearchResultI }">
      <CommonItemsBusinessDetails :item="item" />
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
  CommonHeadersActionFilter, CommonItemsBusinessDetails, CommonHeadersDateRangeFilter,
  CommonItemsName, CommonTitleExport
} from './common'
import { getPersonHeaders } from '@/utils'

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
const headers = getPersonHeaders()
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
