<template>
  <v-menu
    :close-on-content-click="false"
  >
    <template #activator="{ isActive, props }">
      <div class="pb-5 cursor-pointer" data-cy="details-filter">
        <v-text-field
          v-model="detailsFilterDisplay"
          density="compact"
          hide-details
          v-bind="props"
          :append-inner-icon="isActive ? 'mdi-menu-up' : 'mdi-menu-down' "
          placeholder="Details"
          data-cy="details-filter-textbox"
          :class="['base-table__header__item__filter', detailsFilterDisplay!='' ? 'active' : '']"
        />
        <BaseTableFilterClearButton v-if="detailsFilterDisplay!=''" right="25px" @click="selectedDetailsFilters=[]" />
      </div>
    </template>
    <v-expansion-panels
      variant="accordion"
      multiple
    >
      <v-expansion-panel data-cy="details-filter-shares-votes" class="w-52 max-w-52">
        <v-expansion-panel-title class="font-bold">
          Control of Shares/Votes
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Registered Owner"
            :value="PersonControlTypeE.SharesOrVotesRegisteredOwner"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-200 hover:text-blue-500"
            data-cy="details-filter-shares-votes-registered-owner"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Beneficial Owner"
            :value="PersonControlTypeE.SharesOrVotesBeneficialOwner"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-500"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Indirect Control"
            :value="PersonControlTypeE.SharesOrVotesIndirectControl"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-500"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>

      <v-expansion-panel data-cy="details-filter-directors" class="w-52 max-w-52">
        <v-expansion-panel-title class="font-bold">
          Control of Directors
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Indirect Control of directors"
            :value="PersonControlTypeE.DirectorsIndirectControl"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-500"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Direct Control"
            :value="PersonControlTypeE.DirectorsDirectControl"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-500 color:primary"
            data-cy="details-filter-directors-direct-control"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Control Majority of Directors"
            :value="PersonControlTypeE.DirectorsInConcertControl"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-500"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Significant Influence Control"
            :value="PersonControlTypeE.DirectorsSignificantInfluence"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-500"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>
      <v-expansion-panel data-cy="details-filter-other" class="w-52 max-w-52">
        <v-expansion-panel-title class="font-bold">
          Other
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Other"
            value="other"
            density="comfortable"
            hide-details
            class="uppercase px-3 hover:bg-gray-300 hover:text-blue-500"
            data-cy="details-filter-other-other"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-menu>
</template>

<script setup lang="ts">
const search = useBcrosSearch()
const selectedDetailsFilters: Ref<string[]> = ref([])

// for clear filters
const localProps = defineProps<{ clearFilter?: boolean }>()
watch(() => localProps.clearFilter, () => {
  selectedDetailsFilters.value = []
})

const detailsFilterDisplay = computed(() => {
  if (selectedDetailsFilters.value.length === 0) {
    return ''
  }

  if (selectedDetailsFilters.value.length === 1) {
    let icon = convertDetailsToIcon(selectedDetailsFilters.value[0])
    if (!icon) {
      icon = OtherControlIcon
    }
    return icon.displayName
  }

  return 'Multiple'
})

watch(selectedDetailsFilters, (newList: string[], oldList: string[]) => {
  if (oldList.length === 0 && newList.length === 0) {
    return
  }
  search.filterSearch(['categories', 'roles', 'relatedInterests'], selectedDetailsFilters.value)
})

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
:deep .v-expansion-panel-text__wrapper {
  padding: 0;
  background-color: transparent !important;
}

// NOTE: to match other selects
:deep(.v-field__input), :deep(.v-field__append-inner), :deep(.v-field) {
  cursor: pointer;
}

// NOTE: below should match base table styling
:deep(.v-input__control .v-field--active.v-field--dirty .v-field__overlay) {
  background-color: $blueSelected !important;
}
</style>
