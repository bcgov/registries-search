<script setup lang="ts">
import { SearchType, type SearchPayload } from '#imports'

const search = useSearchStore()
const { searchType, activeSearch } = storeToRefs(search)

const datePickerRef: Ref<any> = ref(undefined)
const dateRangeStart: Ref<Date | null> = ref(null)
const dateRangeEnd: Ref<Date | null> = ref(null)
const dateRangeSelected = computed(() => !!dateRangeStart.value && !!dateRangeEnd.value)
const dateFilterText = computed(() => dateRangeSelected.value ? '...' : '')
const showDatePicker = ref(false)
const scrollToDatePicker = async () => {
  showDatePicker.value = true
  // await for datePicker ref to update
  await nextTick()
  if (datePickerRef.value?.$el?.scrollIntoView) {
    datePickerRef.value.$el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const updateDateRange = (val: { endDate: Date | null, startDate: Date | null }, triggerSearch = true) => {
  showDatePicker.value = false
  dateRangeStart.value = val.startDate
  dateRangeEnd.value = val.endDate
  if (triggerSearch) {
    if (val.endDate && val.startDate) {
      search.filterSearch(
        ['query', 'roles', 'roleDates'],
        { start: toDateStr(val.startDate), end: toDateStr(val.endDate) }
      )
    } else {
      search.filterSearch(['query', 'roles', 'roleDates'], {})
    }
  }
}

// for clear filters
const props = defineProps<{ dateRangeReset?: boolean }>()
const dateRangeResetTrigger = ref(false)
watch(() => props.dateRangeReset, () => {
  dateRangeResetTrigger.value = !dateRangeResetTrigger.value
})

onMounted(() => {
  // apply existing filters to component
  const activeFilters = activeSearch.value.filters as SearchPayload
  const startDate = toDate(activeFilters?.query?.roles?.roleDates?.start || '') || null
  const endDate = toDate(activeFilters?.query?.roles?.roleDates?.end || '') || null
  if (startDate || endDate) {
    updateDateRange({ startDate, endDate }, false)
  }
})

// for teleport behaviour in tests
const isVitestRunning = !!process.env.VITEST_WORKER_ID
</script>

<template>
  <Teleport to="#date-range-filter-dest" :disabled="isVitestRunning">
    <DateRangePicker
      v-show="showDatePicker"
      ref="datePickerRef"
      :default-end-date="dateRangeEnd"
      :default-start-date="dateRangeStart"
      :offset-left="searchType === SearchType.PERSON ? '284px' : '0px'"
      :reset="dateRangeResetTrigger"
      @submit="updateDateRange($event)"
    />
  </Teleport>
  <UInput
    v-model="dateFilterText"
    :class="['w-full cursor-pointer', dateFilterText ? '*:bg-shade-highlighted' : '']"
    :placeholder="$t('label.date')"
    readonly
    size="lg"
    :ui="{ base: 'placeholder:text-neutral font-normal cursor-pointer', trailing: 'size-8' }"
    data-testid="base-table-header-filter"
    @click="scrollToDatePicker()"
    @click:append-inner="scrollToDatePicker()"
  >
    <template #trailing>
      <div>
        <UButton
          v-if="dateFilterText !== ''"
          class="absolute right-4 top-0"
          :disabled="false"
          color="primary"
          variant="link"
          icon="i-heroicons-x-mark-20-solid"
          :padded="false"
          @click="dateRangeResetTrigger = !dateRangeResetTrigger"
        />
        <UIcon
          class="absolute size-5 right-1 top-2"
          :class="dateFilterText ? 'text-primary' : ''"
          name="i-mdi-calendar"
        />
      </div>
    </template>
  </UInput>
</template>
