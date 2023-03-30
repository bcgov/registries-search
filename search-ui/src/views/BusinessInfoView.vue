<template>
  <v-container id="business-info" class="container" fluid>
    <base-dialog :display="showStaffPayment" :options="staffDialogOptions" @close="showStaffPayment = false">
      <template v-slot:content>
        <staff-payment :staff-payment-data="staffPaymentData" @update:staffPaymentData="fees.staffPaymentData = $event"
          @valid="staffPaymentValid = $event" />
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
      <v-col cols="9">
        <div v-if="warnings.length > 0">
          <span class="section-header">Alerts <span class="warnings-count">({{warnings.length}})</span></span>
          <div class="mt-4">
            <v-expansion-panels class="warnings-list  pt-2 pb-2">
              <v-expansion-panel v-for="(warning, index) in warnings" :key="index" class="expansion-panel">
                <div v-if="warning == 'NOT_IN_GOOD_STANDING'">
                  <v-expansion-panel-title class="expansion-panel__header">
                    <template v-slot:actions="{ expanded }">
                      <span class="expansion-panel-btn-text">View Details</span>
                      <v-icon color="#1669BB" :icon="expanded ? 'mdi-chevron-up' : 'mdi-chevron-down'">
                      </v-icon>
                    </template>
                    <span>
                      <v-icon color="#F8661A">mdi-alert</v-icon>
                    </span>
                    <span class="ml-2">This business is not in good standing</span>
                  </v-expansion-panel-title>
                  <v-expansion-panel-text class="expansion-panel__text">
                    The most common reason a business is not in good standing is an overdue annual report.
                    Any outstanding annual reports must be filed to bring the business back into good standing.
                    <div class="expansion-panel-txt">
                      If further action is required, please contact BC Registries staff:
                      <ContactInfo class="mt-10px" :contacts="RegistriesInfo" />
                    </div>
                  </v-expansion-panel-text>
                </div>
              </v-expansion-panel>
            </v-expansion-panels>
          </div>
          <v-divider class="my-10" />
        </div>
        <span ref="howToAccess" class="section-header">How to Access Business Documents</span>
        <p class="pt-3">
          1. Determine if the filing documents that you want are available for
          download or are on paper only.*
        </p>
        <p class="pt-1">2. Select from Available Documents to Download.</p>
        <p class="pt-1">3. Pay the appropriate fee.</p>
        <p class="pt-1">4. Download the individual files you require.</p>
        <p class="pt-3">
          <span class="more-info">
            <span>*</span>
            <span class="ml-1">To access paper-only documents, you will need to search through
              <a color="primary" class="link" href="https://bconline.gov.bc.ca/" target="_blank">
                <span>BC OnLine</span>
              </a>
              <v-icon dense color="primary" class="small-icon ml-1">mdi-open-in-new</v-icon>,
              or contact BC Registries staff to
              <a color="primary" class="link" :href="docSearchURL" target="_blank">
                <span>submit a document search request</span>
              </a>
              <v-icon dense color="primary" class="small-icon ml-1">mdi-open-in-new</v-icon>
              .
            </span>
          </span>
        </p>
        <v-divider class="my-10" />
        <span class="section-header">Available Documents to Download:</span>
        <div
          :class="['document-list', 'mt-3', 'py-8', searchValidInput ? '': 'document-list-error']"
          :key="checkBoxesKey"
        >
          <v-row v-if="!pageLoaded" class="my-3" justify="center" no-gutters>
            <v-col cols="auto">
              <v-progress-circular color="primary" size="50" indeterminate />
            </v-col>
          </v-row>
          <div v-else class="pl-3 pr-5">
            <div v-for="item, i in purchasableDocs" :key="`${item.label}-${i}`" no-gutters class="document-row">
              <div class="document-list__label">
                <div>
                  <v-tooltip
                    v-if="item.tooltip"
                    content-class="bottom-arrow"
                    location="top left"
                    transition="fade-transition"
                  >
                    <template v-slot:activator="{ props }">
                      <v-row v-bind="props" no-gutters>
                        <v-col v-bind="props" cols="auto">
                          <v-checkbox
                            density="compact"
                            :disabled="!item.active"
                            hide-details
                            @change="toggleFee($event, item)"
                          />
                        </v-col>
                        <v-col v-bind="props">
                          <span v-bind="props" :class="item.active ? 'active-text' : 'disabled-text'">
                            {{ item.label }}</span><span>{{item.description}}</span>
                        </v-col>
                      </v-row>
                    </template>
                    <span>{{ item.tooltip }}</span>
                  </v-tooltip>
                  <v-row v-else no-gutters>
                    <v-col cols="auto">
                      <v-checkbox
                        density="compact"
                        :disabled="!item.active"
                        hide-details
                        @change="toggleFee($event, item)"
                      />
                    </v-col>
                    <v-col>
                      <span v-bind="props" :class="item.active ? 'active-text' : 'disabled-text'">
                        {{ item.label }}</span> <span>{{item.description}}</span>
                    </v-col>
                  </v-row>
                </div>
              </div>
              <div class="document-list__fee">
                <v-label :class="[item.active ? 'active-text' : 'disabled-text']" align-self="end"
                  cols="auto" v-html="item.fee" />
              </div>
            </div>
          </div>
        </div>
        <v-divider class="my-10" />
        <div>
          <filing-history isLocked />
        </div>
      </v-col>
      <v-col cols="3">
        <base-fee-calculator
          :pre-select-item="feePreSelectItem"
          :fee-actions="feeActions"
          :error-message="!searchValidInput ? validationMsg : ''"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref, Ref, computed } from 'vue'
