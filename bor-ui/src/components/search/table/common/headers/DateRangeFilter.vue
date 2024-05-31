<template>
  <Teleport to="#date-range-filter-dest" :disabled="isVitestRunning">
    <BcrosDateRangePicker
      v-show="showDatePicker"
      ref="datePickerRef"
      :default-end-date="dateRangeEnd"
      :default-start-date="dateRangeStart"
      :offset-left="search.hasExtendedAccess ? '284px' : '0px'"
      :reset="dateRangeResetTrigger"
      @submit="updateDateRange($event)"
    />
  </Teleport>
  <UInput
    class="font-normal mb-5"
    autocomplete="off"
    :color="dateFilterText ? 'primary' : 'gray'"
    size="sm"
    placeholder="Date"
    readonly
    :value="dateFilterText"
    :ui="{ icon: { trailing: { pointer: '' }}, base: 'cursor-pointer text-left'}"
    @click="scrollToDatePicker()"
    @click:append-inner="scrollToDatePicker()"
  >
    <template #trailing>
      <div class="flex">
        <UIcon class="text-xl" name="i-mdi-calendar" />
        <UButton
          v-show="dateFilterText !== ''"
          color="primary"
          variant="link"
          icon="i-heroicons-x-mark-20-solid"
          :padded="false"
          @click="dateRangeResetTrigger = !dateRangeResetTrigger"
        />
      </div>
    </template>
  </UInput>
</template>
<script setup lang="ts">

const search = useBcrosSearch()

const datePickerRef = ref(null)
const dateRangeStart = ref(null)
const dateRangeEnd = ref(null)
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
