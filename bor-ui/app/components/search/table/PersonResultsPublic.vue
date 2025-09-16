<script setup lang="ts">
defineProps<{ headers: BaseTableHeader[], resultsDesc: string }>()

const search = useSearchStore()
const { searchPerson } = storeToRefs(search)

const childHeaders: string[] = ['Business Details', 'Roles']

// filter clearing
const resetFiltersTrigger = ref(false)
</script>

<template>
  <BaseTable
    class="person-results-public rounded-t"
    height="100%"
    :item-key="'legalName'"
    :loading="searchPerson.loading"
    overflow="scroll"
    :reset-filters-trigger="resetFiltersTrigger"
    :results-description="resultsDesc"
    :set-headers="headers"
    :set-items="searchPerson.results"
    :title="$t('label.searchResults')"
    :title-extras="true"
    :total-items="searchPerson.resultsTotal"
  >
    <template #item-loading-slot-actions>
      <div class="h-[83px] pt-[26px] pb-4 px-3 shadow-action-col-item">
        <div class="w-full h-10 bg-gray-300 rounded" />
      </div>
    </template>
    <template #item-slot-name="{ item }">
      <SearchTableCommonItemsName :item="item" icon="i-mdi-account" />
    </template>
    <template #item-slot-citizenship="{ item }">
      <div class="flex justify-center">
        <SearchTableCommonItemsCitizenship :item="item" />
      </div>
    </template>
    <template #item-slot-details="{ item }">
      <div
        v-for="role, i in item.roles"
        :key="'child-role-' + i"
        class="mt-3"
      >
        <div class="flex w-full" data-testid="inner-row-div">
          <div
            :style="{ width: getChildHeaderWidth(headers, 'Business Details', childHeaders) }"
            data-testid="inner-col-div"
          >
            <SearchTableCommonItemsBusinessDetails :role="role" />
          </div>
          <div :style="{ width: getChildHeaderWidth(headers, 'Roles', childHeaders) }" data-testid="inner-col-div">
            {{ capFirstLetter(`${role.roleType}`) }}
          </div>
        </div>
      </div>
    </template>
    <template v-if="searchPerson.error" #body-empty>
      <ErrorRetry
        class="my-5"
        :action="search.getSearchResults"
        :action-args="[searchPerson.val]"
        :message="$t('text.errorRetrySearch')"
      />
    </template>
  </BaseTable>
</template>
