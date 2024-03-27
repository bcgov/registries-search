<template>
  <Teleport to="#date-range-filter-dest" :disabled="isVitestRunning">
    <BcrosDateRangePicker
      v-show="showDatePicker"
      ref="datePickerRef"
      :default-end-date="dateRangeEnd"
      :default-start-date="dateRangeStart"
      :offset-left="search.isExtended ? '284px' : '0px'"
      :reset="dateRangeResetTrigger"
      @submit="updateDateRange($event)"
    />
  </Teleport>
  <v-text-field
    v-model="dateFilterText"
    class="search-table__date-picker-filter active mb-5"
    append-inner-icon="mdi-calendar"
    density="compact"
    hide-details
    placeholder="Date"
    readonly
    @click="scrollToDatePicker()"
    @click:append-inner="scrollToDatePicker()"
  />
  <v-btn
    v-if="dateFilterText"
    class="search-table__clear-btn"
    icon
    @click="dateRangeResetTrigger = !dateRangeResetTrigger"
  >
    <v-icon color="primary" size="20">
      mdi-close
    </v-icon>
  </v-btn>
</template>
<script setup lang="ts">
const search = useBcrosSearch()

const datePickerRef = ref(null)
const dateRangeStart = ref(null)
const dateRangeEnd = ref(null)
const dateRangeSelected = computed(() => (dateRangeStart.value && dateRangeEnd.value) || false)
const dateFilterText = computed(() => {
  if (!dateRangeSelected.value) { return '' }
  const roleDates = search.filters?.query?.roles?.roleDates
  return `${roleDates.start}, ...`
})
const showDatePicker = ref(false)
const scrollToDatePicker = async () => {
  showDatePicker.value = true
  // await for datePicker ref to update
  await nextTick()
  if (datePickerRef.value?.$el?.scrollIntoView) {
    datePickerRef.value.$el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const updateDateRange = (val: { endDate: Date, startDate: Date }) => {
  showDatePicker.value = false
  dateRangeStart.value = val.startDate
  dateRangeEnd.value = val.endDate
  if (val.endDate && val.startDate) {
    search.filterSearch(
      ['query', 'roles', 'roleDates'],
      { start: toDateStr(val.startDate), end: toDateStr(val.endDate) }
    )
  } else {
    search.filterSearch(['query', 'roles', 'roleDates'], {})
  }
}

// for clear filters
const props = defineProps<{ dateRangeReset?: boolean }>()
const dateRangeResetTrigger = ref(false)
watch(() => props.dateRangeReset, () => {
  dateRangeResetTrigger.value = !dateRangeResetTrigger.value
})

// for teleport behaviour in tests
const isVitestRunning = !!process.env.VITEST_WORKER_ID
</script>
