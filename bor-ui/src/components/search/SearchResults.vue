<template>
  <div>
    <div class="search-table">
      <base-table
        id="entity-results"
        class="rounded-top"
        height="100%"
        :itemKey="'legalName'"
        :loading="search._loading"
        overflow="hidden"
        :resetFilters="resetFilters"
        :resultsDescription="resultsDesc"
        :setHeaders="SearchEntityHeaders"
        :setItems="search.results"
        title="Search Results"
        :totalItems="search.totalResults"
        @resetFilters="resetFilters = false"
      >
        <template v-slot:header-filter-slot-action>
          <v-btn
            v-if="isFilteringActive"
            class="btn-basic-outlined search-table__clear"
            :append-icon="'mdi-window-close'"
            @click="clearFilters()"
          >
            Clear Filters
          </v-btn>
        </template>
        <template v-slot:item-slot-name="{ header, item}">
          <search-table-name
            :icon="item.entityType.toLowerCase() === EntityType.PERSON ? 'mdi-account' : 'mdi-domain'"
            :name="header.itemFn(item[header.col])" />
        </template>
        <template v-slot:item-slot-action>
          <!-- @action="goToBusinessInfo(item)" -->
          <search-table-action
            :showBtn="false"
            :tooltipMsg="tooltipMsg"
          />
        </template>
        <template v-if="search._error" v-slot:body-empty>
          <error-retry
            class="my-5"
            :action="getSearchResults"
            :action-args="[search._value]"
            message="We are unable to display your search results. Please try again later."
          />
        </template>
      </base-table>
    </div>
    <div style="text-align: center;">
      <v-btn
        v-if="hasMoreResults"
        class="btn-basic-outlined mt-30px"
        :loading="search._loadingNext"
        @click="getNextSearches()"
      >
        Load More Results
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import _ from 'lodash'
// local
import { BaseTable, ErrorRetry } from '@/components'
import { useSearch } from '@/composables'
import { SearchEntityHeaders } from '@/resources/table-headers'
// internal
import { SearchTableAction, SearchTableName } from './common'
import { EntityType } from '@/enums'

// composables
const { isFilteringActive, facetCount, getNextResults, getSearchResults, hasMoreResults, search } = useSearch()

const resetFilters = ref(false)

const resultsDesc = computed(() => {
  let desc = ''
  if (search.filters.categories.entityType?.includes(EntityType.PERSON)) {
    const count = facetCount('entityType', EntityType.PERSON)
    desc += `${count} ${count === 1 ? 'Person' : 'People'}`
  }
  if (search.filters.categories.entityType?.includes(EntityType.BUSINESS)) {
    const count = facetCount('entityType', EntityType.BUSINESS)
    if (desc) desc += ', '
    desc += `${count} ${count === 1 ? 'Business' : 'Businesses'}`
  }
  return desc
})

const tooltipMsg = 'You can access this business through BC OnLine or by contacting BC Registries. ' +
  'See "Help with Business and Person Search" for details.'

const clearFilters = () => {
  for (const i in search.filters) { search.filters[i] = '' }
  updateTableHeaderFilters()
  resetFilters.value = true
}

const getNextSearches = _.debounce(async () => getNextResults(), 50)

/** Update the base table header filters to display what the current filters are.
 * (needed when leaving and coming back to the component)
 */
const updateTableHeaderFilters = () => {
  const activeFilters = Object.keys(search.filters)
  for (const i in activeFilters) {
    // find header filter
    const header = SearchEntityHeaders.find((item) => item.col === activeFilters[i])
    // update filter value to match search composable
    if (header) header.filter.value = search.filters[activeFilters[i]]
  }
}

// set table filters to session saved ones
onMounted(() => { updateTableHeaderFilters() })

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#entity-results {
  border: solid 1px $gray2;

  @media (max-width: 1160px) {
    :deep(.base-table__header__item__title.v-btn.v-btn--density-default) {
      height: 60px;
    }
  }
}

.search-table {
  &__clear {
    font-size: 14px;
    height: 36px;
    margin: auto;
    padding: 0 12px !important;
    min-width: 108px;
    width: 90%;
  }
  &__clear :deep(.v-btn__content) {
    white-space: nowrap;
  }
}
</style>
