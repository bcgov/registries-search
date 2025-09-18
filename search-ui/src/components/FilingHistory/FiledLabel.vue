<template>
    <div v-if="props.filing" class="filed-label d-inline">
        <span v-if="props.filing.isTypeStaff || filedOnLabel === 'Submitted'">
            {{ filedOnLabel }} on <DateTooltip :date="props.filing.submittedDate" />
        </span>
        <span v-else>
            ({{ filedOnLabel }} on <DateTooltip :date="props.filing.submittedDate" />)
        </span>
        <template v-if="!props.filing.isTypeStaff">
            <span class="vert-pipe" />
            <span>EFFECTIVE as of <DateTooltip :date="props.filing.effectiveDate" /></span>
        </template>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DateTooltip } from '@/components/common'
import { FilingTypes } from '@/enums'
import { FilingHistoryItem } from '@/types'

const props = defineProps<{ filing: FilingHistoryItem }>()
const filedOnLabel = computed(() => props.filing.name === ('changeOfOfficers' as FilingTypes) ? 'Submitted' : 'Filed')
</script>
