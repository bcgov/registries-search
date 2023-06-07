<template>
  <div>
    <BCRegDateRangePicker
      v-show="showDatePicker"
      ref="datePickerRef"
      :defaultEndDate="dateRangeEnd"
      :defaultStartDate="dateRangeStart"
      :reset="dateRangeResetTrigger"
      @submit="updateDateRange($event)"
    />
    <div class="search-table">
      <base-table
        id="entity-results"
        class="rounded-top"
        height="100%"
        :itemKey="'legalName'"
        :loading="search._loading"
        overflow="hidden"
        :resetFiltersTrigger="resetFiltersTrigger"
        :resultsDescription="resultsDesc"
        :setHeaders="SearchEntityHeaders"
        :setItems="search.results"
        title="Search Results"
        :totalItems="search.totalResults"
      >
        <template v-slot:header-filter-slot-date>
          <v-text-field
            class="search-table__date-picker-filter active"
            append-inner-icon="mdi-calendar"
            density="compact"
            hide-details
            placeholder="Date"
            readonly
            v-model="dateFilterText"
            @click="scrollToDatePicker()"
            @click:append-inner="scrollToDatePicker()"
          />
          <v-btn
            v-if="dateFilterText"
            class="search-table__clear-btn"
            icon
            @click="dateRangeResetTrigger = !dateRangeResetTrigger"
          >
            <v-icon color="primary" size="20">mdi-close</v-icon>
          </v-btn>
        </template>
        <template v-slot:header-filter-slot-action>
          <v-btn
            v-if="search._isFilteringActive"
            class="btn-basic-outlined search-table__clear"
            :append-icon="'mdi-window-close'"
            @click="clearFilters()"
          >
            Clear Filters
          </v-btn>
        </template>
        <template v-slot:item-slot-name="{ header, item}">
          <search-table-name
            :icon="item.entityType.toUpperCase() === EntityType.PERSON ? 'mdi-account' : 'mdi-domain'"
            :name="header.itemFn(item)"
          />
        </template>
        <template v-slot:item-slot-action>
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
    <div id="load-more-results" style="text-align: center;">
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
import { computed, nextTick, onMounted, ref } from 'vue'
import _ from 'lodash'
// local
import { BaseTable, BCRegDateRangePicker, ErrorRetry } from '@/components'
import { useSearch } from '@/composables'
import { SearchEntityHeaders } from '@/resources/table-headers'
// internal
import { SearchTableAction, SearchTableName } from './common'
import { EntityType } from '@/enums'
import { toDateStr } from '@/utils'

// composables
const {
  facetCount,
  filterSearch,
  getNextResults,
  getSearchResults,
  hasMoreResults,
  search
} = useSearch()

// datepicker
const datePickerRef = ref(null)
const dateRangeResetTrigger = ref(false)
const dateRangeStart = ref(null)
const dateRangeEnd = ref(null)
const dateRangeSelected = computed(() => (dateRangeStart.value && dateRangeEnd.value) || false)
const dateFilterText = computed(() => {
  if (!dateRangeSelected.value) return ''
  const roleDates = search.filters?.query?.roles?.roleDates
  return `${roleDates.start}, ...`
})
const showDatePicker = ref(false)
const scrollToDatePicker = async () => {
  showDatePicker.value = true
  // await for datePicker ref to update
  await nextTick()
  if (datePickerRef.value?.$el?.scrollIntoView) {
    datePickerRef.value.$el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const updateDateRange = (val: { endDate: Date, startDate: Date }) => {
  showDatePicker.value = false
  dateRangeStart.value = val.startDate
  dateRangeEnd.value = val.endDate
  if (val.endDate && val.startDate) {
    filterSearch(['query','roles','roleDates'], { start: toDateStr(val.startDate), end: toDateStr(val.endDate) })
  } else {
    filterSearch(['query','roles','roleDates'], {})
  }
}

// text functions
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

// filter stuff
const resetFiltersTrigger = ref(false)

const clearFilters = () => {
  resetFiltersTrigger.value = !resetFiltersTrigger.value
  dateRangeResetTrigger.value = !dateRangeResetTrigger.value
  // search on reset filters
  filterSearch(null, null, true)
}

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

const getNextSearches = _.debounce(async () => getNextResults(), 50)
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

  &__clear-btn {
    background-color: transparent;
    bottom: 37%;
    box-shadow: none;
    height: 25px;
    position: absolute;
    right: 20%;
    width: 25px;
  }
}
</style>