import { useRouter } from 'vue-router'
// bcregistry
import { StaffPaymentIF } from '@bcrs-shared-components/interfaces'
// local
import { StaffPayment } from '@/bcrs-common-components'
import { BaseFeeCalculator, BaseDialog, ContactInfo } from '@/components'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import FilingHistory from '@/components/FilingHistory/FilingHistory.vue'
import { useAuth, useEntity, useFeeCalculator, useFilingHistory, useDocumentAccessRequest } from '@/composables'
import { ActionComps, FeeCodes, FeeEntities, RouteNames, DocumentType } from '@/enums'
import { FeeAction, FeeI, FeeDataI, DialogOptionsI } from '@/interfaces'
import { RegistriesInfo } from '@/resources/contact-info'

const props = defineProps({
  appReady: { default: false },
  identifier: { type: String }  // passed with param value in route.push
})

const howToAccess = ref(null)

const loading = ref(false)
const pageLoaded = ref(false)
const router = useRouter()
const validationMsg = ref('')

const { isStaff, isStaffSBC } = useAuth()
const { entity, clearEntity, loadEntity, isFirm, isCoop, isBC, isActive, isBComp, warnings } = useEntity()
const { filingHistory, loadFilingHistory, clearFilingHistory } = useFilingHistory()
const { fees, addFeeItem, clearFees, getFeeInfo, displayFee, removeFeeItem } = useFeeCalculator()
const { documentAccessRequest, createAccessRequest, loadAccessRequestHistory } = useDocumentAccessRequest()

const docSearchURL = "https://www2.gov.bc.ca/gov/content/employment-business/business/" +
  "managing-a-business/permits-licences/businesses-incorporated-companies/searches-certificates"

// fee summary
const feePreSelectItem: Ref<FeeI> = ref({
  code: null,
  fee: 0,
  label: 'Select From Available Documents',
  quantity: 0,
  serviceFee: 0
})

// staff payment
const showStaffPayment = ref(false)
const staffPaymentData = { ...fees.staffPaymentData }
const staffPaymentHandler = () => {
  if (staffPaymentValid.value) {
    // entry is valid, submit payment
    showStaffPayment.value = false
    payForDocuments()
  }
}
const staffPaymentValid = ref(false)

const staffDialogOptions: DialogOptionsI = {
  buttons: [
    { onClickClose: true, outlined: true, text: 'Cancel' },
    { onClick: staffPaymentHandler, onClickClose: false, outlined: false, text: 'Continue to Payment' }
  ],
  text: '',
  title: 'Staff Payment'
}

// fee selections
const bsrchCode = ref(FeeCodes.BSRCH)  // updates to different code for staff
const checkBoxesKey = ref(0)
const purchasableDocs = ref([]) as Ref<{
  code: FeeCodes,
  fee: string,
  label: string,
  documentType: DocumentType,
  active: boolean,
  tooltip: string,
  description: string
}[]>
const selectedDocs = ref([]) as Ref<DocumentType[]>
const hasNoSelectedDocs = computed(() => { return selectedDocs.value.length === 0 })
const searchValidInput = ref(true)

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
  searchValidInput.value = true
  validationMsg.value = ''
  if (hasNoSelectedDocs.value) {
    searchValidInput.value = false
    validationMsg.value = "Select documents to download"
    howToAccess.value?.scrollIntoView({ behavior: 'smooth'})
  } else {
    if (isStaff.value) showStaffPayment.value = true
    else payForDocuments()
  }
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

