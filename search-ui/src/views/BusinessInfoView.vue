<template>
  <v-container id="business-info" class="container" fluid>
    <v-fade-transition>
      <div class="loading-container" v-if="loading">
        <div class="loading__content">
          <v-progress-circular color="primary" size="50" indeterminate />
          <div class="loading-msg" v-if="loading">Completing Payment</div>
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
          <v-row v-for="item, i in purchasableDocs" :key="`${item.label}-${i}`" no-gutters>
            <v-col>
              <v-tooltip v-if="item.tooltip" content-class="tooltip" location="top"></v-tooltip>
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
import { BaseFeeCalculator } from '@/components'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import FilingHistory from '@/components/FilingHistory/FilingHistory.vue'
import { useEntity, useFeeCalculator, useFilingHistory, useDocumentAccessRequest } from '@/composables'
import { ActionComps, FeeCodes, RouteNames, DocumentType } from '@/enums'
import { FeeAction, FeeI } from '@/interfaces'

const props = defineProps({
  identifier: { type: String }  // passed with param value in route.push
})

const loading = ref(false)
const router = useRouter()


const { entity, clearEntity, loadEntity, isFirm } = useEntity()
const { filingHistory, loadFilingHistory, clearFilingHistory } = useFilingHistory()
const { fees, addFeeItem, clearFees, getFeeInfo, displayFee, removeFeeItem } = useFeeCalculator()
const { documentAccessRequest, createAccessRequest } = useDocumentAccessRequest()

// fee summary
const feePreSelectItem: FeeI = {
  code: FeeCodes.SRCH_BASE_DOCS,
  fee: 0,
  label: 'Select From Available Documents',
  quantity: 0,
  serviceFee: 1.5
}

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
  await createAccessRequest(selectedDocs)
  if (!documentAccessRequest._error) {
    selectedDocs.value = []
    clearFees()
    // refresh checkboxes
    checkBoxesKey.value += 1

    clearFilingHistory()
    await loadEntity(entity.identifier)
    await loadFilingHistory(entity.identifier, documentAccessRequest.currentRequest.submissionDate)
    router.push({ name: RouteNames.DOCUMENT_REQUEST })
  }
  loading.value = false
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
    action: payForDocuments,
    compType: ActionComps.BUTTON,
    iconRight: 'mdi-chevron-right',
    outlined: false,
    disabled: reactive(hasNoSelectedDocs),
    text: 'Pay and Unlock Documents'
  }],
]

// checkbox
const getDocFee = async (code: FeeCodes) => {
  const feeInfo = await getFeeInfo(code)
  if (feeInfo) return displayFee(feeInfo.fee, true)
  return 'Not Available'
}


// load entity data, clear any previous fees
onMounted(async () => {
  if (entity.identifier !== props.identifier) clearEntity()
  await loadEntity(props.identifier)
  await loadPurchasableDocs()
  await loadFilingHistory(props.identifier, null)
  clearFees()
})

const loadPurchasableDocs = async () => {
  const feeBaseDocs = await getDocFee(FeeCodes.SRCH_BASE_DOCS)
  const feeCOGS = await getDocFee(FeeCodes.COGS)

  purchasableDocs.value.push({
    code: FeeCodes.SRCH_BASE_DOCS,
    fee: feeBaseDocs,
    label: 'Business Summary and Filing History Documents (paper-only copies are not included)',
    documentType: DocumentType.BUSINESS_SUMMARY_FILING_HISTORY,
    active: true,
    tooltip: ''
  })

  if (isCogsAvailable()) {
    purchasableDocs.value.push({
      code: FeeCodes.COGS,
      fee: feeCOGS,
      label: 'Certificate of Good Standing',
      documentType: DocumentType.CERTIFICATE_OF_GOOD_STANDING,
      active: entity.goodStanding,
      tooltip: !entity.goodStanding ? 'The Certificate of Good Standing ' +
        'can only be ordered if the business is in Good Standing.' : ''
    })
  }
}

const isCogsAvailable = () => {
  return !isFirm.value
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

.disabled-text {
  color: $gray7;
}
</style>
