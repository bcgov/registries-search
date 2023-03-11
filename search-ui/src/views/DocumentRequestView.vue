<template>
    <v-container id="business-info" class="container" fluid>
        <v-fade-transition>
            <div class="loading-container grayed-out" v-if="documentAccessRequest._downloading">
                <div class="loading__content">
                    <v-progress-circular color="primary" size="50" indeterminate />
                    <div class="loading-msg" v-if="documentAccessRequest._downloading">Downloading document</div>
                </div>
            </div>
        </v-fade-transition>
        <v-row no-gutters>
            <v-col cols="9">
                <span class="section-header">Purchased Documents as of {{ submissionDate }}</span>
                <p class="pt-6">
                    Your documents are now available to view and download.
                    You will be able to access these documents for up to 14 days from the business search dashboard.
                </p>
                <div class="pa-6 mt-8 warning-message" v-if="hasNewFilings">
                    <b>Important:</b> There have been changes to this business since your purchase.
                    To view the updated list of filings and to purchase up-to-date documents,
                    <span class="app-blue new-search-link" @click="gotoSearch()">
                        conduct a new search for this business</span>
                </div>
                <p class="pt-6" v-else>
                    If you wish to purchase additional documents, <span class="app-blue new-search-link"
                        @click="gotoSearch()">
                        conduct a new search for this business</span>
                </p>
                <v-divider class="my-10" />
                <span class="section-header">Business Documents</span>
                <div class="document-list mt-3 pa-3 pr-5">
                    <v-list class="py-0" density="compact">
                        <v-list-item v-for="(document, index) in documents" :key="index">
                            <span class="app-blue doc-link pt-6" @click="downloadDoc(document)">
                                <img class="mb-n1" :src="require('@/assets/svgs/pdf-icon-blue.svg')" />
                                <span class="pl-2">{{ documentDescription(document.documentType) }}</span>
                            </span>
                        </v-list-item>
                    </v-list>
                </div>                
                <div>
                    <filing-history :isLocked=false v-if="showFilingHistory" class="mt-10"/>
                </div>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import FilingHistory from '@/components/FilingHistory/FilingHistory.vue'
import { useEntity, useFilingHistory, useDocumentAccessRequest } from '@/composables'
import { DocumentDetailsI, DocumentI } from '@/interfaces'
import { dateToPacificDateTime } from '@/utils'
import { DocumentTypeDescriptions } from '@/resources'
import { DocumentType, RouteNames } from '@/enums'

const { entity } = useEntity()
const { filingHistory } = useFilingHistory()
const { documentAccessRequest, downloadDocument } = useDocumentAccessRequest()

const router = useRouter()

onMounted(async () => {
    const currentRequest: DocumentDetailsI = documentAccessRequest.currentRequest
    if (currentRequest == null) {
        router.push('/')
    }
})

const documents = computed(() => documentAccessRequest.currentRequest?.documents || [])
const submissionDate = computed(() => (documentAccessRequest.currentRequest?.submissionDate) ?
    dateToPacificDateTime(new Date(documentAccessRequest.currentRequest.submissionDate)) : '')
const showFilingHistory = computed(() => documents.value.find(doc => (
    doc.documentType == DocumentType.BUSINESS_SUMMARY_FILING_HISTORY)) != null)
const hasNewFilings = computed(() => {
    if (filingHistory.latestFiling && filingHistory.latestFiling.filingId != filingHistory.filings[0].filingId) {
        return true
    }
    return false
})

const documentDescription = (type: string): string => {
    return DocumentTypeDescriptions[type]
}

const downloadDoc = (document: DocumentI): void => {
    downloadDocument(entity.identifier, document)
}

const gotoSearch = (): void => {
     const identifier = entity.identifier
     router.push({ name: RouteNames.BUSINESS_INFO, params: { identifier } })
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.document-list {
  background-color: white;
  border-radius: 5px;
  width: 100%;

  :deep(.v-list-item:hover) {
    background-color: white;
  }
}

.doc-link {
    cursor: pointer;
    font-size: 14px;
}

.new-search-link {
    text-decoration: underline;
    cursor: pointer;
}

.warning-message {
    width: 100%;
    background-color: #FFF7C4;
    border: solid 1px #F9C90C
}

.v-divider {
    border-width: 1px;
}
</style>
