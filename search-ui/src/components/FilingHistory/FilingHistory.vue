<template>
  <div id="filing-history-list">

    <!--<DownloadErrorDialog :dialog="downloadErrorDialog" @close="downloadErrorDialog = false"
      attach="#filing-history-list" />-->

    <!-- Alternate Loading Spinner -->
    <v-fade-transition>
      <div class="loading-container grayed-out" v-show="isBusy">
        <div class="loading__content">
          <v-progress-circular color="primary" size="50" indeterminate />
          <div class="loading-msg white--text">Fetching data</div>
        </div>
      </div>
    </v-fade-transition>

    <div class="scrollable-container">
      <v-expansion-panels v-if="historyItems.length > 0" v-model="panel">
        <v-expansion-panel class="align-items-top filing-history-item px-6 py-5" v-for="(filing, index) in historyItems"
          :key="index">
          <v-expansion-panel-title class="no-dropdown-icon pa-0">
            <div class="item-header d-flex">
              <!-- the filing label (left side) -->
              <div class="item-header__label">
                <h3 class="item-header__title">{{ filing.displayName }}</h3>

                <!-- NB: blocks below are mutually exclusive, and order is important -->

                <!-- is this a Staff Only filing? -->
                <div v-if="filing.isTypeStaff" class="item-header__subtitle">
                  <FiledLabel :filing="filing" />
                </div>

                <!-- is this a FE BCOMP COA pending (not yet completed)? -->
                <div v-else-if="filing.isFutureEffectiveBcompCoaPending" class="item-header__subtitle">
                  <span>FILED AND PENDING
                    <FiledLabel :filing="filing" />
                  </span>
                  <v-tooltip top content-class="pending-tooltip">
                    <template v-slot:activator="{ props }">
                      <div class="pending-alert" v-on="props">
                        <v-icon color="orange darken-2">mdi-alert</v-icon>
                      </div>
                    </template>
                    The updated office addresses will be legally effective on
                    {{ dateToPacificDateTime(filing.effectiveDate) }}.
                    No other filings are allowed until then.
                  </v-tooltip>
                </div>

                <!-- is this a completed IA? -->
                <!-- or a completed Alteration? -->
                <!-- or a completed Dissolution? -->
                <div v-else-if="filing.isCompletedIa || filing.isCompletedAlteration || filing.isCompletedDissolution"
                  class="item-header__subtitle">
                  <span>FILED AND PAID
                    <FiledLabel :filing="filing" />
                  </span>
                  <v-btn class="details-btn" flat color="blue darken-2" :ripple=false
                    @click.stop="togglePanel(index, filing)">
                    <v-icon left>mdi-information-outline</v-icon>
                    <span>{{ (panel === index) ? "Hide Details" : "View Details" }}</span>
                  </v-btn>
                </div>

                <!-- is this a FE IA pending (overdue)? -->
                <!-- or a FE Alteration pending (overdue)? -->
                <!-- or a FE Dissolution pending (overdue)? -->
                <div v-else-if="filing.isFutureEffectiveAlterationPending ||
                filing.isFutureEffectiveDissolutionPending" class="item-header__subtitle">
                  <span class="orange--text text--darken-2">FILED AND PENDING</span>
                  <span class="vert-pipe" />
                  <span>PAID
                    <FiledLabel :filing="filing" />
                  </span>
                  <v-btn class="details-btn" outlined color="orange darken-2" :ripple=false
                    @click.stop="togglePanel(index, filing)">
                    <v-icon left>mdi-alert</v-icon>
                    <span>{{ (panel === index) ? "Hide Details" : "View Details" }}</span>
                  </v-btn>
                </div>

                <!-- is this a FE IA still waiting for effective date/time? -->
                <!-- is this a FE Alteration still waiting for effective date/time? -->
                <!-- is this a FE Dissolution still waiting for effective date/time? -->
                <div v-else-if="filing.isFutureEffectiveAlteration ||
                filing.isFutureEffectiveDissolution" class="item-header__subtitle">
                  <span v-if="filing.isFutureEffectiveAlteration">FUTURE EFFECTIVE ALTERATION</span>
                  <span v-if="filing.isFutureEffectiveDissolution">FUTURE EFFECTIVE DISSOLUTION</span>
                  <span class="vert-pipe" />
                  <span>PAID
                    <FiledLabel :filing="filing" />
                  </span>
                  <v-btn class="details-btn" outlined color="blue darken-2" :ripple=false
                    @click.stop="togglePanel(index, filing)">
                    <v-icon left>mdi-information-outline</v-icon>
                    <span>{{ (panel === index) ? "Hide Details" : "View Details" }}</span>
                  </v-btn>
                </div>

                <!-- is this a generic paid (not yet completed) filing? -->
                <div v-else-if="isStatusPaid(filing)" class="item-header__subtitle">
                  <span class="orange--text text--darken-2">FILED AND PENDING</span>
                  <span class="vert-pipe" />
                  <span>PAID
                    <FiledLabel :filing="filing" />
                  </span>
                  <v-btn class="details-btn" outlined color="orange darken-2" :ripple=false
                    @click.stop="togglePanel(index, filing)">
                    <v-icon left>mdi-alert</v-icon>
                    <span>{{ (panel === index) ? "Hide Details" : "View Details" }}</span>
                  </v-btn>
                </div>

                <!-- else this must be a completed filing -->
                <!-- NB: no view/hide details button -->
                <div v-else class="item-header__subtitle">
                  <span>FILED AND PAID
                    <FiledLabel :filing="filing" />
                  </span>
                </div>

                <!-- optional detail comments button -->
                <div v-if="filing.commentsCount > 0" class="item-header__subtitle mb-n2">
                  <v-btn class="comments-btn" outlined color="primary" :ripple=false
                    @click.stop="togglePanel(index, filing)">
                    <v-icon small left style="padding-top: 2px">mdi-message-reply</v-icon>
                    <span>Detail{{ filing.commentsCount > 1 ? "s" : "" }} ({{ filing.commentsCount }})</span>
                  </v-btn>
                </div>
              </div>

              <!-- the action button/menu (right side) -->
              <div class="item-header__actions">
                <v-btn class="expand-btn" flat :ripple=false @click.stop="togglePanel(index, filing)"
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
            <!-- NB: blocks below are mutually exclusive, and order is important -->

            <!-- is this a Staff Only filing? -->
            <template v-if="filing.isTypeStaff">
              <StaffFiling :filing="filing" class="mt-6" />
            </template>

            <!-- is this a FE BCOMP COA pending (not yet completed)? -->
            <template v-else-if="filing.isFutureEffectiveBcompCoaPending">
              <!-- no details -->
            </template>

            <!-- is this a completed alteration? -->
            <template v-else-if="filing.isCompletedAlteration">
              <CompletedAlteration :filing=filing :entity-name="legalName" class="mt-6" />
            </template>

            <!-- is this a completed dissolution? -->
            <template v-else-if="filing.isCompletedDissolution">
              <CompletedDissolution :filing="filing" :entity-name="legalName" :entity-type="legalType" class="mt-6" />
            </template>

            <!-- is this a FE IA pending (overdue)? -->
            <!-- or a FE Alteration pending (overdue)? -->
            <!-- or a FE Dissolution pending (overdue)? -->
            <template
              v-else-if="filing.isFutureEffectiveAlterationPending || filing.isFutureEffectiveDissolutionPending">
              <FutureEffectivePending :filing=filing class="mt-6" />
            </template>

            <!-- is this a FE IA still waiting for effective date/time? -->
            <!-- or a FE Alteration still waiting for effective date/time?  -->
            <!-- or a FE Dissolution still waiting for effective date/time?  -->
            <template v-else-if="filing.isFutureEffectiveAlteration || filing.isFutureEffectiveDissolution">
              <FutureEffective :filing=filing class="mt-6" />
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
                :loadingOneIndex=loadingOneIndex @downloadOne="downloadOne" @downloadAll="downloadAll($event)" />
            </template>

            <!-- the details (comments) section -->
            <template v-if="filing.comments && filing.commentsCount > 0">
              <v-divider class="my-6" />
              <DetailsList :filing=filing :isTask="false" />
            </template>

          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </div>

    <!-- No Results Message -->
    <v-card class="no-results" flat v-if="!historyItems.length">
      <v-card-text>
        <template>
          <div class="no-results__title">You have no filing history</div>
          <div class="no-results__subtitle">Your completed filings and transactions will appear here</div>
        </template>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">

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
import { DetailsList } from '@/components/common'
import {
  isStatusPaid, isStatusCompleted, isTypeAlteration, isTypeChangeOfAddress,
  isEffectOfOrderPlanOfArrangement, isTypeDissolution, isTypeStaff, filingTypeToName, camelCaseToWords,
  dateToYyyyMmDd, dateToPacificDateTime
} from '@/utils'
import { fetchDocument, fetchDocuments, fetchComments, flattenAndSortComments } from '@/requests'
import { LegalFiling } from '@/types'
//import { DownloadErrorDialog } from '@/components/dialogs'

