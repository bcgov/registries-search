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
    <template #header-filter-selected-slot-citizenship="{ item }">
      <CountryFlag :country="getCode(item.value)" size="normal" />
    </template>
    <template #header-filter-slot-personControl>
      <CommonHeadersPersonControlDetailsFilter :clear-filter="clearPersonDetailsFilter" />
    </template>
    <template #header-filter-slot-date>
      <CommonHeadersDateRangeFilter :date-range-reset="dateRangeReset" />
    </template>
    <template #header-filter-slot-actions>
      <CommonHeadersActionFilter
        v-if="isFilteringActive"
        :outer-class="'h-[81px] w-full pl-3 pt-5 shadow-action-col-header'"
        @clear="clearFilters()"
      />
    </template>
    <template #item-loading-slot-actions>
      <div class="h-[83px] pt-[26px] pb-4 px-3 shadow-action-col-item bg-white">
        <div class="w-full h-10 bg-gray-300 rounded" />
      </div>
    </template>
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
    <template #item-slot-roles="{ item, header } : { item: SearchResultI, header: BaseTableHeaderI }">
      <tr v-for="role, i in item.roles" :key="'child-role-' + i" class="child-row-item">
        <div class="inner-row-div">
          <td width="192px">
            {{ header.itemFn(item) }}
          </td>
          <td class="pl-3" width="166px">
            <CommonItemsBusinessDetails :role="role" />
          </td>
          <td class="pl-3" width="204px">
            <CommonItemsPersonControl :role="role" />
          </td>
          <td class="pl-3" width="136px">
            <CommonItemsEffectiveDates :role="role" />
          </td>
        </div>
      </tr>
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
import { getCode } from 'country-list'
import {
  CommonHeadersActionFilter, CommonHeadersDateRangeFilter,
  CommonHeadersPersonControlDetailsFilter, CommonItemsAction, CommonItemsBusinessDetails,
  CommonItemsPersonControl, CommonItemsName, CommonTitleExport, CommonItemsInformation,
  CommonItemsEffectiveDates, CommonItemsCitizenship
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
const clearPersonDetailsFilter = ref(false)
const clearFilters = () => {
  resetFiltersTrigger.value = !resetFiltersTrigger.value
  dateRangeReset.value = !dateRangeReset.value
  clearPersonDetailsFilter.value = !clearPersonDetailsFilter.value
  // search on reset filters
  search.filterSearch(null, null, true)
}
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
tr.child-row-item:not(:first-child) .inner-row-div {
  border-top: 1px solid $gray3;
  margin-top: 20px;
  padding-top: 20px;
}
</style>
