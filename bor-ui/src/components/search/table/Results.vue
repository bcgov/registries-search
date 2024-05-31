<template>
  <div data-cy="search-results-table">
    <PersonResultsLimited
      v-if="hasLimitedAccess"
      class="search-table"
      :results-desc="resultsDesc"
      :update-table-header-filters="updateTableHeaderFilters"
    />
    <PersonResultsExtended
      v-else-if="hasExtendedAccess"
      class="search-table"
      :results-desc="resultsDesc"
      :update-table-header-filters="updateTableHeaderFilters"
    />
    <PersonResultsPublic
      v-else
      class="search-table"
      :results-desc="resultsDesc"
      :update-table-header-filters="updateTableHeaderFilters"
    />
    <div id="load-more-results" class="flex justify-center">
      <UButton
        v-show="hasMoreResults"
        class="p-4 mt-[30px]"
        icon="i-mdi-plus"
        label="Load More Results"
        :loading="loadingNext"
        loading-icon="i-mdi-loading"
        trailing
        variant="outline"
        @click="getNextSearches()"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import _ from 'lodash'
import PersonResultsExtended from './PersonResultsExtended.vue'
import PersonResultsLimited from './PersonResultsLimited.vue'
import PersonResultsPublic from './PersonResultsPublic.vue'

const search = useBcrosSearch()
const { totalResults, hasMoreResults, loadingNext, hasExtendedAccess, hasLimitedAccess } = storeToRefs(search)

// text functions
const resultsDesc = computed(() => {
  return `${totalResults.value} ${totalResults.value === 1 ? 'Person' : 'People'}`
})

/** Update the base table header filters to display what the current filters are.
 * (needed when leaving and coming back to the component)
 */
const updateTableHeaderFilters = (headers: BaseTableHeaderI[]) => {
  const activeFilters = Object.keys(search.filters)
  for (const i in activeFilters) {
    // find header filter
    const header = headers.find(item => item.col === activeFilters[i])
    // update filter value to match search composable
    if (header) { header.filter.value = search.filters[activeFilters[i]] }
  }
}

const getNextSearches = _.debounce(async () => (await search.getNextResults()), 50)
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
