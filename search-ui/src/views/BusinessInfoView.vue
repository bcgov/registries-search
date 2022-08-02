<template>
  <v-container id="business-info" class="container" fluid>
    <base-dialog :display="showStaffPayment" :options="staffDialogOptions" @proceed="staffPaymentHandler($event)">
      <template v-slot:content>
        <staff-payment
          :staff-payment-data="staffPaymentData"
          @update:staffPaymentData="fees.staffPaymentData = $event"
          @valid="staffPaymentValid = $event"
        />
      </template>
    </base-dialog>
    <v-fade-transition>
      <div class="loading-container" v-if="loading">
        <div class="loading__content">
          <v-progress-circular color="primary" size="50" indeterminate />
          <div class="loading-msg">Completing Payment</div>
        </div>
      </div>
    </v-fade-transition>
    <v-fade-transition>
      <div class="loading-container  grayed-out" v-if="documentAccessRequest._downloading">
        <div class="loading__content">
          <v-progress-circular color="primary" size="50" indeterminate />
          <div class="loading-msg" v-if="documentAccessRequest._downloading">Downloading document</div>
        </div>
      </div>
    </v-fade-transition>
    <v-row no-gutters>
      <v-col>
        <h2>How to Access Business Documents</h2>
        <p class="pt-3">
          1. Determine if the filing documents that you want are available for
          download or are on paper only.*
        </p>
        <p class="pt-1">2. Select from Available Documents to Download.</p>
        <p class="pt-1">3. Pay the appropriate fee.</p>
        <p class="pt-1">4. Download the individual files you require.</p>
        <p class="pt-3">
          * Some documents are available on paper only and not available to download.
          To request copies of paper documents, contact BC Registries staff.
        </p>
        <v-divider class="my-10" />
        <h2>Available Documents to Download:</h2>
        <div class="document-list  mt-3 pa-3 pr-5 pt-7" :key="checkBoxesKey">
          <v-row v-if="!pageLoaded" class="my-3" justify="center" no-gutters>
            <v-col cols="auto">
              <v-progress-circular color="primary" size="50" indeterminate />
            </v-col>
          </v-row>
          <div v-else>
            <v-row v-for="item, i in purchasableDocs" :key="`${item.label}-${i}`" no-gutters>
              <v-col>
                <v-row no-gutters>
                  <v-col cols="auto" style="position: relative;">
                    <v-tooltip v-if="item.tooltip" content-class="tooltip" location="top">
                      <template v-slot:activator="{ isActive, props }">
                        <div v-if="isActive" class="top-tooltip-arrow document-list__tooltip-arrow" />
                        <v-row v-bind="props" no-gutters>
                          <v-col v-bind="props" cols="auto">
                            <v-checkbox :disabled="!item.active" hide-details @change="toggleFee($event, item)" />
                          </v-col>
                          <v-col v-bind="props" class="document-list__label">
                            <span v-bind="props" :class="item.active ? '' : 'disabled-text'">{{ item.label }}</span>
                          </v-col>
                        </v-row>
                      </template>
                      <span>{{ item.tooltip }}</span>
                    </v-tooltip>
                    <v-row v-else no-gutters>
                      <v-col cols="auto">
                        <v-checkbox :disabled="!item.active" hide-details @change="toggleFee($event, item)" />
                      </v-col>
                      <v-col class="document-list__label">
                        <span v-bind="props" :class="item.active ? '' : 'disabled-text'">{{ item.label }}</span>
                      </v-col>
                    </v-row>
                  </v-col>
                  <v-col />
                </v-row>
              </v-col>
              <v-col :class="['document-list__fee', item.active ? '' : 'disabled-text']" align-self="end" cols="auto"
                v-html="item.fee" />
            </v-row>
          </div>
        </div>
        <v-divider class="my-10" />
        <div>
          <filing-history isLocked />
        </div>
      </v-col>
      <v-col cols="12" sm="auto">
        <base-fee-calculator :pre-select-item="feePreSelectItem" :fee-actions="feeActions" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref, Ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
