<template>
    <div class="main-results-div white-background soft-corners pb-2 mt-4 justify-center">
        <v-row class="pt-3 pl-4" justify="center" no-gutters>
            <v-col v-if="documentAccessRequest._loading" cols="auto">
                <v-progress-circular v-if="documentAccessRequest._loading" color="primary" size="50" indeterminate />
            </v-col>
            <v-col v-else cols="12">
                <v-table fixed-header class="table">
                    <thead>
                        <tr>
                            <th width="33%" class="bg-grey-lighten-4">Submitted on</th>
                            <th width="33%" class="bg-grey-lighten-4">Expires on</th>
                            <th width="34%" class="bg-grey-lighten-4 opaque-header">Documents</th>
                        </tr>
                    </thead>
                    <tbody v-if="totalResultsLength > 0">
                        <tr v-for="item in documentAccessRequest.requests" :key="item.id">
                            <td>{{ dateTimeString(item.submissionDate) }}</td>
                            <td>{{ dateTimeString(item.expiryDate) }}</td>
                            <td>
                                <v-list class="py-0" density="compact">
                                    <v-list-item v-for="(document, index) in item.documents" :key="index">
                                        <span class="app-blue doc-link" @click="downloadDoc(document)">
                                            {{ documentDescription(document.documentType) }}
                                        </span>
                                    </v-list-item>
                                </v-list>
                            </td>
                        </tr>
                    </tbody>
                    <tbody v-else>
                        <tr>
                            <td colspan="6">
                                <p class="pt-4 pb-2"><b>No purchase history</b></p>
                            </td>
                        </tr>
                    </tbody>
                </v-table>
            </v-col>
        </v-row>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
// local
import { useDocumentAccessRequest, useEntity } from '@/composables'
import { dateToPacificDateTime } from '@/utils'

import { DocumentTypeDescriptions } from '@/resources'
import { DocumentI } from '@/interfaces'

// composables
const { documentAccessRequest, downloadDocument } = useDocumentAccessRequest()
const { entity } = useEntity()

const totalResultsLength = computed(() => documentAccessRequest.requests?.length || 0)

const dateTimeString = (val: string): string => {
    return (dateToPacificDateTime(new Date(val)) || 'Unknown')
}

const documentDescription = (type: string): string => {
    return DocumentTypeDescriptions[type]
}

const downloadDoc = (document: DocumentI): void => {
   downloadDocument(entity.identifier, document)
}

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

button {
    font-weight: normal !important;
}

td {
    font-size: 0.875rem !important;
    color: $gray7  !important;
}

th {
    font-size: 0.875rem !important;
    color: $gray9  !important;
}

.main-results-div {
    width: 100%;
}

.result-info {
    color: $gray7  !important;
    font-size: 1rem;
}

.primary-icon {
    color: $app-dk-blue  !important;
}

.table {
    max-width: calc(100% - 48px);
    max-height: calc(50vh - 85px);
}

.v-table {
    overflow: auto;
}

.v-table :deep(.v-table__wrapper) {
    overflow: unset;
}

.opaque-header {
    z-index: 1;
}

.doc-link{
    cursor: pointer;
}

.opaque-header {
  z-index: 1;
}
</style>
