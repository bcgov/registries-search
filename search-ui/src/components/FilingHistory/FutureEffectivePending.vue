<template>
    <div v-if="props.filing" class="future-effective-pending-details body-2">
        <h4>{{ future_effective_title.subtitle }}</h4>

        <p>
            The {{ future_effective_title.filingLabel }} date and time for {{ props.entityName || 'this company' }}
            has been recorded as <strong>{{ effectiveDateTime() }}</strong>.
        </p>

        <p v-if="filing.courtOrderNumber">Court Order Number: {{ filing.courtOrderNumber }}</p>

        <p v-if="filing.isArrangement">Pursuant to a Plan of Arrangement</p>

        <p>
            It may take up to one hour to process this filing. If this issue persists,
            please contact us.
        </p>

        <ContactInfo class="mt-4" :contacts="RegistriesInfo" />
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
// local
import { ContactInfo } from '@/components/common'
import { RegistriesInfo } from '@/resources/contact-info'
import { FilingHistoryItem } from '@/types'
import { dateToPacificDateTime } from '@/utils'

const props = defineProps<{ filing: FilingHistoryItem, entityName: string }>()

/** Data for the subject filing. */
const future_effective_title = computed((): any => {
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
})

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