// local
import { StaffPayment } from '@/bcrs-common-components'
import { BaseFeeCalculator, BaseDialog } from '@/components'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import FilingHistory from '@/components/FilingHistory/FilingHistory.vue'
import { useAuth, useEntity, useFeeCalculator, useFilingHistory, useDocumentAccessRequest } from '@/composables'
import { ActionComps, FeeCodes, FeeEntities, RouteNames, DocumentType } from '@/enums'
import { FeeAction, FeeI, FeeDataI, DialogOptionsIF } from '@/interfaces'
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'

const props = defineProps({
  appReady: { default: false },
  identifier: { type: String }  // passed with param value in route.push
})

const loading = ref(false)
const pageLoaded = ref(false)
const router = useRouter()

const { isStaff, isStaffSBC } = useAuth()
const { entity, clearEntity, loadEntity, isFirm, isCoop, isBC, isActive } = useEntity()
const { filingHistory, loadFilingHistory, clearFilingHistory } = useFilingHistory()
const { fees, addFeeItem, clearFees, getFeeInfo, displayFee, removeFeeItem } = useFeeCalculator()
const { documentAccessRequest, createAccessRequest, loadAccessRequestHistory } = useDocumentAccessRequest()

// fee summary
const feePreSelectItem: Ref<FeeI> = ref({
  code: null,
  fee: 0,
  label: 'Select From Available Documents',
  quantity: 0,
  serviceFee: 1.5
})

// staff payment
const showStaffPayment = ref(false)
const staffDialogOptions: DialogOptionsIF = {
  acceptText: 'Continue to Payment',
  cancelText: 'Cancel',
  text: '',
  title: 'Staff Payment'
}
const staffPaymentData = { ...fees.staffPaymentData }
const staffPaymentHandler = (proceed: boolean) => {
  if (!proceed) showStaffPayment.value = false
  else if (staffPaymentValid.value) {
    // entry is valid, submit payment
    showStaffPayment.value = false
    payForDocuments()
  }
}
const staffPaymentValid = ref(false)

// fee selections
const bsrchCode = ref(FeeCodes.BSRCH)  // updates to different code for staff
const checkBoxesKey = ref(0)
const purchasableDocs = ref([]) as Ref<{
  code: FeeCodes,
  fee: string,
  label: string,
  documentType: DocumentType,
  active: boolean,
  tooltip: string
}[]>
const selectedDocs = ref([]) as Ref<DocumentType[]>
const hasNoSelectedDocs = computed(() => { return selectedDocs.value.length === 0 })

const payForDocuments = async () => {
  loading.value = true
  let header = { folioNumber: fees.folioNumber } as StaffPaymentIF
  if (isStaff.value) header = fees.staffPaymentData
  await createAccessRequest(selectedDocs.value, entity, header)
  if (!documentAccessRequest._error) {
    selectedDocs.value = []
    clearFees()
    // refresh checkboxes
    checkBoxesKey.value += 1

    clearFilingHistory()
    await loadEntity(entity.identifier)
    await loadFilingHistory(entity.identifier, documentAccessRequest.currentRequest.submissionDate)
    await loadAccessRequestHistory()
    router.push({ name: RouteNames.DOCUMENT_REQUEST, params: { identifier: entity.identifier } })
  }
  loading.value = false
}

const submitSelected = () => {
  if (isStaff.value) showStaffPayment.value = true
  else payForDocuments()
}

const feeActions: FeeAction[][] = [
  [{
    action: (val) => { fees.folioNumber = val },
    compType: ActionComps.TEXTFIELD,
    outlined: false,
    text: 'Folio Number (Optional)'
  }],
  [{
    action: () => { router.push({ name: RouteNames.SEARCH }) },
    compType: ActionComps.BUTTON,
    iconLeft: 'mdi-chevron-left',
    outlined: true, text: 'Back to Search Results'
  }],
  [{
    action: submitSelected,
    compType: ActionComps.BUTTON,
    iconRight: 'mdi-chevron-right',
    outlined: false,
    disabled: reactive(hasNoSelectedDocs),
    text: 'Pay and Unlock Documents'
  }],
]

