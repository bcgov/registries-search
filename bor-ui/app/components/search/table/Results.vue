<script setup lang="ts">
import { useThrottleFn } from '@vueuse/core'
import { SearchType, type BaseTableHeader, type BusinessSearchPayload, type SearchPayload } from '#imports'

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

const mapBusinessSearchFilters = (filters: BusinessSearchPayload) => {
  return {
    ...filters.query,
    parties: undefined,
    ...(filters.query.parties ? filters.query.parties : {}),
    legalType: filters.categories.legalType ? filters.categories.legalType[0] : undefined,
    status: filters.categories.status ? filters.categories.status[0] : undefined
  }
}

const mapPersonSearchFilters = (filters: SearchPayload) => {
  return {
    ...filters.query,
    ...(filters.query.roles ? filters.query.roles : {}),
    ...filters.categories,
    roles: undefined,
    ...(filters.categories.roles ? filters.categories.roles : {}),
    nationalities: filters.categories.nationalities ? filters.categories.nationalities[0] : undefined
  }
}
/** Update the base table header filters to display what the current filters are.
 * (needed when leaving and coming back to the component)
 */
const updateTableHeaderFilters = (headers: BaseTableHeader[]) => {
  const activeFilters = searchType.value === SearchType.BUSINESS
    ? mapBusinessSearchFilters(activeSearch.value.filters)
    : mapPersonSearchFilters(activeSearch.value.filters)

  for (const i in activeFilters) {
    // find header filter
    const header = headers.find(item => [item.col, item.subCol].includes(i))
    // update filter value to match search store
    if (header && activeFilters[i]) {
      header.filter!.value = activeFilters[i]
    }
  }
}
watch(searchType, (val) => {
  updateTableHeaderFilters(headers.value[val])
}, { immediate: true })

onMounted(() => {
  updateTableHeaderFilters(headers.value[searchType.value])
})

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
