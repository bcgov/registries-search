<template>
    <div class="documents-list">
        <v-list class="py-0" density="compact">
            <v-list-item v-for="(document, index) in filteredDocuments" :key="index">
                <v-btn variant="text" class="download-one-btn" @click="downloadOne(document, index)"
                    :disabled="props.loadingOne || props.loadingAll || isLocked"
                    :loading="props.loadingOne && (index === props.loadingOneIndex)">
                    <v-tooltip v-if="isLocked" location="top" content-class="tooltip">
                        <template v-slot:activator="{ isActive, props }">
                            <div v-if="isActive" class="ml-4 top-tooltip-arrow"></div>
                            <v-icon v-bind="props">mdi-lock</v-icon>
                        </template>
                        <span>
                            Select Business Summary and Filing History Documents above 
                            and complete payment to access documents.
                        </span>
                    </v-tooltip>
                    <v-icon v-else class="app-blue">mdi-file-pdf-box</v-icon>
                    <span v-bind:class="[isLocked ? '' : 'app-blue']">{{ document.title }}</span>
                </v-btn>
            </v-list-item>

            <v-list-item v-if="filing.documents.length > 1">
                <v-btn variant="text" class="download-all-btn" @click="downloadAll()"
                    :disabled="props.loadingOne || props.loadingAll || isLocked" :loading="props.loadingAll">
                    <v-tooltip v-if="isLocked" location="top" content-class="tooltip">
                        <template v-slot:activator="{ isActive, props }">
                            <div v-if="isActive" class="ml-4 top-tooltip-arrow"></div>
                            <v-icon v-bind="props">mdi-lock</v-icon>
                        </template>
                        <span>
                            Select Business Summary and Filing History Documents above 
                            and complete payment to access documents.
                        </span>
                    </v-tooltip>
                    <v-icon class="app-blue" v-else>mdi-download</v-icon>
                    <span v-bind:class="[isLocked ? '' : 'app-blue']">Download All</span>
                </v-btn>
            </v-list-item>
        </v-list>
    </div>
</template>

<script setup lang="ts">
import { Document } from '@/types'
import { FilingHistoryItem } from '@/types'
import { computed, toRef } from 'vue'

const props = defineProps<{
    filing: FilingHistoryItem,
    loadingOne: boolean,
    loadingAll: boolean,
    loadingOneIndex: number
    isFilingLocked: boolean,
}>()

const emit = defineEmits(['downloadOne', 'downloadAll'])
const isLocked = toRef(props, 'isFilingLocked')

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
.v-list-item {
    padding-left: 0;
    min-height: 1rem;
}
</style>
