<template>
    <div class="documents-list">
        <v-list class="py-0">
            <v-list-item v-for="(document, index) in props.filing.documents" :key="index">
                <v-btn text color="primary" class="download-one-btn" @click="downloadOne(document, index)"
                    :disabled="props.loadingOne || props.loadingAll"
                    :loading="props.loadingOne && (index === props.loadingOneIndex)">
                    <v-icon>mdi-file-pdf-outline</v-icon>
                    <span>{{ document.title }}</span>
                </v-btn>
            </v-list-item>

            <v-list-item v-if="filing.documents.length > 1">
                <v-btn text color="primary" class="download-all-btn" @click="downloadAll(filing)"
                    :disabled="props.loadingOne || props.loadingAll" :loading="props.loadingAll">
                    <v-icon>mdi-download</v-icon>
                    <span>Download All</span>
                </v-btn>
            </v-list-item>
        </v-list>
    </div>
</template>

<script setup lang="ts">
import { Document } from '@/types'
import { FilingHistoryItem } from '@/types'

const props = defineProps<{
    filing?: {} & FilingHistoryItem,
    loadingOne: boolean,
    loadingAll: boolean,
    loadingOneIndex: Number
}>()

const emit = defineEmits(['downloadOne', 'downloadAll'])


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
    min-height: 1.5rem;
}
</style>
