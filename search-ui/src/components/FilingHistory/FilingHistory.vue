<template>
  <div id="filing-history-list">
    <span data-test-id="dashboard-filing-history-subtitle" class="section-header">
      <span v-if="props.isLocked">
        Filing History
        <span v-if="historyItems.length" style="color:#868e96">({{historyItems.length}})</span>
      </span>
      <span v-else>Filing History Documents</span>
      <span class="ml-1" v-if="filingHistory._loading">
        <v-progress-circular color="primary" indeterminate size="22" />
      </span>
    </span>
    <div class="mt-5 pa-5 court-order-section" v-if="hasCourtOrderFilings">
      <v-icon class="ml-1">mdi-gavel</v-icon>
      <span class="ml-2">Court order(s) have been filed on this company. Review the 
        filing history for impacts to business information.</span>
    </div>
    <div class="scrollable-container soft-corners mt-4">
      <div v-if="filingHistory._loading" class="mx-auto my-15" style="width: 50px;">
        <v-progress-circular color="primary" size="50" indeterminate />
      </div>
      <error-retry
        v-else-if="filingHistory._error"
        class="error-retry-filings font-14 mx-auto my-8"
        :action="loadFilingHistory"
        :actionArgs="[filingHistory._identifier, filingHistory._effective_date]"
        :message="historyErrorMsg"
      />
      <v-expansion-panels v-else-if="historyItems.length > 0" v-model="panel">
        <v-expansion-panel class="align-items-top filing-history-item px-6 py-5" v-for="(filing, index) in historyItems"
          :key="index">
          <v-expansion-panel-title class="no-dropdown-icon pa-0">
            <div class="item-header d-flex">
              <!-- the filing label (left side) -->
              <div class="item-header__label">
                <h3 class="item-header__title">
                  <v-icon v-if="filing.displayName === 'Court Order'" class="mr-1 mt-n1">mdi-gavel</v-icon>
                  {{ filing.displayName }}
                </h3>

                <!-- NB: blocks below are mutually exclusive, and order is important -->


                <div v-if="filing.isTypeStaff" class="item-header__subtitle">
                  <FiledLabel :filing="filing" />
                </div>


                <div v-else-if="filing.isFutureEffectiveBcompCoaPending" class="item-header__subtitle">
                  <span>FILED AND PENDING
                    <FiledLabel :filing="filing" />
                  </span>
                  <v-tooltip location="top" content-class="bottom-arrow">
                    <template v-slot:activator="{ props }">
                      <div class="pending-alert" v-bind="props">
                        <v-icon color="orange darken-2">mdi-alert</v-icon>
                      </div>
                    </template>
                    <span>
                      The updated office addresses will be legally effective on
                      {{ dateToPacificDateTime(filing.effectiveDate) }}.
                      No other filings are allowed until then.
                    </span>
                  </v-tooltip>
                </div>


                <div
                  v-else-if="filing.isCompletedIa || filing.isCompletedAlteration || filing.isCompletedDissolution"
                  class="item-header__subtitle"
                >
                  <div>FILED AND PAID
                    <FiledLabel :filing="filing" />
                  </div>
                  <v-btn class="details-btn" flat :ripple=false @click.stop="togglePanel(index, filing)">
                    <v-icon left class="app-blue">mdi-information-outline</v-icon>
                    <span class="app-blue">{{ (panel === index) ? "Hide Details" : "View Details" }}</span>
                  </v-btn>
                </div>


                <div
                  v-else-if="filing.isFutureEffectiveAlterationPending || filing.isFutureEffectiveDissolutionPending"
                  class="item-header__subtitle"
                >
                  <span class="orange--text text--darken-2">FILED AND PENDING</span>
                  <span class="vert-pipe" />
                  <span>PAID
                    <FiledLabel :filing="filing" />
                  </span>
                  <v-btn
                    class="details-btn orange--text text--darken-2"
                    :ripple=false
                    @click.stop="togglePanel(index, filing)"
                  >
                    <v-icon left>mdi-alert</v-icon>
                    <span>{{ (panel === index) ? "Hide Details" : "View Details" }}</span>
                  </v-btn>
                </div>


                <div
                  v-else-if="filing.isFutureEffectiveAlteration || filing.isFutureEffectiveDissolution"
                  class="item-header__subtitle"
                >
                  <span v-if="filing.isFutureEffectiveAlteration">FUTURE EFFECTIVE ALTERATION</span>
                  <span v-if="filing.isFutureEffectiveDissolution">FUTURE EFFECTIVE DISSOLUTION</span>
                  <span class="vert-pipe" />
                  <span>PAID
                    <FiledLabel :filing="filing" />
                  </span>
                  <v-btn class="details-btn" flat :ripple=false @click.stop="togglePanel(index, filing)">
                    <v-icon left class="app-blue">mdi-information-outline</v-icon>
                    <span class="app-blue">{{ (panel === index) ? "Hide Details" : "View Details" }}</span>
                  </v-btn>
                </div>


                <div v-else-if="isStatusPaid(filing)" class="item-header__subtitle">
                  <span class="orange--text text--darken-2">FILED AND PENDING</span>
                  <span class="vert-pipe" />
                  <span>PAID
                    <FiledLabel :filing="filing" />
                  </span>
                  <v-btn
                    class="details-btn orange--text text--darken-2"
                    :ripple=false
                    @click.stop="togglePanel(index, filing)"
                  >
                    <v-icon left>mdi-alert</v-icon>
                    <span>{{ (panel === index) ? "Hide Details" : "View Details" }}</span>
                  </v-btn>
                </div>


                <div v-else class="item-header__subtitle">
                  <span>FILED AND PAID
                    <FiledLabel :filing="filing" />
                  </span>
                </div>

                <!-- optional detail comments button -->
                <div v-if="filing.commentsCount > 0" class="item-header__subtitle mb-n2">
                  <v-btn class="comments-btn" flat :ripple=false @click.stop="togglePanel(index, filing)">
                    <v-icon small left style="padding-top: 2px" class="app-blue">mdi-message-reply</v-icon>
                    <span class="app-blue">Detail{{ filing.commentsCount > 1 ? "s" : "" }} ({{ filing.commentsCount
                    }})</span>
                  </v-btn>
                </div>
              </div>

              <!-- the action button/menu (right side) -->
              <div class="item-header__actions">
                <v-btn class="expand-btn" variant="flat" :ripple="false"  @click.stop="togglePanel(index, filing)"
                  v-show="displayAction(filing)">
                  <span v-if="filing.availableOnPaperOnly" class="app-blue">
                    {{ (panel === index) ? "Close" : "Request a Copy" }}
                  </span>
                  <span v-else-if="filing.isTypeStaff" class="app-blue">
                    {{ (panel === index) ? "Hide" : "View" }}
                  </span>
                  <span v-else-if="filing.documentsLink" class="app-blue">
                    {{ (panel === index) ? "Hide Documents" : "View Documents" }}
                  </span>                  
                </v-btn>
              </div>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <div>
              <!-- NB: blocks below are mutually exclusive, and order is important -->

              <template v-if="filing.isTypeStaff">
                <StaffFiling :filing="filing" class="mt-6" />
              </template>

              <!-- is this a FE BCOMP COA pending (not yet completed) -->
              <template v-else-if="filing.isFutureEffectiveBcompCoaPending">
                <!-- no details -->
              </template>

              <!-- is this a completed alteration -->
              <template v-else-if="filing.isCompletedAlteration">
                <CompletedAlteration :filing=filing :entity-name="entity.name" class="mt-6" />
              </template>

              <!-- is this a completed dissolution -->
              <template v-else-if="filing.isCompletedDissolution">
                <CompletedDissolution :filing="filing" class="mt-6" />
              </template>

              <template
                v-else-if="filing.isFutureEffectiveAlterationPending || filing.isFutureEffectiveDissolutionPending">
                <FutureEffectivePending :filing=filing class="mt-6" :entity-name="entity.name" />
              </template>

              <!-- is this a FE IA still waiting for effective date/time? -->
              <!-- or a FE Alteration still waiting for effective date/time?  -->
              <!-- or a FE Dissolution still waiting for effective date/time?  -->
              <template v-else-if="filing.isFutureEffectiveAlteration || filing.isFutureEffectiveDissolution">
                <FutureEffective :filing=filing class="mt-6" :entity-name="entity.name" />
              </template>

              <!-- is this a generic paid (not yet completed) filing? -->
              <template v-else-if="isStatusPaid(filing)">
                <PendingFiling :filing=filing class="mt-6" />
              </template>

              <!-- is this a paper filing? -->
              <template v-else-if="filing.availableOnPaperOnly">
                <PaperFiling class="mt-6" />
              </template>

              <!-- else this must be a completed filing -->
              <template v-else>
                <!-- no details -->
              </template>

              <!-- the documents section -->
              <template v-if="filing.documents && filing.documents.length > 0">
                <v-divider class="my-6" />
                <DocumentsList :filing=filing :loadingOne=loadingOne :loadingAll=loadingAll
                  :loadingOneIndex=loadingOneIndex @downloadOne="downloadOne" @downloadAll="downloadAll"
                  :isLocked=isLocked />
              </template>

              <!-- the details (comments) section -->
              <template v-if="filing.comments && filing.commentsCount > 0">
                <v-divider class="my-6" />
                <DetailsList :filing=filing :isTask="false" />
              </template>

            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
      <!-- No Results Message -->
      <v-card class="no-results" flat v-else>
        <v-card-text>
          <div class="no-results__title">No filing history. Completed filings and 
            transactions will appear here.</div>           
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script setup lang="ts">
// external
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { StatusCodes } from 'http-status-codes'
// Components and dialogs
import CompletedAlteration from './CompletedAlteration.vue'
import CompletedDissolution from './CompletedDissolution.vue'
import DocumentsList from './DocumentsList.vue'
import FiledLabel from './FiledLabel.vue'
import FutureEffective from './FutureEffective.vue'
import FutureEffectivePending from './FutureEffectivePending.vue'
import PaperFiling from './PaperFiling.vue'
import PendingFiling from './PendingFiling.vue'
import StaffFiling from './StaffFiling.vue'
import { DetailsList, ErrorRetry } from '@/components'
import {
  isStatusPaid, isStatusCompleted, isTypeAlteration, isTypeChangeOfAddress,
  isEffectOfOrderPlanOfArrangement, isTypeDissolution, isTypeStaff, filingTypeToName, camelCaseToWords,
  dateToYyyyMmDd, dateToPacificDateTime, flattenAndSortComments, isEffectiveDateFuture, isEffectiveDatePast
} from '@/utils'
import { fetchDocumentList, fetchComments } from '@/requests'
import { LegalFiling, ApiFiling } from '@/interfaces/legal-api-responses'

