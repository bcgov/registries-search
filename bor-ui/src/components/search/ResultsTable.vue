<template>
  <div data-cy="search-results-table">
    <BcrosDateRangePicker
      v-show="showDatePicker"
      ref="datePickerRef"
      :default-end-date="dateRangeEnd"
      :default-start-date="dateRangeStart"
      :reset="dateRangeResetTrigger"
      @submit="updateDateRange($event)"
    />
    <div class="search-table">
      <base-table
        id="entity-results"
        class="rounded-top"
        height="100%"
        :item-key="'legalName'"
        :loading="search._loading"
        overflow="hidden"
        :reset-filters-trigger="resetFiltersTrigger"
        :results-description="resultsDesc"
        :set-headers="searchEntityHeaders"
        :set-items="search.results"
        title="Search Results"
        :title-extras="true"
        :total-items="search.totalResults"
      >
        <template #title-extras>
          <v-row no-gutters justify="end">
            <v-col align-self="center" cols="auto">
              <v-select
                v-model="search.exportRows"
                class="search-table__export-select pt-1 rounded-top"
                density="default"
                hide-details
                :items="[50,100,250,500,1000,2000]"
                label="Maximum results to export"
                style="width: 225px;"
                variant="underlined"
              />
            </v-col>
            <v-col align-self="center" cols="auto">
              <v-btn
                class="search-table__export-rows-btn"
                color="primary"
                density="compact"
                :loading="exportLoading"
                prepend-icon="mdi-table-arrow-down"
                :ripple="false"
                variant="text"
                @click="exportToXlsx()"
              >
                Export to .xlsx
              </v-btn>
            </v-col>
          </v-row>
        </template>
        <template #header-filter-slot-date>
          <v-text-field
            v-model="dateFilterText"
            class="search-table__date-picker-filter active"
            append-inner-icon="mdi-calendar"
            density="compact"
            hide-details
            placeholder="Date"
            readonly
            @click="scrollToDatePicker()"
            @click:append-inner="scrollToDatePicker()"
          />
          <v-btn
            v-if="dateFilterText"
            class="search-table__clear-btn"
            icon
            @click="dateRangeResetTrigger = !dateRangeResetTrigger"
          >
            <v-icon color="primary" size="20">
              mdi-close
            </v-icon>
          </v-btn>
        </template>
        <template #header-filter-slot-action>
          <v-btn
            v-if="search._isFilteringActive"
            class="search-table__clear"
            :append-icon="'mdi-window-close'"
            color="primary"
            variant="outlined"
            @click="clearFilters()"
          >
            Clear Filters
          </v-btn>
        </template>
        <template #item-slot-name="{ header, item}">
          <search-table-name
            :icon="item.entityType.toUpperCase() === EntityTypeE.PERSON ? 'mdi-account' : 'mdi-domain'"
            :name="header.itemFn(item)"
          />
        </template>
        <template #item-slot-details="{ item } : { item: SearchResultI }">
          <div v-if="item.roles">
            <a :href="getItemDetailsLink(item)" target="_blank">
              {{ item.roles[0].relatedName }}
              <v-icon
                v-if="!isModernized(item)"
                class="mb-1"
                color="primary"
                icon="mdi-open-in-new"
                size="small"
              />
            </a>
            <br>
            {{ item.roles[0].relatedIdentifier }}
            <br>
            {{ item.roles[0].relatedBN }}
          </div>
          <span v-else>N/A</span>
        </template>
        <!-- <template v-slot:item-slot-action>
          <search-table-action
            :showBtn="false"
            :tooltipMsg="tooltipMsg"
          />
        </template> -->
        <template v-if="search._error" #body-empty>
          <bcros-error-retry
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
        class="mt-30px"
        :loading="search._loadingNext"
        color="primary"
        variant="outlined"
        @click="getNextSearches()"
      >
        Load More Results
      </v-btn>
    </div>
    <v-snackbar :model-value="showExportSnack">
      Search results successfully exported in the order displayed in the table.
      <template #actions>
        <v-btn icon="mdi-window-close" @click="showExportSnack = false" />
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import _ from 'lodash'
import { SearchTableName } from './common'

// composables
const {
  facetCount,
  exportSearch,
  filterSearch,
  getNextResults,
  getSearchResults,
  hasMoreResults,
  search
} = useSearch()

const searchEntityHeaders = getSearchEntityHeaders()

// datepicker
const datePickerRef = ref(null)
const dateRangeResetTrigger = ref(false)
const dateRangeStart = ref(null)
const dateRangeEnd = ref(null)
const dateRangeSelected = computed(() => (dateRangeStart.value && dateRangeEnd.value) || false)
const dateFilterText = computed(() => {
  if (!dateRangeSelected.value) { return '' }
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
    filterSearch(['query', 'roles', 'roleDates'], { start: toDateStr(val.startDate), end: toDateStr(val.endDate) })
  } else {
    filterSearch(['query', 'roles', 'roleDates'], {})
  }
}

// business details link
const businessSearchURL = sessionStorage.getItem('REGISTRIES_SEARCH_URL')
const bcolURL = sessionStorage.getItem('BCONLINE_URL')
const isModernized = (item: SearchResultI) => {
  const modernizedTypes = [
    CorpTypeCdE.BENEFIT_COMPANY,
    CorpTypeCdE.COOP,
    CorpTypeCdE.SOLE_PROP,
    CorpTypeCdE.PARTNERSHIP
  ]
  return modernizedTypes.includes(item.roles[0].relatedLegalType)
}
const getItemDetailsLink = (item: SearchResultI) => {
  if (isModernized(item)) {
    return `${businessSearchURL}?identifier=${item.roles[0].relatedIdentifier}`
  }
  return bcolURL
}

// text functions
const resultsDesc = computed(() => {
  let desc = ''
  if (search.filters.categories.entityType?.includes(EntityTypeE.PERSON)) {
    const count = facetCount('entityType', EntityTypeE.PERSON)
    desc += `${count} ${count === 1 ? 'Person' : 'People'}`
  }
  if (search.filters.categories.entityType?.includes(EntityTypeE.BUSINESS)) {
    const count = facetCount('entityType', EntityTypeE.BUSINESS)
    if (desc) { desc += ', ' }
    desc += `${count} ${count === 1 ? 'Business' : 'Businesses'}`
  }
  return desc
})

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
    const header = searchEntityHeaders.find(item => item.col === activeFilters[i])
    // update filter value to match search composable
    if (header) { header.filter.value = search.filters[activeFilters[i]] }
  }
}

// Exporting to excel stuff
const exportLoading = ref(false)
const showExportSnack = ref(false)

/** Export search results into an .xlsx download file. */
const exportToXlsx = _.debounce(async () => {
  exportLoading.value = true
  await exportSearch()
  exportLoading.value = false
  if (!search._error) { showExportSnack.value = true }
}, 50, { leading: true, trailing: false })

// set table filters to session saved ones
onMounted(() => { updateTableHeaderFilters() })

const getNextSearches = _.debounce(async () => (await getNextResults()), 50)
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

    :deep(.v-btn__append) {
      margin-left: 4px;
      margin-top: 2px;
    }
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

  &__export-select {
    background-color: white;
    :deep(.v-field.v-field--active:not(.v-field--error) .v-label.v-field-label--floating) {
      color: $gray7;
      margin-left: 9px;
    }
    :deep(.v-field__append-inner) {
      margin-right: 12px;
    }
    :deep(.v-select__selection) {
      font-size: 16px;
      margin-bottom: 4px;
    }
  }
}
</style>
