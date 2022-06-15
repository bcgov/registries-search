<template>
  <v-container  id="business-info" class="container" fluid>    
   <v-fade-transition>
      <div class="loading-container" v-if="documentAccessRequest._saving">
        <div class="loading__content">
          <v-progress-circular color="primary" size="50" indeterminate />
          <div class="loading-msg" v-if="documentAccessRequest._saving">Completing Payment</div>           
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
        <p class="pt-3">1. Select from Available Documents to Download.</p>
        <p class="pt-1">2. Pay the appropriate fee.</p>
        <p class="pt-1">3. Download the individual files you require.</p>
        <p class="pt-3">
          Note: some documents are available on paper only and not available
          to download. To request copies of paper documents, contact BC Registries Staff.
        </p>
        <v-divider class="my-10" />
        <h2>Available Documents to Download:</h2>
        <div class="document-list justify-center mt-3 pa-3 pr-5" :key="checkBoxesKey">
          <v-row v-for="item, i in purchasableDocs" :key="`${item.label}-${i}`" no-gutters>
            <v-col>
              <v-checkbox
                class="document-list__checkbox"
                hide-details
                :label="item.label"
                @change="toggleFee($event, item)"
              />
            </v-col>
            <v-col class="document-list__fee pt-4" align-self="end" cols="auto" v-html="item.fee" />
          </v-row>
        </div>
        <v-divider class="my-10" />
        <div>
          <h4>Purchase History</h4> 
          <document-access-request-history />
        </div>
        <v-divider class="my-10" />
         <div>
          <filing-history />
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
import DocumentAccessRequestHistory from '@/components/BusinessInfo/DocumentAccessRequestHistory.vue'
import { useEntity, useFeeCalculator, useFilingHistory, useDocumentAccessRequest } from '@/composables'
import { ActionComps, FeeCodes, RouteNames, DocumentType } from '@/enums'
import { FeeAction, FeeI } from '@/interfaces'

const props = defineProps({
  identifier: { type: String }  // passed with param value in route.push
})

const router = useRouter()


const { entity, clearEntity, loadEntity } = useEntity()
const { loadFilingHistory, filingHistory } = useFilingHistory()
const { fees, addFeeItem, clearFees, getFeeInfo, displayFee, removeFeeItem } = useFeeCalculator()
const { documentAccessRequest, loadAccessRequestHistory, createAccessRequest } = useDocumentAccessRequest()

// fee summary
const feePreSelectItem: FeeI = {
  code: FeeCodes.SRCH_BASE_DOCS,
  fee: 0,
  label: 'Select From Available Documents',
  quantity: 0,
  serviceFee: 1.5
}

const checkBoxesKey = ref(0)
const purchasableDocs = ref([]) as Ref<{ code: FeeCodes, fee: string, label: string, documentType: DocumentType }[]>
const selectedDocs = ref([])as Ref<DocumentType[]>
const hasNoSelectedDocs = computed(() => { return selectedDocs.value.length === 0 })

const payForDocuments = async () => {  
  await createAccessRequest(entity.identifier, selectedDocs)   
  if (!documentAccessRequest._error) {     
    loadAccessRequestHistory(props.identifier)
    clearFees()
    // refresh checkboxes
    checkBoxesKey.value += 1
  }   
}

const feeActions: FeeAction[][] = [
  [{
    action: (val) => { fees.folioNumber = val },
    compType: ActionComps.TEXTFIELD,
    outlined: false,    
    text: 'Folio Number (Optional)' }],
  [{
    action: () => { router.push({ name: RouteNames.SEARCH }) },
    compType: ActionComps.BUTTON,
    iconLeft: 'mdi-chevron-left',    
    outlined: true, text: 'Back to Search Results' }],
  [{
    action: payForDocuments,
    compType: ActionComps.BUTTON,
    iconRight: 'mdi-chevron-right',
    outlined: false,     
    disabled: reactive(hasNoSelectedDocs),
    text: 'Pay and Unlock Documents' }],
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
  loadEntity(props.identifier)
  loadFilingHistory(props.identifier)
  loadAccessRequestHistory(props.identifier)
  clearFees()
  const feeBaseDocs = await getDocFee(FeeCodes.SRCH_BASE_DOCS)
  purchasableDocs.value.push({
    code: FeeCodes.SRCH_BASE_DOCS,
    fee: feeBaseDocs,
    label: 'Business Summary and Filing History Documents',
    documentType: DocumentType.BUSINESS_SUMMARY_FILING_HISTORY
  })
})

const toggleFee = (event: any, item: any) => {
  if (event.target.checked) {
    addFeeItem(item.code, 1)
    selectedDocs.value.push(item.documentType)
  }
  else 
  {
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
  &__checkbox, &__checkbox::before {
    background-color: white !important;
    display: flex;
    box-shadow: none;
  }
  &__fee {
    color: $gray8;
    font-weight: 700;
    height: 56px;
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
:deep(.v-label) {
  color: $gray8;
  font-weight: 700;
  --v-medium-emphasis-opacity: 1;
}
</style>