// Enums, interfaces and mixins
import { ErrorCategories, ErrorCodes, FilingTypes, RouteNames } from '@/enums'
import { Document, FilingHistoryItem } from '@/types'
import { useEntity, useFilingHistory, useDocumentAccessRequest } from '@/composables'
import { ErrorI } from '@/interfaces'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ isLocked: boolean }>()

const router = useRouter()
const { entity, isBComp } = useEntity()
const { filingHistory, hasCourtOrderFilings, loadFilingHistory } = useFilingHistory()
const { downloadFilingDocument } = useDocumentAccessRequest()

const filings = computed(() => filingHistory.filings)


const panel = ref(-1) // currently expanded panel
const historyErrorMsg = computed(() => {
  if (router.currentRoute.value.name === RouteNames.DOCUMENT_REQUEST) {
    return 'We were unable to retrieve the filing history. This purchase will be ' +
      'available under Recently Purchased Documents for 14 days. Please try again later.'
  }
  return 'We were unable to retrieve the filing history for this business. Please try again later.'
})
const historyItems = ref([])
const loadingOne = ref(false)
const loadingAll = ref(false)
const loadingOneIndex = ref(-1)
const isBusy = ref(false)

const emit = defineEmits(['error'])

const documentDownloadError: ErrorI = {
  category: ErrorCategories.REPORT_GENERATION,
  message: 'Document Download Error',
  statusCode: StatusCodes.INTERNAL_SERVER_ERROR,
  type: ErrorCodes.SERVICE_UNAVAILABLE
}

