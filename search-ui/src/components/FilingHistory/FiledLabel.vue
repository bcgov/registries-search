<template>
    <div v-if="props.filing" class="filed-label d-inline">
        <template v-if="props.filing.isTypeStaff">
            <span>Filed on
                <DateTooltip :date="props.filing.submittedDate" />
            </span>
        </template>

        <template v-else>
            <span> (Filed on
                <DateTooltip :date="props.filing.submittedDate" />)
            </span>
            <span class="vert-pipe" />
            <span>EFFECTIVE as of
                <DateTooltip :date="props.filing.effectiveDate" />
            </span>
        </template>
    </div>
</template>

<script setup lang="ts">

import { DateTooltip } from '@/components/common'
import { FilingHistoryItem } from '@/types'

const props = defineProps<{ filing: FilingHistoryItem }>()
</script>