// load entity data / filing history, set fee data / selections
onMounted(async () => {
  pageLoaded.value = false
  clearFees()
  loadFilingHistory(props.identifier, null)
  if (entity.identifier !== props.identifier) clearEntity()
  await loadEntity(props.identifier)
  // NB: some logic depends on entity info + auth info
  // check every second for up to 11s (1 more second than app.vue waits for auth)
  for (let i = 0; i < 11; i++) {
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
  const feeData = await getDocFees([bsrchCode.value, FeeCodes.CGOOD, FeeCodes.CSTAT, FeeCodes.LSEAL])
  if (!isStaff.value && !isStaffSBC.value) {
    // set fee preselect serviceFee based on service fee of first item in fees
    feePreSelectItem.value.serviceFee = feeData[0].serviceFee
  }
  purchasableDocs.value.push({
    code: bsrchCode.value,
    fee: displayFee(feeData[0].fee, false, true),
    label: 'Business Summary and Filing History Documents',
    documentType: DocumentType.BUSINESS_SUMMARY_FILING_HISTORY,
    active: true,
    tooltip: '',
    description: '(paper-only copies are not included)'
  })

  if (isCogsAvailable()) {
    purchasableDocs.value.push({
      code: FeeCodes.CGOOD,
      fee: displayFee(feeData[1].fee, false, true),
      label: 'Certificate of Good Standing',
      documentType: DocumentType.CERTIFICATE_OF_GOOD_STANDING,
      active: entity.goodStanding,
      tooltip: !entity.goodStanding ? 'The Certificate of Good Standing ' +
        'is only available if the business is in Good Standing.' : '',
      description: ''
    })
  }

  if (isCstatAvailable()) {
    purchasableDocs.value.push({
      code: FeeCodes.CSTAT,
      fee: displayFee(feeData[2].fee, false, true),
      label: 'Certificate of Status',
      documentType: DocumentType.CERTIFICATE_OF_STATUS,
      active: true,
      tooltip: '',
      description: ''
    })
  }
  // letter under seal is always available
  purchasableDocs.value.push({
    code: FeeCodes.LSEAL,
    fee: displayFee(feeData[3].fee, false, true),
    label: 'Letter Under Seal',
    documentType: DocumentType.LETTER_UNDER_SEAL,
    active: true,
    tooltip: '',
    description: ''
  })
}

const isCogsAvailable = () => {
  return !isFirm.value && isActive.value
}

const isCstatAvailable = () => {
  return (isBC.value || isCoop.value || isBComp.value) && isActive.value
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
  if (selectedDocs.value.length > 0) {
    searchValidInput.value = true
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.document-list {
  background-color: white;
  border-radius: 5px;
  width: 100%;

  &__label,
  &__fee {
    color: $gray8;      
  }

  &__label {     
    width: 85%;
  }

  &__fee {       
    text-align: right;
    width: 15%;
    margin-right: 5px;
  }
}

.document-list-error {  
  border-left: solid 4px #D3272C;
  border-top-right-radius: 5px;
  border-bottom-right-radius: 5px;
  border-bottom-left-radius: 0px;
  border-top-left-radius: 0px;
}


.v-divider {
  border-width: 1.25px !important;
}

:deep(.v-selection-control__input)::before {
  display: none;
}

:deep(.mdi-checkbox-marked) {
  color: $primary-blue
}

:deep(.mdi-checkbox-blank-outline) {
  color: $primary-blue;
  --v-medium-emphasis-opacity: 1;
}

:deep(.v-checkbox .v-selection-control) {
  height: 12px;
}

:deep(.v-checkbox.v-input--density-compact),
:deep(.v-checkbox.v-input--density-compact .v-input__control .v-checkbox-btn) {
  height: 24px;
  --v-input-control-height: 24px;
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
  color: #757575;
  font-weight: normal;
  opacity: 100%;
}

.more-info {
  display: flex;
}

.active-text {
  font-weight: 700;
}

.small-icon {
  font-size: 18px;
}

.warnings-list {
  background: white;
  border-radius: 5px;
}

:deep(.v-expansion-panel__shadow) {
  box-shadow: none !important
}

.expansion-panel {
  &__header {
    font-size: 14px;
    font-weight: bold;
    color: $gray9
  }

  &__text {
    font-size: 14px;
    color: $gray7;
    margin-top: -0.875rem
  }
}

:deep(.v-expansion-panel-title__overlay) {
  background-color: white;
}

.expansion-panel-btn-text {
  color: $primary-blue;
  padding-top: 3.5px;
  font-weight: normal;
  font-size: 13px;
}

.document-row {
  display: flex;
  width: 100%;
}
.document-row:not(:first-child) {
  padding-top: 10px
}

.warnings-count {
  color: #868e96
}
</style>
