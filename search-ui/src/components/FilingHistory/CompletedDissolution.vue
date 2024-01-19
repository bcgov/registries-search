<template>
  <div v-if="props.filing" class="completed-dissolution-details body-2">
    <h4>Dissolution Complete</h4>

    <p>
      The {{ dissolutionText1 }} {{ entity.name || '' }} was successfully
      <strong>{{ dissolutionText2 }}</strong><span v-if="isFirm"> with dissolution date of
      <strong>{{ dissolutionDate }}</strong></span>. {{ dissolutionText3 }}
      has been struck from the register and dissolved, and ceased to be
      {{ dissolutionText4 }} under the {{ actTitle }}.
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
import { dateToPacificDate, dateToPacificDateTime } from '@/utils'
import { computed } from '@vue/reactivity'

const props = defineProps<{ filing: FilingHistoryItem }>()
const { entity, entityTitle, actTitle, isFirm, getEntityDescription } = useEntity()

/** The dissolution date to display. */
const dissolutionDate = computed((): string => {
  console.log(props.filing)
  if (props.filing?.data?.dissolution?.dissolutionDate) {
    return dateToPacificDate(
      new Date(props.filing.data.dissolution.dissolutionDate + 'T16:00:00')
    )
  }
  return (dateToPacificDate(props.filing?.effectiveDate, true) || 'Unknown')
})

/** The dissolution date-time to display. */
const dissolutionDateTime = computed((): string => {
  return (dateToPacificDateTime(props.filing?.effectiveDate) || 'Unknown')
})

/** The dissolution submitted date-time to display. */
const dissolutionSubmittedDateTime = computed((): string => {
  return (dateToPacificDateTime(props.filing?.submittedDate) || 'Unknown')
})

const getFirmDesc = () => {
  return getEntityDescription(entity.legalType).replace('BC ', '')
}

/** The dissolution text to display */
const dissolutionText1 = computed((): string => {
  if (isFirm.value) {
    return `statement of dissolution for ${getFirmDesc()}`
  }
  return entityTitle.value
})

const dissolutionText2 = computed((): string => {
  if (isFirm.value) {
    return `submitted on ${dissolutionSubmittedDateTime.value}`
  }
  return `dissolved on ${dissolutionDateTime.value}`
})

const dissolutionText3 = computed((): string => {
  if (isFirm.value) {
    return `The ${getFirmDesc()}`
  }
  return `The ${entityTitle.value}`
})

const dissolutionText4 = computed((): string => {
  if (isFirm.value) {
    return `a registered ${getFirmDesc()}`
  }
  return `an incorporated ${entityTitle.value}`
})

</script>

<style lang="scss" scoped>
p {
  margin-top: 1rem !important;
}
</style>
