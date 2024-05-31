<template>
  <base-table
    class="person-results-extended rounded-t"
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
    <!-- <template #header-item-slot-actions>
      <div class="h-[76.5px] w-full pt-8 shadow-action-col-header">
        <b>Actions</b>
      </div>
    </template> -->
    <template #header-filter-selected-slot-citizenship="{ selected }">
      <span v-if="!selected">All</span>
      <div v-else class="flex">
        <CountryFlag :country="getCode(selected)" size="normal" />
      </div>
    </template>
    <template #header-filter-slot-personControl>
      <CommonHeadersPersonControlDetailsFilter :clear-filter="clearPersonDetailsFilter" />
    </template>
    <template #header-filter-slot-date>
      <CommonHeadersDateRangeFilter :date-range-reset="dateRangeReset" />
    </template>
    <!-- <template #header-filter-slot-actions>
      <CommonHeadersActionFilter
        v-if="isFilteringActive"
        :outer-class="'h-[81px] w-full pl-3 pt-5 shadow-action-col-header'"
        @clear="clearFilters()"
      />
    </template> -->
    <!-- <template #item-loading-slot-actions>
      <div class="h-[83px] pt-[26px] pb-4 px-3 shadow-action-col-item bg-white">
        <div class="w-full h-10 bg-bcGovGray-300 rounded" />
      </div>
    </template> -->
    <template #item-slot-name="{ item } : { item: SearchResultI }">
      <CommonItemsName :item="item" />
    </template>
    <template #item-slot-information="{ item } : { item: SearchResultI }">
      <CommonItemsInformation :item="item" />
    </template>
    <template #item-slot-citizenship="{ item } : { item: SearchResultI }">
      <div class="flex justify-center">
        <CommonItemsCitizenship :item="item" />
      </div>
    </template>
    <template #item-slot-details="{ item } : { item: SearchResultI }">
      <div v-for="role, i in item.roles" :key="'child-role-' + i" class="child-row-item">
        <div class="inner-row-div flex w-full">
          <div
            class="inner-col-div pl-3"
            :style="{ width: getChildHeaderWidth(headers, 'Business Details', childHeaders) }"
          >
            <CommonItemsBusinessDetails :role="role" />
          </div>
          <div class="inner-col-div pl-3" :style="{ width: getChildHeaderWidth(headers, 'Roles', childHeaders) }">
            {{ capFirstLetter(`${role.roleType}`) }}
          </div>
          <div class="inner-col-div pl-3" :style="{ width: getChildHeaderWidth(headers, 'Details', childHeaders) }">
            <CommonItemsPersonControl :role="role" />
          </div>
          <div
            class="inner-col-div pl-3 mr-0"
            :style="{ width: getChildHeaderWidth(headers, 'Effective Dates', childHeaders) }"
          >
            <CommonItemsEffectiveDates :role="role" />
          </div>
        </div>
      </div>
    </template>
    <!-- <template #item-slot-actions="{ item } : { item: SearchResultI }">
      <div class="h-full w-full px-3 pt-3 shadow-action-col-item">
        <CommonItemsAction show-btn @action="console.info('clicked open on', item.legalName)" />
      </div>
    </template> -->
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
import { getCode } from 'country-list'
import {
  CommonHeadersDateRangeFilter, CommonHeadersPersonControlDetailsFilter,
  CommonItemsBusinessDetails, CommonItemsPersonControl, CommonItemsName,
  CommonTitleExport, CommonItemsInformation, CommonItemsEffectiveDates,
  CommonItemsCitizenship
} from './common'

const props = defineProps<{
  resultsDesc: string,
  updateTableHeaderFilters:(val: BaseTableHeaderI[]) => void,
}>()

// composables
const search = useBcrosSearch()
const {
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
const clearPersonDetailsFilter = ref(false)
// const clearFilters = () => {
//   resetFiltersTrigger.value = !resetFiltersTrigger.value
//   dateRangeReset.value = !dateRangeReset.value
//   clearPersonDetailsFilter.value = !clearPersonDetailsFilter.value
//   // search on reset filters
//   search.filterSearch(null, null, true)
// }

// get width for role columns dynamically
const childHeaders: string[] = ['Business Details', 'Roles', 'Details', 'Effective Dates']
</script>
<style lang="scss" scoped>
.child-row-item:not(:first-child) .inner-row-div {
  border-top: 1px solid theme('colors.gray.300');
  margin-top: 20px;
  padding-top: 20px;
}
</style>
