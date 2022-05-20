<template>
  <v-tooltip transition="fade-transition" right>
    <template v-slot:activator="{ props }">
      <div v-bind="props" v-on="props" class="date-tooltip d-inline cursor-default">
        <span class="dotted-underline">{{dateString()}}</span>
      </div>
    </template>
    {{dateTimeString()}}
  </v-tooltip>
</template>

<script setup lang="ts">
import { dateToPacificDate, dateToPacificDateTime } from '@/utils'

const props = defineProps<{ date: Date }>()


const dateString = (): string => {
  return (dateToPacificDate(props.date) || 'Unknown')
}

const dateTimeString = (): string => {
  return (dateToPacificDateTime(props.date) || 'Unknown')
}
</script> 
