<template>
  <div id="staff-payment-container">
    <v-row no-gutters>
      <v-col v-if="displaySideLabel" cols="12" sm="3" class="pr-4 pb-4">
        <label class="title-label" :class="{'error-text': invalidSection}">Payment</label>
      </v-col>

      <v-col class="pay-form" cols="12" :sm="displaySideLabel ? 9 : 12">
        <v-radio-group class="payment-group" hide-details v-model="paymentOption">
          <!-- Cash or Cheque radio button and form -->
          <v-radio
            id="fas-radio"
            class="mb-0"
            color="primary"
            label="Cash or Cheque"
            :value="StaffPaymentOptions.FAS"
          />
          <v-form class="mt-4 ml-8" ref="fasForm" v-model="fasFormValid">
            <v-text-field
              filled
              id="routing-slip-number-textfield"
              label="Routing Slip Number"
              v-model="staffPaymentData.routingSlipNumber"
              :rules="validate ? routingSlipNumberRules : []"
              :disabled="paymentOption === StaffPaymentOptions.BCOL || paymentOption === StaffPaymentOptions.NO_FEE"
              @keyup="staffPaymentData.routingSlipNumber = staffPaymentData.routingSlipNumber.trim()"
              @focus="paymentOption = StaffPaymentOptions.FAS"
              @input="emitStaffPaymentData({option: StaffPaymentOptions.FAS, routingSlipNumber: $event.target._value})"
            />
          </v-form>

          <!-- BC OnLine radio button and form -->
          <v-radio
            id="bcol-radio"
            class="mb-0 pt-2"
            color="primary"
            label="BC OnLine"
            :value="StaffPaymentOptions.BCOL"
          />
          <v-form class="mt-4 ml-8" ref="bcolForm" v-model="bcolFormValid">
            <v-text-field
              filled
              id="bcol-account-number-textfield"
              label="BC OnLine Account Number"
              v-model="staffPaymentData.bcolAccountNumber"
              :rules="validate ? bcolAccountNumberRules : []"
              :disabled="paymentOption === StaffPaymentOptions.FAS || paymentOption === StaffPaymentOptions.NO_FEE"
              @keyup="staffPaymentData.bcolAccountNumber = staffPaymentData.bcolAccountNumber.trim()"
              @focus="paymentOption = StaffPaymentOptions.BCOL"
              @input="emitStaffPaymentData({option: StaffPaymentOptions.BCOL, bcolAccountNumber: $event.target.value})"
            />
            <v-text-field
              filled
              id="dat-number-textfield"
              label="DAT Number"
              v-model="staffPaymentData.datNumber"
              :rules="validate ? datNumberRules : []"
              :disabled="paymentOption === StaffPaymentOptions.FAS || paymentOption === StaffPaymentOptions.NO_FEE"
              @keyup="staffPaymentData.datNumber = staffPaymentData.datNumber.trim()"
              @focus="paymentOption = StaffPaymentOptions.BCOL"
              @input="emitStaffPaymentData({ option: StaffPaymentOptions.BCOL, datNumber: $event.target._value })"
            />
            <FolioNumberInput
              ref="folioNumberInputRef"
              :disabled="paymentOption === StaffPaymentOptions.FAS || paymentOption === StaffPaymentOptions.NO_FEE"
              :validate="validate"
              @focus="paymentOption = StaffPaymentOptions.BCOL"
              @emitFolioNumber="staffPaymentData.folioNumber = $event;
                emitStaffPaymentData({ option: StaffPaymentOptions.BCOL, folioNumber: $event })"
            />
          </v-form>

          <!-- No Fee radio button -->
          <v-radio
            id="no-fee-radio"
            class="mb-0 pt-2"
            color="primary"
            label="No Fee"
            :value="StaffPaymentOptions.NO_FEE"
          />
        </v-radio-group>
        <template v-if="displayPriorityCheckbox">
          <v-divider class="mt-6"></v-divider>

          <!-- Priority checkbox -->
          <v-checkbox
            id="priority-checkbox"
            class="priority-checkbox mt-4 pt-0"
            label="Priority (add $100.00)"
            hide-details
            v-model="staffPaymentData.isPriority"
            :disabled="paymentOption === StaffPaymentOptions.NO_FEE"
            @change="emitStaffPaymentData({ option: paymentOption, isPriority: $event.target.checked })"
          />
        </template>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch, Ref } from 'vue'
import { FormIF } from '@bcrs-shared-components/interfaces'
import { StaffPaymentIF } from '../interfaces'
import { StaffPaymentOptions } from '../enums'
// local
import { FolioNumberInput } from '.'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  displayPriorityCheckbox: { default: false },
  displaySideLabel: { default: false },
  invalidSection: { default: false },
  staffPaymentData: {
    default: () => {
      return {
        option: StaffPaymentOptions.NONE,
        routingSlipNumber: null,
        bcolAccountNumber: null,
        datNumber: null,
        folioNumber: null,
        isPriority: false
      }
    }
  },
  validate: { default: true },
})

const emit = defineEmits<{
  (e: 'valid', value: boolean): void
  (e: 'update:staffPaymentData', value: StaffPaymentIF): void
}>()

const bcolForm: Ref<FormIF> = ref(null)
const fasForm: Ref<FormIF> = ref(null)
const folioNumberInputRef: Ref<typeof FolioNumberInput> = ref(null)

