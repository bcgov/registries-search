<template>
  <div data-cy="search-results-table">
    <div v-if="searchType === SearchTypeE.PERSON">
      <PersonResultsExtended
        v-if="hasExtendedAccess"
        class="search-table"
        :headers="headers[SearchTypeE.PERSON]"
        :results-desc="resultsDesc"
      />
      <PersonResultsPublic
        v-else
        class="search-table"
        :headers="headers[SearchTypeE.PERSON]"
        :results-desc="resultsDesc"
      />
    </div>
    <PersonResultsLimited
      v-else-if="searchType === SearchTypeE.DIRECTOR"
      class="search-table"
      :headers="headers[SearchTypeE.DIRECTOR]"
      :results-desc="resultsDesc"
    />
    <BusinessResults
      v-else
      class="search-table"
      :headers="headers[SearchTypeE.BUSINESS]"
      :results-desc="resultsDesc"
    />
    <div id="load-more-results" class="flex justify-center">
      <UButton
        v-show="hasMoreResults"
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

<script setup lang="ts">
import { useThrottleFn } from '@vueuse/core'
import BusinessResults from './BusinessResults.vue'
import PersonResultsExtended from './PersonResultsExtended.vue'
import PersonResultsLimited from './PersonResultsLimited.vue'
import PersonResultsPublic from './PersonResultsPublic.vue'
import { SearchTypeE } from '#imports'

const search = useBcrosSearch()
const { activeSearch, hasMoreResults, searchType } = storeToRefs(search)
const { hasExtendedAccess } = storeToRefs(useBcrosSearchAccess())

// table headers
const headers = ref({
  [SearchTypeE.BUSINESS]: getBusinessHeaders(),
  [SearchTypeE.DIRECTOR]: getPersonHeadersLimited(),
  [SearchTypeE.PERSON]: hasExtendedAccess.value ? getPersonHeadersExtended() : getPersonHeadersPublic()
})

// text functions
const resultsDesc = computed(() => {
  if (searchType.value === SearchTypeE.BUSINESS) {
    return `${activeSearch.value.resultsTotal} ${activeSearch.value.resultsTotal === 1 ? 'Business' : 'Businesses'}`
  }
  return `${activeSearch.value.resultsTotal} ${activeSearch.value.resultsTotal === 1 ? 'Person' : 'People'}`
})

/** Update the base table header filters to display what the current filters are.
 * (needed when leaving and coming back to the component)
 */
const updateTableHeaderFilters = (headers: BaseTableHeaderI[]) => {
  const activeFilters = Object.keys(activeSearch.value.filters)
  for (const i in activeFilters) {
    // find header filter
    const header = headers.find(item => item.col === activeFilters[i])
    // update filter value to match search store
    if (header) { header.filter.value = activeSearch.value.filters[activeFilters[i]] }
  }
}
watch(searchType, (val) => {
  updateTableHeaderFilters(headers.value[val])
}, { immediate: true })

const getNextSearches = useThrottleFn(async () => {
  await search.getNextResults()
}, 1000)
</script>

<style lang="scss">
.search-table {
  border: solid 1px theme('colors.gray.200');

  a {
    color: theme('colors.blue.500');
    text-decoration: underline;
  }

  tr .base-table__header__item:last-child {
    padding-right: 12px;
  }

  .inner-col-div {
    overflow-wrap: break-word;
  }

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
