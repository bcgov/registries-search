<script setup lang="ts">
import { useThrottleFn } from '@vueuse/core'
import { SearchType } from '#imports'

const search = useSearchStore()
const { activeSearch, hasMoreResults, searchType } = storeToRefs(search)
const { hasExtendedAccess } = storeToRefs(useSearchAccessStore())

// table headers
const headers = ref({
  [SearchType.BUSINESS]: getBusinessHeaders(),
  [SearchType.DIRECTOR]: getPersonHeadersLimited(),
  [SearchType.PERSON]: hasExtendedAccess.value ? getPersonHeadersExtended() : getPersonHeadersPublic()
})

// text functions
const resultsDesc = computed(() => {
  if (searchType.value === SearchType.BUSINESS) {
    return `${activeSearch.value.resultsTotal} ${activeSearch.value.resultsTotal === 1 ? 'Business' : 'Businesses'}`
  }
  return `${activeSearch.value.resultsTotal} ${activeSearch.value.resultsTotal === 1 ? 'Person' : 'People'}`
})

/** Update the base table header filters to display what the current filters are.
 * (needed when leaving and coming back to the component)
 */
const updateTableHeaderFilters = (headers: BaseTableHeader[]) => {
  const activeFilters = Object.keys(activeSearch.value.filters)
  for (const i in activeFilters) {
    // find header filter
    const header = headers.find(item => item.col === activeFilters[i])
    // update filter value to match search store
    if (header) {
      header.filter.value = activeSearch.value.filters[activeFilters[i]]
    }
  }
}
watch(searchType, (val) => {
  updateTableHeaderFilters(headers.value[val])
}, { immediate: true })

const getNextSearches = useThrottleFn(async () => {
  await search.getNextResults()
}, 1000)
</script>

<template>
  <div data-testid="search-results-table">
    <div v-if="searchType === SearchType.PERSON">
      <SearchTablePersonResultsExtended
        v-if="hasExtendedAccess"
        class="search-table"
        :headers="headers[SearchType.PERSON]"
        :results-desc="resultsDesc"
      />
      <SearchTablePersonResultsPublic
        v-else
        class="search-table"
        :headers="headers[SearchType.PERSON]"
        :results-desc="resultsDesc"
      />
    </div>
    <SearchTablePersonResultsLimited
      v-else-if="searchType === SearchType.DIRECTOR"
      class="search-table"
      :headers="headers[SearchType.DIRECTOR]"
      :results-desc="resultsDesc"
    />
    <SearchTableBusinessResults
      v-else
      class="search-table"
      :headers="headers[SearchType.BUSINESS]"
      :results-desc="resultsDesc"
    />
    <div id="load-more-results" class="flex justify-center">
      <UButton
        v-if="hasMoreResults"
        class="p-4 mt-[30px]"
        icon="i-mdi-plus"
        label="Load More Results"
        :loading="activeSearch.loadingNext"
        loading-icon="i-mdi-loading"
        trailing
        variant="outline"
        @click="getNextSearches()"
      />
    </div>
  </div>
</template>

<style>
.search-table {

  .actions-col {
    padding: 0 0 0 4px;
    position: sticky;
    right: 0;
    width: 156px;
    max-width: 156px;
    min-width: 156px;
    z-index: 4;
  }
}
</style>
