<template>
  <UPopover class="mb-5" :popper="{ placement: 'bottom-start', locked: true }">
    <UInput
      v-model="detailsFilterDisplay"
      class="font-normal"
      placeholder="Details"
      size="sm"
      trailing
      :ui="{ icon: { trailing: { pointer: '' } }, base: 'cursor-pointer text-left', default: { class: 'bg-gray-100' } }"
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

const t = useNuxtApp().$i18n.t

const detailsFilterDisplay = computed(() => {
  // return selectedDetailsFilters.value
  if (selectedDetailsFilters.value.length === 0) {
    return ''
  }

  if (selectedDetailsFilters.value.length === 1) {
    return convertDetailsToIcon(selectedDetailsFilters.value[0])?.displayName || t('text.table.defaultSelected')
  }

  return t('text.table.multiple')
})

const options = [
  {
    label: t('label.control.shareControl'),
    subOptions: [
      { label: t('label.control.registeredOwner'), value: PersonControlTypeE.SHARES_REG_OWNER },
      { label: t('label.control.beneficialOwner'), value: PersonControlTypeE.SHARES_BEN_OWNER },
      { label: t('label.control.indirectControl'), value: PersonControlTypeE.SHARES_INDIRECT },
      { label: t('label.control.inConcert'), value: PersonControlTypeE.SHARES_INCONCERT },
      { label: t('label.control.actingJointly'), value: PersonControlTypeE.SHARES_JOINTLY }
    ]
  },
  {
    label: t('label.control.voteControl'),
    subOptions: [
      { label: t('label.control.registeredOwner'), value: PersonControlTypeE.VOTES_REG_OWNER },
      { label: t('label.control.beneficialOwner'), value: PersonControlTypeE.VOTES_BEN_OWNER },
      { label: t('label.control.indirectControl'), value: PersonControlTypeE.VOTES_INDIRECT },
      { label: t('label.control.inConcert'), value: PersonControlTypeE.VOTES_INCONCERT },
      { label: t('label.control.actingJointly'), value: PersonControlTypeE.VOTES_JOINTLY }
    ]
  },
  {
    label: t('label.control.directorControl'),
    subOptions: [
      { label: t('label.control.indirectControl'), value: PersonControlTypeE.DIRS_INDIRECT },
      { label: t('label.control.directControl'), value: PersonControlTypeE.DIRS_DIRECT },
      { label: t('label.control.significantInfluence'), value: PersonControlTypeE.DIRS_SIG_INFL },
      { label: t('label.control.inConcert'), value: PersonControlTypeE.DIRS_INCONCERT },
      { label: t('label.control.actingJointly'), value: PersonControlTypeE.DIR_JOINTLY }
    ]
  },
  {
    label: t('label.control.other'),
    subOptions: [
      { label: t('label.control.other'), value: PersonControlTypeE.OTHER }
    ]
  }
]

const { filterSearch } = useBcrosSearch()
watch(selectedDetailsFilters, (newList: string[], oldList: string[]) => {
  if (oldList.length === 0 && newList.length === 0) {
    return
  }
  filterSearch(['categories', 'roles', 'relatedInterests'], newList)
})

</script>

<style lang="scss" scoped>
</style>
