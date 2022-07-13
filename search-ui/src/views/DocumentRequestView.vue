<template>
    <v-container id="business-info" class="container" fluid>
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
                <span class="header">Purchased Documents as of {{ submissionDate }}</span>
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
                <h2>Business Documents</h2>
                <div class="document-list  mt-3 pa-3 pr-5 pt-4 pb-8">
                    <v-list class="py-0" density="compact">
                        <v-list-item v-for="(document, index) in documents" :key="index">
                            <span class="app-blue doc-link pt-6" @click="downloadDoc(document)">
                                <v-icon class="app-blue pr-1">mdi-file-pdf-box</v-icon>
                                {{ documentDescription(document.documentType) }}
                            </span>
                        </v-list-item>
                    </v-list>
                </div>
                <v-divider class="my-10" />
                <div>
                    <filing-history :isLocked=false v-if="showFilingHistory" />
                </div>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'

import FilingHistory from '@/components/FilingHistory/FilingHistory.vue'
import { useEntity, useFilingHistory, useDocumentAccessRequest } from '@/composables'
import { DocumentDetailsI, DocumentI } from '@/interfaces'
import { dateToPacificDateTime } from '@/utils'
import { DocumentTypeDescriptions } from '@/resources'
import { DocumentType } from '@/enums'
import { useRouter } from 'vue-router'

const { entity, loadEntity } = useEntity()
const { loadFilingHistory, filingHistory } = useFilingHistory()
const { documentAccessRequest, downloadDocument } = useDocumentAccessRequest()

const router = useRouter()

onMounted(async () => {
    const currentRequest: DocumentDetailsI = documentAccessRequest.currentRequest
    await loadEntity(currentRequest.businessIdentifier)
    await loadFilingHistory(currentRequest.businessIdentifier, currentRequest.submissionDate)
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
    router.push('/')
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.header {
    font-size: 1.25rem;
    font-weight: bold;
    color: #212529
}

.document-list {
    background-color: white;
    width: 100%;
}

.doc-link {
    cursor: pointer;
    font-size: 0.95rem;
}

.new-search-link {
    text-decoration: underline;
}

.warning-message {
    width: 100%;
    background-color: #FFF7C4;
    border: solid 1px #F9C90C
}
</style>
