<template>
  <base-table
    class="person-results-public rounded-t"
    height="100%"
    :item-key="'legalName'"
    :loading="searchPerson.loading"
    overflow="scroll"
    :reset-filters-trigger="resetFiltersTrigger"
    :results-description="resultsDesc"
    :set-headers="headers"
    :set-items="searchPerson.results"
    title="Search Results"
    :title-extras="true"
    :total-items="searchPerson.resultsTotal"
  >
    <template #item-loading-slot-actions>
      <div class="h-[83px] pt-[26px] pb-4 px-3 shadow-action-col-item bg-white">
        <div class="w-full h-10 bg-gray-300 rounded" />
      </div>
    </template>
    <template #item-slot-name="{ item } : { item: SearchResultI }">
      <CommonItemsName :item="item" icon="i-mdi-account" />
    </template>
    <template #item-slot-citizenship="{ item } : { item: SearchResultI }">
      <div class="flex justify-center">
        <CommonItemsCitizenship :item="item" />
      </div>
    </template>
    <template #item-slot-details="{ item } : { item: SearchResultI }">
      <div v-for="role, i in item.roles" :key="'child-role-' + i" class="child-row-item">
        <div class="inner-row-div flex w-full">
          <div
            class="inner-col-div pl-3"
            :style="{ width: getChildHeaderWidth(headers, 'Business Details', childHeaders) }"
          >
            <CommonItemsBusinessDetails :role="role" />
          </div>
          <div class="inner-col-div pl-3" :style="{ width: getChildHeaderWidth(headers, 'Roles', childHeaders) }">
            {{ capFirstLetter(`${role.roleType}`) }}
          </div>
        </div>
      </div>
    </template>
    <!-- <template #item-slot-actions="{ item } : { item: SearchResultI }">
      <div class="h-full w-full px-3 pt-3 shadow-action-col-item">
        <CommonItemsAction show-btn @action="console.info('clicked open on', item.legalName)" />
      </div>
    </template> -->
    <template v-if="searchPerson.error" #body-empty>
      <bcros-error-retry
        class="my-5"
        :action="search.getSearchResults"
        :action-args="[searchPerson.val]"
        message="We are unable to display your search results. Please try again later."
      />
    </template>
  </base-table>
</template>

<script setup lang="ts">
import {
  CommonItemsBusinessDetails, CommonItemsName, CommonItemsCitizenship
} from './common'

const props = defineProps<{
  resultsDesc: string,
  updateTableHeaderFilters:(val: BaseTableHeaderI[]) => void,
}>()

const search = useBcrosSearch()
const { searchPerson } = storeToRefs(search)

// search table config (headers)
const headers = getPersonHeadersPublic()
const childHeaders: string[] = ['Business Details', 'Roles']
// set table filters to session saved ones
onMounted(() => { props.updateTableHeaderFilters(headers) })

// filter clearing
const resetFiltersTrigger = ref(false)
</script>
<style lang="scss" scoped>
.child-row-item:not(:first-child) .inner-row-div {
  border-top: 1px solid theme('colors.gray.300');
  margin-top: 20px;
  padding-top: 20px;
}
</style>
