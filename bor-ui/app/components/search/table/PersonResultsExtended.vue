<script setup lang="ts">
import { getCode } from 'country-list'

defineProps<{ headers: BaseTableHeader[], resultsDesc: string }>()

// composables
const search = useSearchStore()
const { searchPerson } = storeToRefs(search)

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

// Vitests aren't handling the components using UTooltip
const isVitestRunning = !!process.env.VITEST_WORKER_ID
</script>

<template>
  <BaseTable
    class="person-results-extended rounded-t"
    height="100%"
    :item-key="'legalName'"
    :loading="searchPerson.loading"
    overflow="scroll"
    :reset-filters-trigger="resetFiltersTrigger"
    :results-description="resultsDesc"
    :set-headers="headers"
    :set-items="searchPerson.results"
    :title="$t('label.searchResults')"
    :title-extras="true"
    :total-items="searchPerson.resultsTotal"
  >
    <template #title-extras>
      <SearchTableCommonTitleExport v-model:export-rows="searchPerson.exportRows" />
    </template>
    <template #header-filter-selected-slot-citizenship="{ selected }">
      <span v-if="!selected" class="text-neutral">All</span>
      <div v-else class="flex -mt-2">
        <CountryFlag :country="getCode(selected)" size="normal" />
      </div>
    </template>
    <template #header-filter-slot-personControl>
      <SearchTableCommonHeadersPersonControlDetailsFilter :clear-filter="clearPersonDetailsFilter" />
    </template>
    <template #header-filter-slot-date>
      <SearchTableCommonHeadersDateRangeFilter :date-range-reset="dateRangeReset" />
    </template>
    <template #item-slot-name="{ item }">
      <SearchTableCommonItemsName :item="item" icon="i-mdi-account" />
    </template>
    <template #item-slot-information="{ item }">
      <SearchTableCommonItemsInformation :item="item" />
    </template>
    <template #item-slot-citizenship="{ item }">
      <div class="flex justify-center">
        <SearchTableCommonItemsCitizenship v-if="!isVitestRunning" :item="item" />
      </div>
    </template>
    <template #item-slot-details="{ item }">
      <div
        v-for="role, i in item.roles"
        :key="'child-role-' + i"
        class="child-row-item"
      >
        <div class="inner-row-div flex w-full">
          <div
            class="inner-col-div"
            :style="{ width: getChildHeaderWidth(headers, 'Business Details', childHeaders) }"
          >
            <SearchTableCommonItemsBusinessDetails :role="role" />
          </div>
          <div class="inner-col-div pl-1" :style="{ width: getChildHeaderWidth(headers, 'Roles', childHeaders) }">
            {{ capFirstLetter(`${role.roleType}`) }}
          </div>
          <div class="inner-col-div pl-2" :style="{ width: getChildHeaderWidth(headers, 'Details', childHeaders) }">
            <SearchTableCommonItemsPersonControl v-if="!isVitestRunning" :role="role" />
          </div>
          <div
            class="inner-col-div mr-0"
            :style="{ width: getChildHeaderWidth(headers, 'Effective Dates', childHeaders) }"
          >
            <SearchTableCommonItemsEffectiveDates :role="role" />
          </div>
        </div>
      </div>
    </template>
    <template v-if="searchPerson.error" #body-empty>
      <ErrorRetry
        class="my-5"
        :action="search.getSearchResults"
        :action-args="[searchPerson.val]"
        :message="$t('text.errorRetrySearch')"
      />
    </template>
  </BaseTable>
</template>