// Enums, interfaces and mixins
import { ref, computed, watch } from 'vue'
import { FilingTypes } from '@/enums'
import { useStore } from 'vuex'
import { Document, FilingHistoryItem, ApiFiling } from '@/types'

const store = useStore()

const isBComp = computed(() => store.getters['isBComp'] as boolean)
const identifier = computed(() => store.getters['getIdentifier'] as string)
const legalName = computed(() => store.getters['getLegalName'] as string)
const legalType = computed(() => store.getters['getLegalType'] as string)
const filings = computed(() => store.state.filings as ApiFiling[])

const downloadErrorDialog = ref(false)
const panel = ref(-1) // currently expanded panel
const historyItems = ref([])
const loadingOne = ref(false)
const loadingAll = ref(false)
const loadingOneIndex = ref(-1)
const isBusy = ref(false)

const emit = defineEmits(['history-count'])

/** Returns whether the action button is visible or not. */
const displayAction = (filing): string => {
  return filing.availableOnPaperOnly || filing.isTypeStaff || filing.documentsLink
}

const loadData = (): void => {
  historyItems.value = []

  // create 'history items' list from 'filings' array from API
  for (const filing of filings.value) {

    // safety check for required fields
    if (!filing.name || !filing.displayName || !filing.effectiveDate || !filing.submittedDate || !filing.status) {
      // eslint-disable-next-line no-console
      console.log('Invalid filing =', filing)
      continue
    }
    loadFiling(filing)
  }

  // report number of items back to parent (dashboard)
  emit('history-count', historyItems.value.length)
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
      // is this a completed alteration?
      item.isCompletedAlteration = isStatusCompleted(filing)

      // is this a Future Effective alteration (not yet completed)?
      item.isFutureEffectiveAlteration = (
        filing.isFutureEffective &&
        isStatusPaid(filing)
      )

      // is this a Future Effective alteration pending (overdue)?
      item.isFutureEffectiveAlterationPending = (
        item.isFutureEffectiveAlteration &&
        isEffectiveDatePast(effectiveDate)
      )

      // data is available only for a completed filing
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
    // eslint-disable-next-line no-console
    console.log('Error loading filing =', error)
  }
}

