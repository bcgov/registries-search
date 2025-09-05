<!-- TODO: will be replaced by common component #30551 -->
<script setup lang="ts">
const props = defineProps<{
  defaultEndDate?: Date | null
  defaultStartDate?: Date | null
  offsetLeft?: string
  offsetTop?: string
  reset?: boolean
}>()
const emit = defineEmits<{ (e: 'submit', value: { endDate: Date | null, startDate: Date | null }): void }>()

const datePickerErr = ref(false)
const endDate: Ref<Date | null> = ref(props.defaultEndDate || null)
const startDate: Ref<Date | null> = ref(props.defaultStartDate || null)
const resetTrigger = ref(false)

const resetDateRange = (): void => {
  resetTrigger.value = !resetTrigger.value
  datePickerErr.value = false
  emit('submit', { endDate: null, startDate: null })
}
watch(() => props.reset, () => {
  resetDateRange()
})

const submitDateRange = (): void => {
  if (!startDate.value || !endDate.value) {
    datePickerErr.value = true
    return
  }
  datePickerErr.value = false
  emit('submit', { endDate: endDate.value, startDate: startDate.value })
}
</script>

<template>
  <div
    ref="datePicker"
    class="date-selection shadow-[0px_3px_6px_2px_#0003] py-8"
    :style="{ 'margin-top': offsetTop ? offsetTop : '264px', 'margin-left': offsetLeft ? offsetLeft : '0px' }"
  >
    <div class="flex space-x-5 justify-center">
      <div>
        <b class="date-selection__heading" :class="{ 'picker-err': startDate === null && datePickerErr }">
          Select Start Date:
        </b>
        <BaseDatePicker
          class="date-selection__picker mt-2"
          :error="startDate === null && datePickerErr"
          :reset-trigger="resetTrigger"
          :set-max-date="endDate"
          @selected-date="startDate = $event"
        />
      </div>
      <div class="pl-4">
        <b class="date-selection__heading" :class="{ 'picker-err': endDate === null && datePickerErr }">
          Select End Date:
        </b>
        <BaseDatePicker
          class="date-selection__picker mt-2"
          :error="endDate === null && datePickerErr"
          :reset-trigger="resetTrigger"
          :set-min-date="startDate"
          @selected-date="endDate = $event"
        />
        <div class="flex space-x-4 justify-end pt-4">
          <UButton
            class="font-bold hover:bg-inherit"
            label="OK"
            color="primary"
            variant="ghost"
            data-testid="date-selection-btn"
            @click="submitDateRange()"
          />
          <UButton
            class="font-normal hover:bg-inherit"
            label="Cancel"
            color="primary"
            variant="ghost"
            data-testid="date-selection-btn"
            @click="resetDateRange()"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.date-selection {
  border-radius: 5px;
  z-index: 99;
  left: 50%;
  overflow: auto;
  position: absolute;
  transform: translate(-50%, 0);
  background-color: white;
  width: 700px;
}
.date-selection__heading.picker-err {
  color: var(--ui-error);
}
</style>
