<template>
    <div class="documents-list">
        <v-list class="py-0" density="compact">
            <v-list-item v-for="(document, index) in filteredDocuments" :key="index">
                <v-btn variant="text" class="download-one-btn" @click="downloadOne(document, index)"
                    :disabled="props.loadingOne || props.loadingAll || props.isLocked"
                    :loading="props.loadingOne && (index === props.loadingOneIndex)">
                    <v-icon v-if="props.isLocked">mdi-lock</v-icon>
                    <v-icon v-else class="app-blue">mdi-file-pdf-box</v-icon>
                    <span v-bind:class="[props.isLocked ? '' : 'app-blue']">{{ document.title }}</span>
                </v-btn>
            </v-list-item>

            <v-list-item v-if="filing.documents.length > 1" >
                <v-btn variant="text" class="download-all-btn" @click="downloadAll(filing)"
                    :disabled="props.loadingOne || props.loadingAll || props.isLocked" :loading="props.loadingAll">
                    <v-icon v-if="props.isLocked">mdi-lock</v-icon>
                    <v-icon class="app-blue" v-else>mdi-download</v-icon>
                    <span v-bind:class="[props.isLocked ? '' : 'app-blue']">Download All</span>
                </v-btn>
            </v-list-item>
        </v-list>
    </div>
</template>

<script setup lang="ts">
import { Document } from '@/types'
import { FilingHistoryItem } from '@/types'
import {computed} from 'vue'

const props = defineProps<{
    filing: FilingHistoryItem,
    loadingOne: boolean,
    loadingAll: boolean,
    loadingOneIndex: number,
    isLocked: boolean
}>()

const emit = defineEmits(['downloadOne', 'downloadAll'])

const filteredDocuments = computed(() => props.filing.documents.filter(document => (document.title.toLowerCase() != 'receipt')))

/** Emits an event to download the subject document. */
const downloadOne = (document: Document, index: number): void => {
    emit('downloadOne', {
        'document': document,
        'index': index
    })
}

/** Emits an event to download all. */
const downloadAll = (filing: any): void => {
    emit('downloadAll')
}

</script>

<style lang="scss" scoped>
.v-list-item {
    padding-left: 0;
    min-height: 1rem;
}
</style>
