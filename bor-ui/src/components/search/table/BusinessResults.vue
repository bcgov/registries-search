<template>
  <base-table
    class="business-results rounded-t"
    height="100%"
    item-key="identifier"
    :loading="searchBusiness.loading"
    overflow="scroll"
    :reset-filters-trigger="resetFiltersTrigger"
    :results-description="resultsDesc"
    :set-headers="headers"
    :set-items="searchBusiness.results"
    title="Search Results"
    :title-extras="true"
    :total-items="searchBusiness.resultsTotal"
  >
    <template #header-filter-slot-action>
      <CommonHeadersClearFilters
        v-if="searchBusiness.filterActive"
        class="flex grow justify-center mb-4"
        @action="clearFilters()"
      />
    </template>
    <template #item-slot-name="{ item } : { item: RegSearchResultI }">
      <CommonItemsName
        icon="i-mdi-domain"
        :item="{ legalName: item.name }"
      />
    </template>
    <template #item-slot-action="{ item } : { item: RegSearchResultI }">
      <CommonItemsAction
        class="flex grow justify-center"
        :show-btn="ModernizedTypes.includes(item.legalType)"
        :tooltip-msg="tooltipMsg"
        @action="goToOpenBusiness(item.identifier)"
      />
    </template>
    <template v-if="searchBusiness.error" #body-empty>
      <bcros-error-retry
        class="my-5"
        :action="search.getSearchResults"
        :action-args="[searchBusiness.val]"
        message="We are unable to display your search results. Please try again later."
      />
    </template>
  </base-table>
</template>

<script setup lang="ts">
import { CommonHeadersClearFilters, CommonItemsAction, CommonItemsName } from './common'

defineProps<{ headers: BaseTableHeaderI[], resultsDesc: string }>()

const search = useBcrosSearch()
const { searchBusiness } = storeToRefs(search)

const clearFilters = () => {
  resetFiltersTrigger.value = !resetFiltersTrigger.value
  // search on reset filters
  search.filterSearch(null, null, true)
}

const goToOpenBusiness = (identifier: string) => {
  const { businessSearchURL } = useRuntimeConfig().public
  useBcrosNavigate().redirect(businessSearchURL + `/open/${identifier}`)
}

// filter clearing
const resetFiltersTrigger = ref(false)

const tooltipMsg = 'You can access this business through BC OnLine or by contacting BC Registries. ' +
  'See "Help with Business and Person Search" for details.'
</script>
<style lang="scss" scoped>
.child-row-item:not(:first-child) .inner-row-div {
  border-top: 1px solid theme('colors.gray.300');
  margin-top: 20px;
  padding-top: 20px;
}
</style>
