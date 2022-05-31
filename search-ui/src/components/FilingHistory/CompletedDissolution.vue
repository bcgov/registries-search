<template>
  <div v-if="props.filing" class="completed-dissolution-details body-2">
    <h4>Dissolution Complete</h4>

    <p>
      The {{ entityTitle }} {{ entity.name || '' }} was successfully
      <strong>dissolved on {{ dissolutionDateTime }}</strong>.
      The {{ entityTitle }} has been struck from the register and dissolved,
      and ceased to be an incorporated {{ entityTitle }}
      under the {{ actTitle }}.
    </p>

    <p>
      <strong>You are required to retain a copy of all the dissolution documents
        in your records book.</strong>
    </p>
  </div>
</template>

<script setup lang="ts">
import { useEntity } from '@/composables'
import { FilingHistoryItem } from '@/types'
import { dateToPacificDateTime } from '@/utils'
import { computed } from '@vue/reactivity'

const props = defineProps<{ filing: FilingHistoryItem }>()
const { entity, entityTitle, actTitle } = useEntity()


/** The dissolution date-time to display. */
const dissolutionDateTime = computed((): string => {
  return (dateToPacificDateTime(props.filing?.effectiveDate) || 'Unknown')
})

</script>

<style lang="scss" scoped>
p {
  margin-top: 1rem !important;
}
</style>
