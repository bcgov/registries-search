<template>
  <v-menu
    :close-on-content-click="false"
  >
    <template #activator="{ isActive, props }">
      <div class="pb-5 person-details-filter" data-cy="details-filter">
        <v-text-field
          v-model="detailsFilterDisplay"
          density="compact"
          hide-details
          v-bind="props"
          clearable
          clear-icon="mdi-close"
          :append-inner-icon="isActive ? 'mdi-menu-up' : 'mdi-menu-down' "
          placeholder="Details"
          data-cy="details-filter-textbox"
          @click:clear="selectedDetailsFilters=[]"
        />
      </div>
    </template>
    <v-expansion-panels
      variant="accordion"
      multiple
      class="accordion-filter"
    >
      <v-expansion-panel class="expansion-panel" data-cy="details-filter-shares-votes">
        <v-expansion-panel-title class="expansion-panel-title">
          Control of Shares/Votes
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Registered Owner"
            :value="PersonControlTypeE.SharesOrVotesRegisteredOwner"
            data-cy="details-filter-shares-votes-registered-owner"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Beneficial Owner"
            :value="PersonControlTypeE.SharesOrVotesBeneficialOwner"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Indirect Control"
            :value="PersonControlTypeE.SharesOrVotesIndirectControl"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>

      <v-expansion-panel class="expansion-panel" data-cy="details-filter-directors">
        <v-expansion-panel-title class="expansion-panel-title">
          Control of Directors
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Indirect Control of directors"
            :value="PersonControlTypeE.DirectorsIndirectControl"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Direct Control"
            :value="PersonControlTypeE.DirectorsDirectControl"
            data-cy="details-filter-directors-direct-control"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Control Majority of Directors"
            :value="PersonControlTypeE.DirectorsInConcertControl"
          />
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Significant Influence Control"
            :value="PersonControlTypeE.DirectorsSignificantInfluence"
          />
        </v-expansion-panel-text>
      </v-expansion-panel>
      <v-expansion-panel class="expansion-panel" data-cy="details-filter-other">
        <v-expansion-panel-title class="expansion-panel-title">
          Other
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-checkbox
            v-model="selectedDetailsFilters"
            label="Other"
            value="other"
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
const props = defineProps<{ clearFilter?: boolean }>()
watch(() => props.clearFilter, () => {
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
  search.filterSearch(['query', 'roles', 'relatedInterests'], selectedDetailsFilters.value)
})

</script>

<style>

.expansion-panel-title {
  font-weight: bold;
  font-size: smaller
}

.person-details-filter {
  cursor: pointer;
}
</style>
