<template>
  <UPopover class="mb-5" :popper="{ placement: 'bottom-start', locked: true }">
    <UInput
      v-model="detailsFilterDisplay"
      class="font-normal"
      placeholder="Details"
      size="sm"
      trailing
      :ui="{ icon: { trailing: { pointer: '' }}, base: 'cursor-pointer text-left'}"
      data-cy="control-filter"
    >
      <template #trailing>
        <UButton
          v-if="detailsFilterDisplay"
          color="primary"
          variant="link"
          icon="i-heroicons-x-mark-20-solid"
          :padded="false"
          @click="selectedDetailsFilters = []"
        />
        <UIcon class="text-xl text-gray-700" name="i-mdi-chevron-down" />
      </template>
    </UInput>
    <template #panel>
      <UAccordion
        :items="options"
        multiple
        data-cy="control-filter-accordion"
      >
        <template #item="{ item }">
          <UCheckbox
            v-for="option in item.subOptions"
            :key="option.value"
            v-model="selectedDetailsFilters"
            class="px-3 py-2"
            :label="option.label"
            :value="option.value"
            :data-cy="'control-filter-checkbox-' + option.value"
          />
        </template>
      </UAccordion>
    </template>
  </UPopover>
</template>

<script setup lang="ts">
const selectedDetailsFilters: Ref<string[]> = ref([])

const props = defineProps<{ clearFilter?: boolean }>()
watch(() => props.clearFilter, () => {
  selectedDetailsFilters.value = []
})

const detailsFilterDisplay = computed(() => {
  // return selectedDetailsFilters.value
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

const options = [
  {
    label: 'Control of Shares/Votes',
    subOptions: [
      { label: 'Registered Owner', value: PersonControlTypeE.SharesOrVotesRegisteredOwner },
      { label: 'Beneficial Owner', value: PersonControlTypeE.SharesOrVotesBeneficialOwner },
      { label: 'Indirect Control', value: PersonControlTypeE.SharesOrVotesIndirectControl }
    ]
  },
  {
    label: 'Control of Directors',
    subOptions: [
      { label: 'Indirect Control', value: PersonControlTypeE.DirectorsIndirectControl },
      { label: 'Direct Control', value: PersonControlTypeE.DirectorsDirectControl },
      { label: 'Majority Control', value: PersonControlTypeE.DirectorsInConcertControl },
      { label: 'Significant Influence Control', value: PersonControlTypeE.DirectorsSignificantInfluence }
    ]
  },
  {
    label: 'Other',
    subOptions: [
      { label: 'Other', value: PersonControlTypeE.Other }
    ]
  }
]

const search = useBcrosSearch()
watch(selectedDetailsFilters, (newList: string[], oldList: string[]) => {
  if (oldList.length === 0 && newList.length === 0) {
    return
  }
  search.filterSearch(['categories', 'roles', 'relatedInterests'], selectedDetailsFilters.value)
})

</script>

<style lang="scss" scoped>
</style>