// checkbox
const getDocFees = async (codes: FeeCodes[]) => {
  const feeData: FeeDataI[] = []
  for (const i in codes) {
    feeData.push({
      entityType: FeeEntities.BSRCH,
      filingTypeCode: codes[i]
    })
  }
  return await getFeeInfo(feeData)
}

// load entity data, clear previous fees
onMounted(async () => {
  pageLoaded.value = false
  clearFees()
  loadFilingHistory(props.identifier, null)
  if (entity.identifier !== props.identifier) clearEntity()
  await loadEntity(props.identifier)
  // NB: some logic depends on entity info + auth info
  // check every second for up to 11s (1 more second than app.vue waits for auth)
  for (let i=0; i<11; i++) {
    if (props.appReady) break
    await new Promise(resolve => setTimeout(resolve, 1000))
  }
  if (isStaff.value || isStaffSBC.value) {
    bsrchCode.value = FeeCodes.SBSRCH
    feePreSelectItem.value.serviceFee = 0
  }
  await loadPurchasableDocs()
  pageLoaded.value = true
})

const loadPurchasableDocs = async () => {
  const feeData = await getDocFees([bsrchCode.value, FeeCodes.CGOOD, FeeCodes.CSTAT])

  purchasableDocs.value.push({
    code: bsrchCode.value,
    fee: displayFee(feeData[0].fee, false),
    label: 'Business Summary and Filing History Documents (paper-only copies are not included)',
    documentType: DocumentType.BUSINESS_SUMMARY_FILING_HISTORY,
    active: true,
    tooltip: ''
  })

  if (isCogsAvailable()) {
    purchasableDocs.value.push({
      code: FeeCodes.CGOOD,
      fee: displayFee(feeData[1].fee, false),
      label: 'Certificate of Good Standing',
      documentType: DocumentType.CERTIFICATE_OF_GOOD_STANDING,
      active: entity.goodStanding,
      tooltip: !entity.goodStanding ? 'The Certificate of Good Standing ' +
        'can only be ordered if the business is in Good Standing.' : ''
    })
  }

  if (isCstatAvailable()) {
    purchasableDocs.value.push({
        code: FeeCodes.CSTAT,
        fee: displayFee(feeData[2].fee, false),
        label: 'Certificate of Status',
        documentType: DocumentType.CERTIFICATE_OF_STATUS,
        active: true,
        tooltip: ''
    })
  }
}

const isCogsAvailable = () => {
  return !isFirm.value && isActive.value
}

const isCstatAvailable = () => {
  return (isBC.value || isCoop.value) && isActive.value
}

const toggleFee = (event: any, item: any) => {
  if (!item.active) return
  if (event.target.checked) {
    addFeeItem(item.code, 1)
    selectedDocs.value.push(item.documentType)
  }
  else {
    removeFeeItem(item.code, 1)
    selectedDocs.value = selectedDocs.value.filter(doc => doc != item.documentType)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.document-list {
  background-color: white;
  width: 100%;

  &__label,
  &__fee {
    color: $gray8;
    font-weight: 700;
    height: 56px;
  }

  &__label {
    padding-top: 5px !important;
  }

  &__fee {
    padding-left: 8px !important;
    padding-top: 3px !important;
    text-align: right;
  }

  &__tooltip {
    margin-top: 30px !important;
  }

  &__tooltip-arrow {
    margin-left: 10px;
    margin-top: -9px !important;
  }
}

.v-divider {
  border-width: 1px;
}

:deep(.v-selection-control__input)::before {
  display: none;
}

:deep(.mdi-checkbox-marked) {
  color: $primary-blue
}

:deep(.mdi-checkbox-blank-outline) {
  color: $gray8;
  --v-medium-emphasis-opacity: 1;
}

:deep(.v-checkbox .v-selection-control) {
  height: 32px;
}

:deep(.v-label) {
  color: $gray8;
  font-weight: 700;
  white-space: normal;
  --v-medium-emphasis-opacity: 1;
}

:deep(.v-overlay__content) {
  width: 100%;
}

.disabled-text {
  color: $gray7;
}
</style>
