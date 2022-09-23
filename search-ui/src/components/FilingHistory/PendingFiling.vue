<template>
    <div v-if="props.filing" class="pending-filing-details body-2">
        <h4>Filing Pending</h4>

        <p>This {{ title() }} is paid, but the filing has not been completed by the Business Registry yet.
            Some filings may take longer than expected.</p>

        <p v-if="props.filing.courtOrderNumber">Court Order Number: {{ props.filing.courtOrderNumber }}</p>

        <p v-if="props.filing.isArrangement">Pursuant to a Plan of Arrangement</p>

        <p>If this issue persists, please contact us.</p>

        <ContactInfo class="mt-4" :contacts="RegistriesInfo" />
    </div>
</template>

<script setup lang="ts">
import { ContactInfo } from '@/components'
import { FilingHistoryItem } from '@/types'
import { FilingNames, FilingTypes } from '@/enums'
import { RegistriesInfo } from '@/resources/contact-info'

const props = defineProps<{ filing: FilingHistoryItem }>()

/** The title of the subject filing. */
const title = (): string => {
    if (isTypeAlteration(props.filing)) return FilingNames.ALTERATION
    if (props.filing.displayName) return props.filing.displayName
    return 'Filing'
}

/** Returns True if filing is an Alteration. */
const isTypeAlteration = (item: FilingHistoryItem): boolean => {
    return (item.name === FilingTypes.ALTERATION)
}
</script>

<style lang="scss" scoped>
p {
    margin-top: 1rem !important;
}
</style>