/** Whether the subject effective date/time is in the past. */
const isEffectiveDatePast = (effectiveDate: Date): boolean => {
  // FUTURE: stop assuming local date is correct
  return (effectiveDate <= new Date())
}

/** Whether the subject effective date/time is in the future. */
const isEffectiveDateFuture = (effectiveDate: Date): boolean => {
  // FUTURE: stop assuming local date is correct
  return (effectiveDate > new Date())
}


const downloadOne = async (document: Document, index: number): Promise<void> => {
  if (document && index >= 0) { // safety check
    loadingOne.value = true
    loadingOneIndex.value = index

    await fetchDocument(document).catch(error => {
      // eslint-disable-next-line no-console
      console.log('fetchDocument() error =', error)
      // downloadErrorDialog.value = true
    })

    loadingOne.value = false
    loadingOneIndex.value = -1
  }
}

const downloadAll = async (item: FilingHistoryItem): Promise<void> => {
  if (item?.documents) { // safety check
    loadingAll.value = true

    for (const document of item.documents) {
      await fetchDocument(document).catch(error => {
        // eslint-disable-next-line no-console
        console.log('fetchDocument() error =', error)
        // downloadErrorDialog.value = true
      })
    }

    loadingAll.value = false
  }
}

/** Loads the comments for this history item. */
const loadComments = async (item: FilingHistoryItem): Promise<void> => {
  try {
    // fetch comments array from API
    const comments = await fetchComments(item.commentsLink)
    // flatten and sort the comments
    item.comments = flattenAndSortComments(comments)
  } catch (error) {
    // set property to null to retry next time
    item.comments = null
    // eslint-disable-next-line no-console
    console.log('loadComments() error =', error)
    // FUTURE: enable some error dialog?
  }
  // update comments count
  item.commentsCount = item.comments?.length || 0
}

