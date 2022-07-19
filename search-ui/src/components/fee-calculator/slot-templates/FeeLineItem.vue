<template>
  <div v-if="lineItem || serviceFee" class="fee-list__item">
    <v-row v-if="!serviceFee" class="py-4" no-gutters>
      <v-col class="fee-list__item-name" cols="8">{{ lineItem.label }}</v-col>
      <v-col class="fee-list__item-value" align-self="end" v-html="displayFee(lineItem.fee, noFee)" />
    </v-row>
    <v-row v-else class="ml-3 py-4" no-gutters>
      <v-col class="fee-list__item-name">Service Fee</v-col>
      <v-col class="fee-list__item-value" v-html="displayFee(serviceFee, noFee)" />
    </v-row>
  </div>  
</template>

<script setup lang="ts">
import { PropType } from 'vue';
// local
import { useFeeCalculator } from '@/composables'
import { FeeI } from '@/interfaces';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  lineItem: null as PropType<FeeI>,
  noFee: Boolean,
  serviceFee: Number
})

const { displayFee } = useFeeCalculator()

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.fee-list__item {
  line-height: 1.2rem;
  font-size: 0.875rem;
  &-name, &-value {
    font-weight: 700;
  }

  &-name {
    margin-right: 2rem;
  }

  &-value {
    text-align: right;
  }
}

.fee-list__item + .fee-list__item {
  border-top: 1px solid $gray3;
}
</style>