/** Returns whether the action button is visible or not. */
const displayAction = (filing): string => {
  return filing.availableOnPaperOnly || filing.isTypeStaff || filing.documentsLink
}

const loadData = (): void => {
  isBusy.value = true
  historyItems.value = []

  // create 'history items' list from 'filings' array from API
  for (const filing of filings.value) {

    // safety check for required fields
    if (!filing.name || !filing.displayName || !filing.effectiveDate || !filing.submittedDate || !filing.status) {
      console.warn('Invalid filing =', filing)
      continue
    }
    loadFiling(filing)
    isBusy.value = false
  }
}

/** Loads a filing into the historyItems list. */
const loadFiling = (filing: ApiFiling): void => {
  try {
    const effectiveDate = new Date(filing.effectiveDate)
    const submittedDate = new Date(filing.submittedDate)

    // build filing item
    const item: FilingHistoryItem = {
      availableOnPaperOnly: filing.availableOnPaperOnly,
      commentsCount: filing.commentsCount,
      displayName: filing.displayName,
      effectiveDate,
      filingId: filing.filingId,
      isFutureEffective: filing.isFutureEffective,
      name: filing.name || FilingTypes.UNKNOWN,
      status: filing.status,
      submittedDate,
      submitter: filing.submitter,

      commentsLink: filing.commentsLink,
      documentsLink: filing.documentsLink,
      filingLink: filing.filingLink,

      comments: null, // null until loaded
      documents: null // null until loaded
    }

    // add properties for correction filings
    // (a correction filing has the id of the filing that it corrects)
    if (filing.correctedFilingId) {
      item.correctedFilingId = filing.correctedFilingId
      item.correctedLink = filing.correctedLink
    }

    // add properties for corrected filings
    // (a corrected filing has the id of the filing that corrects it)
    if (filing.correctionFilingId) {
      item.correctionFilingId = filing.correctionFilingId
      item.correctionLink = filing.correctionLink
    }

    // add properties for BCOMP COAs
    if (isBComp.value && isTypeChangeOfAddress(filing)) {
      // is this a Future Effective BCOMP COA pending (not yet completed)?
      // (NB: this is False after the effective date)
      item.isFutureEffectiveBcompCoaPending = (
        filing.isFutureEffective &&
        isStatusPaid(filing) &&
        isEffectiveDateFuture(effectiveDate)
      )
    }

    // add properties for Alterations
    if (isTypeAlteration(filing)) {
      item.isCompletedAlteration = isStatusCompleted(filing)
      item.isFutureEffectiveAlteration = (
        filing.isFutureEffective &&
        isStatusPaid(filing)
      )
      item.isFutureEffectiveAlterationPending = (
        item.isFutureEffectiveAlteration &&
        isEffectiveDatePast(effectiveDate)
      )
      if (item.isCompletedAlteration) {
        item.courtOrderNumber = filing.data.order?.fileNumber || ''
        item.isArrangement = isEffectOfOrderPlanOfArrangement(filing.data.order?.effectOfOrder)
        item.toLegalType = filing.data.alteration?.toLegalType || null
        item.fromLegalType = filing.data.alteration?.fromLegalType || null
      }
    }

    // add properties for Dissolutions
    if (isTypeDissolution(filing)) {
      // is this a completed dissolution?
      item.isCompletedDissolution = isStatusCompleted(filing)

      // is this a Future Effective dissolution (not yet completed)?
      item.isFutureEffectiveDissolution = (
        filing.isFutureEffective &&
        isStatusPaid(filing)
      )

      // is this a Future Effective dissolution pending (overdue)?
      item.isFutureEffectiveDissolutionPending = (
        item.isFutureEffectiveDissolution &&
        isEffectiveDatePast(effectiveDate)
      )
    }

    // add properties for staff filings
    if (isTypeStaff(filing)) {
      item.documents = [] // no documents
      item.fileNumber = filing.data.order?.fileNumber || '' // may be falsy
      item.isTypeStaff = true
      item.notationOrOrder = filing.data.order?.orderDetails // should not be falsy
      item.planOfArrangement = filing.data.order?.effectOfOrder ? 'Pursuant to a Plan of Arrangement' : ''
    }

    historyItems.value.push(item)
  } catch (error) {
    console.error('Error loading filing =', error)
  }
}

