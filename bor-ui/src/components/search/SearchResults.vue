<template>
  <div>
    <div class="search-table">
      <base-table
        v-if="search.searchType === 'business'"
        id="businesses-table"
        class="rounded-top"
        height="100%"
        :itemKey="'identifier'"
        :loading="search._loading"
        overflow="hidden"
        :resetFilters="resetFilters"
        :resultsDescription="resultsDescBusiness"
        :setHeaders="BusinessSearchHeaders"
        :setItems="search.results"
        title="Search Results"
        :totalItems="search.totalResults"
        @resetFilters="resetFilters = false"
      >
        <template v-slot:header-filter-slot-action>
          <v-btn
            v-if="filtering"
            class="btn-basic-outlined search-table__clear"
            :append-icon="'mdi-window-close'"
            @click="clearFilters()"
          >
            Clear Filters
          </v-btn>
        </template>
        <template v-slot:item-slot-name="{ header, item}">
          <search-table-name icon="mdi-domain" :name="header.itemFn(item[header.col])" />
        </template>
        <template v-slot:item-slot-action="{ item }">
          <!-- @action="goToBusinessInfo(item)" -->
          <search-table-action
            :showBtn="learBusinessTypes.includes(item.legalType)"
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
      <base-table
        v-else
        id="owners-table"
        class="rounded-top"
        height="100%"
        :itemKey="'parentIdentifier'"
        :loading="search._loading"
        overflow="hidden"
        :resetFilters="resetFilters"
        :resultsDescription="resultsDescOwner"
        :setHeaders="PartySearchHeaders"
        :setItems="search.results"
        title="Search Results"
        :totalItems="search.totalResults"
        @resetFilters="resetFilters = false"
      >
        <template v-slot:header-filter-slot-action>
          <v-btn
            v-if="filtering"
            class="btn-basic-outlined search-table__clear"
            :append-icon="'mdi-window-close'"
            @click="clearFilters()"
          >
            Clear Filters
          </v-btn>
        </template>
        <template v-slot:item-slot-name="{ header, item }">
          <search-table-name
            :icon="item.partyType === 'person' ? 'mdi-account' : 'mdi-domain'"
            :name="header.itemFn(item[header.col])"
          />
        </template>
        <template v-slot:item-slot-roles="{ item }">
          <ul class="basic-list">
            <li v-for="(role, index) in item.partyRoles" :key="index">
              <span>{{ capFirstLetter(role) }}</span>
            </li>
          </ul>
        </template>
        <template v-slot:item-slot-action="{ item }">
          <!-- @action="goToBusinessFromParty(item)" -->
          <search-table-action
            :showBtn="learBusinessTypes.includes(item.parentLegalType)"
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
import { onMounted, ref, watch } from 'vue'
import { computed } from 'vue'
import _ from 'lodash'
// local
import { BaseTable, ErrorRetry } from '@/components'
import { useEntity, useSearch } from '@/composables'
import { BusinessSearchHeaders, PartySearchHeaders } from '@/resources/table-headers'
// internal
import { SearchTableAction, SearchTableName } from './common'

// composables
const { learBusinessTypes } = useEntity()
const { filtering, getNextResults, getSearchResults, hasMoreResults, search } = useSearch()

const resetFilters = ref(false)

const resultsDescBusiness = computed(() => search.results?.length === 1 ? 'Business' : 'Businesses')
const resultsDescOwner = computed(() => search.results?.length === 1 ? 'Firm Owner' : 'Firm Owners')

const tooltipMsg = 'You can access this business through BC OnLine or by contacting BC Registries. ' +
  'See "Help with Business Search" for details.'

const clearFilters = () => {
  for (const i in search.filters) { search.filters[i] = '' }
  updateTableHeaderFilters()
  resetFilters.value = true
}

const getNextSearches = _.debounce(async () => getNextResults(), 50)

const capFirstLetter = (val: string) => val.charAt(0).toUpperCase() + val.slice(1)

/** Update the base table header filters to display what the current filters are.
 * (needed when leaving and coming back to the component)
 */
const updateTableHeaderFilters = () => {
  const activeFilters = Object.keys(search.filters)
  for (const i in activeFilters) {
    // find header filter
    let header = BusinessSearchHeaders.find((item) => item.col === activeFilters[i])
    if (!header) header = PartySearchHeaders.find((item) => item.col === activeFilters[i])
    // update filter value to match search composable
    header.filter.value = search.filters[activeFilters[i]]
  }
}

// set table filters to session saved ones
onMounted(() => { updateTableHeaderFilters() })
watch(() => search.searchType, () => { updateTableHeaderFilters() })

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#businesses-table {
  border: solid 1px $gray2;

  @media (max-width: 1160px) {
    :deep(.base-table__header__item__title.v-btn.v-btn--density-default) {
      height: 60px;
    }
  }
}

#owners-table {
  border: solid 1px $gray2;

  @media (max-width: 1320px) {
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
