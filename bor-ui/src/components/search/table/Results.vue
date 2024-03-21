<template>
  <div data-cy="search-results-table">
    <PersonResults
      v-if="!isExtended"
      class="search-table"
      :results-desc="resultsDesc"
      :update-table-header-filters="updateTableHeaderFilters"
    />
    <PersonResultsExtended
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
import PersonResults from './PersonResults.vue'
import PersonResultsExtended from './PersonResultsExtended.vue'

const search = useBcrosSearch()
const { hasMoreResults, isExtended, loadingNext } = storeToRefs(search)

// text functions
const resultsDesc = computed(() => {
  let desc = ''
  if (search.filters.categories.entityType?.includes(EntityTypeE.PERSON)) {
    const count = search.facetCount('entityType', EntityTypeE.PERSON)
    desc += `${count} ${count === 1 ? 'Person' : 'People'}`
  }
  if (search.filters.categories.entityType?.includes(EntityTypeE.BUSINESS)) {
    const count = search.facetCount('entityType', EntityTypeE.BUSINESS)
    if (desc) { desc += ', ' }
    desc += `${count} ${count === 1 ? 'Business' : 'Businesses'}`
  }
  return desc
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

  &__date-picker-filter {
    :deep(.v-field__input), :deep(.v-field__append-inner), :deep(.v-field) {
      cursor: pointer;
    }
  }
  &__date-picker-filter.v-input--dirty {
    :deep(.v-input__control .v-field--active.v-field--dirty .v-field__overlay) {
      background-color: $blueSelected;
      opacity: 1;
    }
  }

  &__clear {
    font-size: 14px !important;
    height: 36px;
    margin: auto;
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

  &__clear-btn {
    background-color: transparent;
    bottom: 37%;
    box-shadow: none;
    height: 25px;
    position: absolute;
    right: 20%;
    width: 25px;
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
}
</style>
