<!-- FUTURE: will be replaced by common component #30551 -->
<script setup lang="ts">
import VueDatePicker from '@vuepic/vue-datepicker'

// props / emits
const props = defineProps<{
  defaultSelectedDate?: Date
  error?: boolean
  setMaxDate?: Date | null
  setMinDate?: Date | null
  resetTrigger?: boolean
}>()
const emit = defineEmits<{ (e: 'selectedDate', value: Date | null): void }>()

// date selection
const selectedDate: Ref<Date | null> = ref(props.defaultSelectedDate || null)
watch(() => selectedDate.value, val => emit('selectedDate', val))

watch(() => props.resetTrigger, () => {
  selectedDate.value = props.defaultSelectedDate || null
})

// max/min
const maxDate: Ref<Date | null> = ref(props.setMaxDate || null)
watch(() => props.setMaxDate, (val) => {
  maxDate.value = val || null
})

const minDate: Ref<Date | null> = ref(props.setMinDate || null)
watch(() => props.setMinDate, (val) => {
  minDate.value = val || null
})
</script>

<template>
  <div class="bcros-date-picker rounded-md" :class="{ 'bcros-date-picker__err': error }">
    <VueDatePicker
      v-model="selectedDate"
      auto-apply
      :action-row="{ showCancel: false, showNow: false, showPreview: false, showSelect: false }"
      calendar-cell-class-name="bcros-date-picker__calendar__day"
      calendar-class-name="bcros-date-picker__calendar"
      :day-names="['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']"
      :enable-time-picker="false"
      format="yyyy-MM-dd"
      hide-offset-dates
      inline
      :max-date="maxDate || ''"
      :min-date="minDate || ''"
      :month-change-on-scroll="false"
      :week-start="0"
      data-testid="date-picker"
    />
  </div>
</template>

<style lang="css">
@import '@vuepic/vue-datepicker/dist/main.css';

.bcros-date-picker {
  width: 300px;
}

.bcros-date-picker__err {
  border: 1px solid var(--ui-error);
  border-radius: 10px;
  box-shadow: 0px 0px 3px var(--ui-error);
}

.dp__calendar_item .dp__cell_inner {
  border-radius: 50%;
}

.dp__calendar_header {
  margin-top: 6px;

  .dp__calendar_header_item {
    font-size: 12px;
    font-weight: 500;
    color: var(--ui-neutral-highlighted) !important;
    padding: 4px 0 0 0;
    width: 40px;
  }
}

.dp__menu {
  border-radius: 10px;
  height: 329px;
}

.dp__main {
  width: 298px;
}

.dp__theme_light {
  --dp-background-color: #ffffff;
  --dp-text-color: #495057;
  --dp-hover-color: #E4EDF7;
  --dp-hover-text-color: #495057;
  --dp-hover-icon-color: #495057;
  --dp-primary-color: #1669bb;
  --dp-primary-text-color: #f8f5f5;
  --dp-secondary-color: #c0c4cc;
  --dp-border-color: #ddd;
  --dp-menu-border-color: #ddd;
  --dp-border-color-hover: #aaaeb7;
  --dp-disabled-color: #f6f6f6;
  --dp-scroll-bar-background: #f3f3f3;
  --dp-scroll-bar-color: #959595;
  --dp-success-color: #76d275;
  --dp-success-color-disabled: #a3d9b1;
  --dp-icon-color: #959595;
  --dp-danger-color: #ff6f60;
  --dp-highlight-color: rgba(25, 118, 210, 0.1);
}
</style>
