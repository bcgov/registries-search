<script setup lang="ts">
const selectedDetailsFilters: Ref<string[]> = ref([])

const props = defineProps<{ clearFilter?: boolean }>()
watch(() => props.clearFilter, () => {
  selectedDetailsFilters.value = []
})

const t = useNuxtApp().$i18n.t

const detailsFilterDisplay = computed(() => {
  if (selectedDetailsFilters.value.length === 0) {
    return t('label.details')
  }

  if (selectedDetailsFilters.value.length === 1) {
    return convertDetailsToIcon(selectedDetailsFilters.value[0])?.displayName || t('label.oneSelected')
  }

  return t('label.multiple')
})

const options = [
  {
    label: t('label.controlShares'),
    subOptions: [
      { label: t('label.registeredOwner'), value: PersonControlType.SHARES_REG_OWNER },
      { label: t('label.beneficialOwner'), value: PersonControlType.SHARES_BEN_OWNER },
      { label: t('label.indirectControl'), value: PersonControlType.SHARES_INDIRECT },
      { label: t('label.actingInConcert'), value: PersonControlType.SHARES_INCONCERT },
      { label: t('label.actingJointly'), value: PersonControlType.SHARES_JOINTLY }
    ]
  },
  {
    label: t('label.controlVotes'),
    subOptions: [
      { label: t('label.registeredOwner'), value: PersonControlType.VOTES_REG_OWNER },
      { label: t('label.beneficialOwner'), value: PersonControlType.VOTES_BEN_OWNER },
      { label: t('label.indirectControl'), value: PersonControlType.VOTES_INDIRECT },
      { label: t('label.actingInConcert'), value: PersonControlType.VOTES_INCONCERT },
      { label: t('label.actingJointly'), value: PersonControlType.VOTES_JOINTLY }
    ]
  },
  {
    label: t('label.directorControl'),
    subOptions: [
      { label: t('label.indirectControl'), value: PersonControlType.DIRS_INDIRECT },
      { label: t('label.directControl'), value: PersonControlType.DIRS_DIRECT },
      { label: t('label.significantInfluence'), value: PersonControlType.DIRS_SIG_INFL },
      { label: t('label.actingInConcert'), value: PersonControlType.DIRS_INCONCERT },
      { label: t('label.actingJointly'), value: PersonControlType.DIR_JOINTLY }
    ]
  },
  {
    label: t('label.other'),
    subOptions: [
      { label: t('label.other'), value: PersonControlType.OTHER }
    ]
  }
]

const { filterSearch } = useSearchStore()
watch(selectedDetailsFilters, (newList: string[], oldList: string[]) => {
  if (oldList.length === 0 && newList.length === 0) {
    return
  }
  filterSearch(['categories', 'roles', 'relatedInterests'], toRaw(newList))
})
</script>

<template>
  <UPopover
    :content="{
      align: 'start',
      side: 'bottom',
    }"
  >
    <UInput
      v-model="detailsFilterDisplay"
      class="w-full cursor-pointer"
      :class="selectedDetailsFilters.length > 0 ? 'bg-shade-highlighted' : ''"
      size="lg"
      :ui="{
        base: [
          (selectedDetailsFilters.length > 0 ? 'text-highlighted bg-shade-highlighted' : 'text-neutral'),
          'text-ellipsis text-left font-normal cursor-pointer',
        ],
      }"
      data-testid="control-filter"
    >
      <template #trailing>
        <UButton
          v-if="selectedDetailsFilters.length > 0"
          class="absolute right-4 top-0"
          color="primary"
          variant="link"
          icon="i-heroicons-x-mark-20-solid"
          :padded="false"
          @click="selectedDetailsFilters = []"
        />
        <UIcon name="i-mdi-arrow-drop-down" class="size-5 text-neutral absolute right-1 top-2" />
      </template>
    </UInput>
    <template #content>
      <UAccordion
        class="w-full"
        :items="options"
        data-testid="control-filter-accordion"
      >
        <template #body="{ item }">
          <UCheckboxGroup
            v-model="selectedDetailsFilters"
            :items="item.subOptions"
          />
        </template>
      </UAccordion>
    </template>
  </UPopover>
</template>
