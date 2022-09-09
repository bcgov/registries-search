<template>
    <div class="documents-list">
        <v-list class="py-0" density="compact">
            <v-list-item v-for="(document, index) in filteredDocuments" :key="index">
                <v-btn variant="text" class="download-one-btn" @click="downloadOne(document, index)"
                    :disabled="props.loadingOne || props.loadingAll || isLocked">
                    <v-tooltip v-if="isLocked" location="top" content-class="tooltip">
                        <template v-slot:activator="{ isActive, props }">
                            <div v-if="isActive" class="ml-4 top-tooltip-arrow doc-tooltip-arrow"></div>
                            <v-icon v-bind="props" color="#495057">mdi-file-lock</v-icon>
                            <span v-bind="props" class="doc-title">{{ document.title }}</span>
                        </template>
                        <span>
                            Select Business Summary and Filing History Documents above 
                            and complete payment to access documents.
                        </span>
                    </v-tooltip>
                    <div v-else>
                        <img class="mb-n1" :src="require('@/assets/svgs/pdf-icon-blue.svg')" />
                        <span class="app-blue ml-1">{{ document.title }}</span>
                    </div>
                </v-btn>
            </v-list-item>

            <v-list-item v-if="filing.documents.length > 1">
                <v-btn variant="text" class="download-all-btn" @click="downloadAll()"
                    :disabled="props.loadingOne || props.loadingAll || isLocked">
                    <v-tooltip v-if="isLocked" location="top" content-class="tooltip">
                        <template v-slot:activator="{ isActive, props }">
                            <div v-if="isActive" class="ml-4 top-tooltip-arrow doc-tooltip-arrow"></div>
                            <v-icon v-bind="props" color="#495057">mdi-file-lock</v-icon>
                            <span v-bind="props" class="doc-title">Download All</span>
                        </template>
                        <span>
                            Select Business Summary and Filing History Documents above 
                            and complete payment to access documents.
                        </span>
                    </v-tooltip>
                    <div v-else>
                        <v-icon class="app-blue">mdi-download</v-icon>
                        <span class="app-blue" style="margin-left: 2px;">Download All</span>
                    </div>
                </v-btn>
            </v-list-item>
        </v-list>
    </div>
</template>

<script setup lang="ts">
import { Document } from '@/types'
import { FilingHistoryItem } from '@/types'
import { computed } from 'vue'

const props = defineProps<{
    filing: FilingHistoryItem,
    loadingOne: boolean,
    loadingAll: boolean,
    loadingOneIndex: number,
    isLocked: boolean,
}>()

const emit = defineEmits(['downloadOne', 'downloadAll'])

const filteredDocuments = computed(() => props.filing.documents.filter(document =>
    (document.title.toLowerCase() != 'receipt')))

/** Emits an event to download the subject document. */
const downloadOne = (document: Document, index: number): void => {
    emit('downloadOne', {
        'filing': props.filing,
        'document': document,
        'index': index
    })
}

/** Emits an event to download all. */
const downloadAll = (): void => {
    emit('downloadAll', {        
        'filing': props.filing
    })
}
</script>

<style lang="scss" scoped>
.doc-title {
    margin-left: 0 !important;
    padding-left: 0.25rem;
    overflow-y: visible;
    text-align: start;
    width: 100px;
    color: #495057;
}
.doc-tooltip-arrow {
    margin-top: -31px !important;
}
.v-list-item {
    padding-left: 0;
    min-height: 1rem;
}
</style>
