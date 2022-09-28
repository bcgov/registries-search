<template>
    <div v-if="props.filing" class="future-effective-details body-2">
        <h4>{{ future_effective_title.subtitle }}</h4>

        <p>
            The {{ future_effective_title.filingLabel }} date and time for {{ props.entityName || 'this company' }}
            will be <strong>{{ effectiveDateTime() }}</strong>.
        </p>

        <p v-if="props.filing.courtOrderNumber">Court Order Number: {{ props.filing.courtOrderNumber }}</p>

        <p v-if="props.filing.isArrangement">Pursuant to a Plan of Arrangement</p>

        <p>
            If you wish to change the information in this {{ future_effective_title.filingLabel }}, you must contact BC
            Registries staff to file a withdrawal. Withdrawing this {{ future_effective_title.filingTitle }} will remove
            this {{ future_effective_title.filingLabel }} and all associated information, and will incur a $20.00 fee.
        </p>

        <h4 class="font-14">BC Registries Contact Information:</h4>

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
    if (props.filing.isFutureEffectiveIa) {
        return {
            subtitle: 'Future Effective Incorporation Date',
            filingLabel: 'incorporation',
            filingTitle: 'Incorporation Application'
        }
    }
    if (props.filing.isFutureEffectiveAlteration) {
        return {
            subtitle: 'Future Effective Alteration Date',
            filingLabel: 'alteration',
            filingTitle: 'Alteration Notice'
        }
    }
    return {
        subtitle: 'Future Effective Filing Date',
        filingLabel: 'filing',
        filingTitle: 'filing'
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
