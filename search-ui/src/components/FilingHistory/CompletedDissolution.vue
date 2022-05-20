<template>
  <div v-if="props.filing" class="completed-dissolution-details body-2">
    <h4>Dissolution Complete</h4>

    <p>
      The {{entityTitle}} {{props.entityName || ''}} was successfully
      <strong>dissolved on {{dissolutionDateTime}}</strong>.
      The {{entityTitle}} has been struck from the register and dissolved,
      and ceased to be an incorporated {{entityTitle}}
      under the {{actTitle}}.
    </p>

    <p>
      <strong>You are required to retain a copy of all the dissolution documents
      in your records book.</strong>
    </p>
  </div>
</template>

<script setup lang="ts">
 import { FilingHistoryItem } from '@/types'
 import { dateToPacificDateTime } from '@/utils'
  
  const props = defineProps<{ filing:FilingHistoryItem, entityName: '', entityType: '' }>()

  /** The entity title to display. */
  const entityTitle = (): string => {
    return isCoop ? 'Cooperative Association' : 'Company'
  }

  /** The dissolution date-time to display. */
  const dissolutionDateTime = (): string => {
    return (dateToPacificDateTime(props.filing?.effectiveDate) || 'Unknown')
  }

  /** The act title to display. */
  const actTitle = (): string => {
    return isCoop ? 'Cooperative Association Act' : 'Business Corporations Act'
  }

  const isCoop = (): string => {
    return props.entityType === 'CP' ? 'Cooperative Association Act' : 'Business Corporations Act'
  }

</script>

<style lang="scss" scoped>
p {
  margin-top: 1rem !important;
}
</style>
