<script setup lang="ts">
defineProps<{ headers: BaseTableHeader[], resultsDesc: string }>()

const search = useSearchStore()
const { searchDirector } = storeToRefs(search)

const childHeaders = ['Roles', 'Effective Dates', 'Business Details', 'Business Status', 'Business Email']

// filter clearing
const resetFiltersTrigger = ref(false)
const dateRangeReset = ref(false)
</script>

<template>
  <BaseTable
    class="person-results rounded-t relative"
    height="100%"
    :item-key="'legalName'"
    :loading="searchDirector.loading"
    overflow="scroll"
    :reset-filters-trigger="resetFiltersTrigger"
    :results-description="resultsDesc"
    :set-headers="headers"
    :set-items="searchDirector.results"
    :title="$t('label.searchResults')"
    :title-extras="true"
    :total-items="searchDirector.resultsTotal"
  >
    <template #title-extras>
      <SearchTableCommonTitleExport v-model:export-rows="searchDirector.exportRows" />
    </template>
    <template #header-filter-slot-date>
      <SearchTableCommonHeadersDateRangeFilter :date-range-reset="dateRangeReset" />
    </template>
    <template #item-slot-name="{ item }">
      <SearchTableCommonItemsName
        icon="i-mdi-account"
        :item="item"
      />
    </template>
    <template #item-slot-address="{ item }">
      <ConnectAddressDisplay
        v-if="item.entityAddresses"
        :address="formatAddress(item.entityAddresses[0])"
      />
      <span v-else>N/A</span>
    </template>
    <template #item-slot-roles="{ item }">
      <div
        v-for="role, i in item.roles"
        :key="'child-role-' + i"
        class="mt-3"
      >
        <div class="flex w-full" data-testid="inner-row-div">
          <div :style="{ width: getChildHeaderWidth(headers, 'Roles', childHeaders) }" data-testid="inner-col-div">
            <div>
              {{ capFirstLetter(`${role.roleType}`) }}
            </div>
          </div>
          <div
            class="pl-2 mr-0"
            :style="{ width: getChildHeaderWidth(headers, 'Effective Dates', childHeaders) }"
            data-testid="inner-col-div"
          >
            <SearchTableCommonItemsEffectiveDates :role="role" />
          </div>
          <div
            class="pl-2"
            :style="{ width: getChildHeaderWidth(headers, 'Business Details', childHeaders) }"
            data-testid="inner-col-div"
          >
            <SearchTableCommonItemsBusinessDetails :role="role" />
          </div>
          <div
            class="pl-2"
            :style="{ width: getChildHeaderWidth(headers, 'Business Status', childHeaders) }"
            data-testid="inner-col-div"
          >
            {{ capFirstLetter(`${role.relatedState}`) }}
          </div>
          <div
            class="pl-2"
            :style="{ width: getChildHeaderWidth(headers, 'Business Email', childHeaders) }"
            data-testid="inner-col-div"
          >
            {{ role.relatedEmail || '' }}
          </div>
        </div>
      </div>
    </template>
    <template v-if="searchDirector.error" #body-empty>
      <ErrorRetry
        class="my-5"
        :action="search.getSearchResults"
        :action-args="[searchDirector.val]"
        :message="$t('text.errorRetrySearch')"
      />
    </template>
  </BaseTable>
</template>