/** Loads the documents for this history item. */
const loadDocuments = async (item: FilingHistoryItem): Promise<void> => {
  try {
    // fetch documents object from API
    const documents = await fetchDocuments(item.documentsLink)
    // load each type of document
    item.documents = []
    // iterate over documents properties
    for (const prop in documents) {
      if (prop === 'legalFilings' && Array.isArray(documents.legalFilings)) {
        // iterate over legalFilings array
        for (const legalFiling of documents.legalFilings as LegalFiling[]) {
          // iterate over legalFiling properties
          for (const prop in legalFiling) {
            // this is a legal filing output
            let title
            // use display name for primary document's title
            if (prop === item.name) title = item.displayName
            else title = filingTypeToName(prop as FilingTypes, null, true)
            const date = dateToYyyyMmDd(item.submittedDate)
            const filename = `${identifier.value} ${title} - ${date}.pdf`
            const link = legalFiling[prop] as string
            pushDocument(title, filename, link)
          }
        }
      } else {
        // this is a submission level output
        const title = camelCaseToWords(prop)
        const date = dateToYyyyMmDd(item.submittedDate)
        const filename = `${identifier.value} ${title} - ${date}.pdf`
        const link = documents[prop] as string
        pushDocument(title, filename, link)
      }
    }
  } catch (error) {
    // set property to null to retry next time
    item.documents = null
    // eslint-disable-next-line no-console
    console.log('loadDocuments() error =', error)
    // FUTURE: enable some error dialog?
  }

  function pushDocument(title: string, filename: string, link: string) {
    if (title && filename && link) {
      item.documents.push({ title, filename, link } as Document)
    } else {
      // eslint-disable-next-line no-console
      console.log(`invalid document = ${title} | ${filename} | ${link}`)
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

</script>

<style lang="scss" scoped>
@import "@/assets/styles/theme.scss";

.scrollable-container {
  max-height: 60rem;
  overflow-y: auto;
}

.filing-history-item {
  // disable expansion generally
  pointer-events: none;
}

// specifically enable anchors, buttons, the pending alert icon and tooltips
// for this page and sub-components
::v-deep a,
::v-deep .v-btn,
::v-deep .pending-alert .v-icon,
::v-deep .v-tooltip+div {
  pointer-events: auto;
}

.item-header {
  line-height: 1.25rem;
  width:100%;

  &__label {
    flex: 1 1 auto;
    text-align: left;
  }

  &__actions {
    text-align: right;
    min-width: 12rem;

    .expand-btn {
      letter-spacing: -0.01rem;
      font-size: $px-14;
      font-weight: 700;
    }

    // make menu button slightly smaller
    .menu-btn {
      height: unset !important;
      min-width: unset !important;
      padding: 0.25rem !important;
    }
  }

  &__title {
    font-weight: 700;
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
  margin-bottom: 0.25rem;
}

.v-expansion-panel {
  box-shadow: none !important;
}

::v-deep .v-expansion-panel-text__wrap {
  padding: 0;
}

::v-deep .theme--light.v-list-item--disabled {
  opacity: 0.38 !important;
}
</style>
