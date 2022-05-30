<template>
    <div v-if="props.filing" class="completed-alteration-details body-2">
        <h4>Alteration Complete</h4>

        <p v-if="props.filing.toLegalType !== props.filing.fromLegalType">
            {{ props.entityName || 'This company' }} was successfully altered
            from a {{ fromLegalType }} to a {{ toLegalType }}
            on <DateTooltip :date="props.filing.effectiveDate" />.
        </p>

        <p v-if="props.filing.courtOrderNumber" class="mb-0">Court Order Number: {{ props.filing.courtOrderNumber }}</p>

        <p v-if="props.filing.isArrangement" class="mt-0">Pursuant to a Plan of Arrangement</p>
    </div>
</template>

<script setup lang="ts">
import DateTooltip from '@/components/common/DateTooltip.vue'
import { FilingHistoryItem } from '@/types'
import { GetCorpFullDescription } from '@bcrs-shared-components/corp-type-module'
import { computed } from '@vue/reactivity'


const props = defineProps<{ filing: FilingHistoryItem, entityName: string }>()

const fromLegalType = computed((): string => {
    return GetCorpFullDescription(props.filing?.fromLegalType)
})

const toLegalType = computed((): string => {
    return GetCorpFullDescription(props.filing?.toLegalType)
})
</script>

<style lang="scss" scoped>
p {
    margin-top: 1rem !important;
}
</style>
