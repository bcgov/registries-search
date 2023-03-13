<template>
    <div class="documents-list">
        <v-list class="py-0" density="compact">
            <v-list-item v-for="(document, index) in filteredDocuments" :key="index">
                <v-btn variant="text" class="download-one-btn" @click="downloadOne(document, index)"
                    :disabled="props.loadingOne || props.loadingAll || isLocked">
                    <v-tooltip v-if="isLocked" location="top" content-class="bottom-arrow" transition="fade-transition">
                        <template v-slot:activator="{ props }">
                            <img :src="require('@/assets/svgs/pdf-locked-gray.svg')" />
                            <span v-bind="props" class="doc-title doc-title__disabled pl-2">{{ document.title }}</span>
                        </template>
                        <span>
                            Select Business Summary and Filing History Documents above 
                            and complete payment to access documents.
                        </span>
                    </v-tooltip>
                    <div v-else>                        
                        <img :src="require('@/assets/svgs/pdf-icon-blue.svg')" />
                        <span class="app-blue doc-title pl-2 doc-title-active">{{ document.title }}</span>
                    </div>
                </v-btn>
            </v-list-item>

            <v-list-item v-if="filing.documents.length > 1">
                <v-btn variant="text" class="download-all-btn" @click="downloadAll()"
                    :disabled="props.loadingOne || props.loadingAll || isLocked">
                    <v-tooltip v-if="isLocked" location="top" content-class="bottom-arrow" transition="fade-transition">
                        <template v-slot:activator="{ props }">
                            <img :src="require('@/assets/svgs/download-all-locked-gray.svg')" />
                            <span v-bind="props" class="doc-title doc-title__disabled pl-2">Download All</span>
                        </template>
                        <span>
                            Select Business Summary and Filing History Documents above 
                            and complete payment to access documents.
                        </span>
                    </v-tooltip>
                    <div v-else>
                        <v-icon class="app-blue download-all-active">mdi-download</v-icon>
                        <span class="app-blue doc-title pl-2">Download All</span>
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
@import '@/assets/styles/theme.scss';
.doc-title {
    margin-left: 0 !important;     
    overflow-y: visible;
    text-align: start;
    width: 100px;  
    font-size: 14px;

    &__disabled {
        color: $gray7;
    }
}
.doc-tooltip-arrow {
    margin-top: -31px !important;
}
.v-list-item {
  min-height: 1rem;
  padding-left: 0;
} 
.v-list-item:hover {
  background-color: white !important;
}
.download-all-active {
    margin-left: -5px;
}

.doc-title-active{
   vertical-align: top;
   padding-top:2px
}
.download-one-btn,
.download-all-btn {
  opacity: 1;
}
</style>
