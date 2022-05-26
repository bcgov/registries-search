<template>
    <div v-if="props.filing" class="staff-filing-details body-2">
        <p>{{ props.filing.notationOrOrder }}</p>

        <p class="mb-0" v-if="props.filing.fileNumber">Court Order Number: {{ props.filing.fileNumber }}</p>

        <p class="mt-0" v-if="props.filing.planOfArrangement">{{ props.filing.planOfArrangement }}</p>
    </div>
</template>

<script setup lang="ts">
import { FilingHistoryItem } from '@/types'

const props = defineProps<{ filing:FilingHistoryItem }>()
</script>

<style lang="scss" scoped>
p {
    margin-top: 1rem !important;
}
</style>
