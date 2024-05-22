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
    <div id="load-more-results" style="text-align: center;">
      <v-btn
        v-if="hasMoreResults"
        class="mt-30px"
        :loading="loadingNext"
        color="primary"
        variant="outlined"
        @click="getNextSearches()"
      >
        Load More Results
      </v-btn>
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
@import '@/assets/styles/theme.scss';
.search-table {
  border: solid 1px $gray2;

  a {
    color: $app-blue;
    text-decoration: underline;
  }

  &__clear {
    font-size: 14px !important;
    height: 36px;
    padding: 0 12px !important;
    min-width: 108px;
    width: 90%;

    .v-btn__append {
      margin-left: 4px;
      margin-top: 2px;
    }

    .v-btn__content {
      white-space: nowrap;
    }
  }

  &__export-select {
    background-color: white;
    .v-input__control .v-field.v-field--active:not(.v-field--error) .v-field__outline .v-label.v-field-label--floating {
      color: $gray7;
      margin-left: 9px;
    }
    .v-input__control .v-field__append-inner {
      margin-right: 12px;
    }
    .v-input__control .v-field .v-field__field .v-field__input .v-select__selection {
      font-size: 16px;
      margin-bottom: 4px;
    }
  }

  tr .base-table__header__item:last-child {
    padding-right: 12px;
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