const downloadOne = async (event): Promise<void> => {
  if (event.document && event.index >= 0) { // safety check
    loadingOne.value = true
    loadingOneIndex.value = event.index

    await downloadFilingDocument(entity.identifier, event.filing.filingId, event.document).catch(error => {
      console.error('fetchFilingDocument() error =', error)
      emit('error', documentDownloadError)
    })

    loadingOne.value = false
    loadingOneIndex.value = -1
  }
}

const downloadAll = async (event): Promise<void> => {
  if (event.filing?.documents) {
    loadingAll.value = true
    const filteredDocuments = event.filing.documents.filter(document => (document.title.toLowerCase() != 'receipt'))

    for (const document of filteredDocuments) {
      await downloadFilingDocument(entity.identifier, event.filing.filingId, document).catch(error => {
        console.error('fetchFilingDocument() error =', error)
        emit('error', documentDownloadError)
      })
    }
    loadingAll.value = false
  }
}

/** Loads the comments for this history item. */
const loadComments = async (item: FilingHistoryItem): Promise<void> => {
  try {
    const comments = await fetchComments(item.commentsLink)
    item.comments = flattenAndSortComments(comments)
  } catch (error) {
    item.comments = null
    console.warn('loadComments() error =', error)
  }
  item.commentsCount = item.comments?.length || 0
}

