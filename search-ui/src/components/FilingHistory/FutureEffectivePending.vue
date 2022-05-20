<template>
    <div v-if="props.filing" class="future-effective-pending-details body-2">
        <h4>{{ _.subtitle }}</h4>

        <p>
            The {{ _.filingLabel }} date and time for {{ props.entityName || 'this company' }}
            has been recorded as <strong>{{ effectiveDateTime }}</strong>.
        </p>

        <p v-if="filing.courtOrderNumber">Court Order Number: {{ filing.courtOrderNumber }}</p>

        <p v-if="filing.isArrangement">Pursuant to a Plan of Arrangement</p>

        <p>
            It may take up to one hour to process this filing. If this issue persists,
            please contact us.
        </p>

        <ContactInfo class="mt-4" />
    </div>
</template>

<script setup lang="ts">
import { ContactInfo } from '@/components/common'
import { FilingHistoryItem } from '@/types'
import { dateToPacificDateTime } from '@/utils'

const props = defineProps<{ filing: FilingHistoryItem, entityName: string }>()

/** Data for the subject filing. */
const _ = (): any => {
    if (props.filing.isFutureEffectiveIaPending) {
        return {
            subtitle: 'Incorporation Pending',
            filingLabel: 'incorporation'
        }
    }
    if (props.filing.isFutureEffectiveAlterationPending) {
        return {
            subtitle: 'Alteration Pending',
            filingLabel: 'alteration'
        }
    }
    return {
        subtitle: 'Filing Pending',
        filingLabel: 'filing'
    }
}

/** The future effective datetime of the subject filing. */
const effectiveDateTime = (): string => {
    return (dateToPacificDateTime(props.filing.effectiveDate) || 'Unknown')
}

</script>

<style lang="scss" scoped>
p {
    margin-top: 1rem !important;
}
</style>