/** Radio group model property. */
const paymentOption = ref(StaffPaymentOptions.NONE)

const staffPaymentData: StaffPaymentIF = reactive({
  option: paymentOption.value,
  routingSlipNumber: '',
  bcolAccountNumber: '',
  datNumber: '',
  folioNumber: '',
  isPriority: false
})

const fasFormValid = ref(false)
const bcolFormValid = ref(false)

const isMounted = ref(false)

/** Indicates whether or not this component is valid. */
const isCompValid = computed((): boolean => (fasFormValid.value ||
  (bcolFormValid.value && folioNumberInputRef.value.validateFolioNumber()) ||
  (staffPaymentData.option === StaffPaymentOptions.NO_FEE)))

/** Validation rules. */
const routingSlipNumberRules: Array<(v: string) => string | true> = [
  v => !!v || 'Enter FAS Routing Slip Number',
  v => /^\d{9}$/.test(v) || 'Routing Slip Number must be 9 digits'
]
const bcolAccountNumberRules: Array<(v: string) => string | true> = [
  v => !!v || 'Enter BC OnLine Account Number',
  v => /^\d{6}$/.test(v) || 'BC OnLine Account Number must be 6 digits'
]
const datNumberRules: Array<(v: string) => string | true> = [
  v => !!v || 'Enter DAT Number',
  v => /^[A-Z]{1}[0-9]{7,9}$/.test(v) || 'DAT Number must be in standard format (eg, C1234567)'
]

onMounted(async () => {
  await nextTick()
  isMounted.value = true
})

const emitStaffPaymentData = ({
  option = staffPaymentData.option,
  routingSlipNumber = staffPaymentData.routingSlipNumber || '',
  bcolAccountNumber = staffPaymentData.bcolAccountNumber || '',
  datNumber = staffPaymentData.datNumber || '',
  folioNumber = staffPaymentData.folioNumber || '',
  isPriority = staffPaymentData.isPriority || false
}) => {
  // return only the appropriate fields for each option
  switch (option) {
    case StaffPaymentOptions.FAS:
      emit('update:staffPaymentData', { option, routingSlipNumber, isPriority } as StaffPaymentIF)
      break
    case StaffPaymentOptions.BCOL:
      emit('update:staffPaymentData',
        { option, bcolAccountNumber, datNumber, folioNumber, isPriority } as StaffPaymentIF)
      break
    case StaffPaymentOptions.NO_FEE:
      emit('update:staffPaymentData', { option } as StaffPaymentIF)
      break
  }
}

/** Called when payment option (radio group item) has changed. */
watch(() => paymentOption.value, (val: StaffPaymentOptions) => {
  staffPaymentData.option = val
  switch (val) {
    case StaffPaymentOptions.FAS:
      // reset other form
      bcolForm.value.resetValidation()
      folioNumberInputRef.value.resetFolioNumberValidation()
      // enable validation for this form
      fasForm.value.validate()
      // update data
      emitStaffPaymentData({ option: StaffPaymentOptions.FAS })
      break

    case StaffPaymentOptions.BCOL:
      // reset other form
      fasForm.value.resetValidation()
      // enable validation for this form
      bcolForm.value.validate()
      // update data
      emitStaffPaymentData({ option: StaffPaymentOptions.BCOL })
      break

    case StaffPaymentOptions.NO_FEE:
      // reset other forms
      fasForm.value.resetValidation()
      bcolForm.value.resetValidation()
      folioNumberInputRef.value.resetFolioNumberValidation()
      // update data
      emitStaffPaymentData({ option: StaffPaymentOptions.NO_FEE })
      break
  }
})

/** Watches for change to FAS form validity. */
watch(() => fasFormValid.value, () => {
  // ignore initial condition
  if (!isMounted.value) return
  emit('valid', isCompValid.value)
})

/** Watches for change to BCOL form validity. */
watch(() => bcolFormValid.value, () => {
  // ignore initial condition
  if (!isMounted.value) return
  emit('valid', isCompValid.value)
})

/** Watches for changes to Staff Payment Data prop. */
watch(() => staffPaymentData.option, async (val) => {
  paymentOption.value = val
  await nextTick()
  emit('valid', isCompValid.value)
})
watch([
  () => staffPaymentData.bcolAccountNumber,
  () => staffPaymentData.datNumber,
  () => staffPaymentData.folioNumber,
  () => staffPaymentData.routingSlipNumber,
  () => staffPaymentData.isPriority
], async () => {
  await nextTick()
  emit('valid', isCompValid.value)
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#staff-payment-container {
  line-height: 1.2rem;
  font-size: $px-16;
}

.title-label {
  font-weight: bold;
  color: $gray9;
}

.payment-container {
  > label:first-child {
    font-weight: 700;
    margin-bottom: 2rem;
  }
}

.pay-form {
  color: $gray7;
  font-weight: normal;
  .payment-group {
    margin-top: -9px;
    padding-top: 0;

    :deep(.v-field-label) {
      opacity: .7;
      font-weight: normal;
    }
  }

  :deep(.v-label) {
    color: $gray7;
    font-weight: normal;
  }

  :deep(.v-input__control) {
    margin-bottom: -12px;
  }

  :deep(.v-input__details) {
    margin-top: 10px;
    margin-bottom: 8px;
  }

  :deep(.mdi-checkbox-blank-outline),
  :deep(.mdi-radiobox-blank) {
    color: $gray7;
    opacity: 1;
  }
}
</style>
