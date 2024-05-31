<template>
  <base-table
    class="person-results rounded-t relative"
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
    <!-- <template #header-filter-slot-actions>
      <CommonHeadersActionFilter
        v-if="isFilteringActive"
        :outer-class="'h-[60px] pt-1'"
        @clear="clearFilters()"
      />
    </template> -->
    <template #item-slot-name="{ item }">
      <CommonItemsName
        :icon="item.entityType.toUpperCase() === EntityTypeE.PERSON ? 'i-mdi-account' : 'i-mdi-domain'"
        :item="item"
      />
    </template>
    <template #item-slot-address="{ item }">
      <BcrosAddressDisplay
        v-if="item.entityAddresses"
        :address="item.entityAddresses[0]"
      />
      <span v-else>N/A</span>
    </template>
    <template #item-slot-roles="{ item } : { item: SearchResultI }">
      <div v-for="role, i in item.roles" :key="'child-role-' + i" class="child-row-item">
        <div class="inner-row-div flex w-full">
          <div class="inner-col-div" :style="{ width: getChildHeaderWidth(headers, 'Roles', childHeaders) }">
            <div>
              {{ capFirstLetter(`${role.roleType}`) }}
            </div>
          </div>
          <div
            class="inner-col-div pl-2 mr-0"
            :style="{ width: getChildHeaderWidth(headers, 'Effective Dates', childHeaders) }"
          >
            <CommonItemsEffectiveDates :role="role" />
          </div>
          <div
            class="inner-col-div pl-2"
            :style="{ width: getChildHeaderWidth(headers, 'Business Details', childHeaders) }"
          >
            <CommonItemsBusinessDetails :role="role" />
          </div>
          <div
            class="inner-col-div pl-2"
            :style="{ width: getChildHeaderWidth(headers, 'Business Status', childHeaders) }"
          >
            {{ capFirstLetter(`${role.relatedState}`) }}
          </div>
          <div
            class="inner-col-div pl-2"
            :style="{ width: getChildHeaderWidth(headers, 'Business Email', childHeaders) }"
          >
            {{ role.relatedEmail || '' }}
          </div>
        </div>
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
  CommonItemsBusinessDetails, CommonHeadersDateRangeFilter,
  CommonItemsEffectiveDates, CommonItemsName, CommonTitleExport
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
const headers = getPersonHeadersLimited()
const childHeaders = ['Roles', 'Effective Dates', 'Business Details', 'Business Status', 'Business Email']
// set table filters to session saved ones
onMounted(() => { props.updateTableHeaderFilters(headers) })

// filter clearing
const resetFiltersTrigger = ref(false)
const dateRangeReset = ref(false)
// const clearFilters = () => {
//   resetFiltersTrigger.value = !resetFiltersTrigger.value
//   dateRangeReset.value = !dateRangeReset.value
//   // search on reset filters
//   search.filterSearch(null, null, true)
// }
</script>