/** Loads the documents for this history item. */
const loadDocuments = async (item: FilingHistoryItem): Promise<void> => {
  try {
    const documents = await fetchDocumentList(entity.identifier, item.filingId)
    item.documents = []
    for (const prop in documents) {
      if (prop === 'legalFilings' && Array.isArray(documents.legalFilings)) {
        for (const legalFiling of documents.legalFilings as LegalFiling[]) {
          for (const prop in legalFiling) {
            let title
            if (prop === item.name) title = item.displayName
            else title = filingTypeToName(prop as FilingTypes, null, true)
            const date = dateToYyyyMmDd(item.submittedDate)
            const filename = `${entity.identifier} ${title} - ${date}.pdf`
            const link = legalFiling[prop] as string
            pushDocument(title, filename, link)
          }
        }
      } else if (prop !== 'receipt') {
        const title = camelCaseToWords(prop)
        const date = dateToYyyyMmDd(item.submittedDate)
        const filename = `${entity.identifier} ${title} - ${date}.pdf`
        const link = documents[prop] as string
        pushDocument(title, filename, link)
      }
    }
  } catch (error) {
    item.documents = null
    console.error('loadDocuments() error =', error)
  }

  function pushDocument(title: string, filename: string, link: string) {
    if (title && filename && link) {
      item.documents.push({ title, filename, link } as Document)
    } else {
      console.error(`invalid document = ${title} | ${filename} | ${link}`)
    }
  }
}

/** Closes current panel or opens new panel. */
const togglePanel = async (index: number, item: FilingHistoryItem): Promise<void> => {
  const isCurrentPanel = (panel.value === index)

  // check if we're opening a new panel
  if (!isCurrentPanel) {
    const promises: Array<Promise<void>> = []
    // check if we're missing comments or documents
    if (item.commentsLink && !item.comments) promises.push(loadComments(item))
    if (item.documentsLink && !item.documents) promises.push(loadDocuments(item))

    if (promises.length > 0) {
      isBusy.value = true
      // NB: errors are handled in loadComments() and loadDocuments()
      await Promise.all(promises)
      // leave busy spinner displayed another 250ms
      // to mitigate flashing when the promises are resolved quickly
      setTimeout(() => { isBusy.value = false }, 250)
    }
  }

  // toggle the subject panel
  panel.value = isCurrentPanel ? null : index
}

watch(() => filings.value, () => {
  loadData()
})

onMounted(async () => {
  if (filingHistory.filings.length > 0) {
    loadData()
  }
})
</script>

<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";
.error-retry-filings {
  max-width: 550px;
}

.scrollable-container {
  background-color: white;
  max-height: 60rem;
  overflow-y: auto;
  margin-bottom: 50px;
}

.filing-history-item {
  // disable expansion generally
  pointer-events: none;
}

// specifically enable anchors, buttons, the pending alert icon and tooltips
// for this page and sub-components
:deep(a),
:deep(.v-btn),
:deep(.pending-alert .v-icon),
:deep(.v-tooltip+div) {
  pointer-events: auto;
}

.item-header {
  line-height: 1.25rem;
  width: 100%;

  &__label {
    flex: 1 1 auto;
    text-align: left;
  }

  &__actions {
    padding-left: 3.5rem;     
    text-align: right;
    min-width: 12rem;
    margin-right: -15px;
    
    .expand-btn {
      letter-spacing: -0.01rem;
      font-size: $px-14;
      font-weight: 700;
    }

    :deep(.v-btn__overlay) {
        background-color: $gray9 !important;
    }   

    // make menu button slightly smaller
    .menu-btn {
      height: unset !important;
      min-width: unset !important;
      padding: 0.25rem !important;
    }
  }

  &__title {
    font-size: 16px;
    color: $gray9;
    font-weight: bold;
  }

  &__subtitle {
    color: $gray6;
    margin-top: 0.5rem;
  }
}

.item-header+.item-header {
  border-top: 1px solid $gray3;
}


.v-col-padding {
  padding: 0 12px 0 12px;
}

.pending-tooltip {
  max-width: 16.5rem;
}

.pending-alert .v-icon {
  font-size: 18px; // same as other v-icons
  padding-left: 0.875rem;
}

.details-btn,
.expand-btn,
.comments-btn {
  border: none;
}

.details-btn {   
  box-shadow: none;
  margin-bottom: 0.25rem;
  padding-left: 0;
}

.v-expansion-panel {
  box-shadow: none !important;
}

:deep(.v-expansion-panel-text__wrapper) {
  padding: 0;
}

:deep(.v-expansion-panel-title__overlay) {
  background-color: white;
}

.court-order-section {
  color: $gray7;
  width: 100%;
  background-color: white;
}
.court-order-section .v-icon {
  color: $gray9;
}
</style>
