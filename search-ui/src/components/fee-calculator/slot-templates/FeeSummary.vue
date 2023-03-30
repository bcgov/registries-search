<template>
  <v-card>
    <header class="font-weight-bold px-3 py-3">
      <slot name="header">Fee Summary</slot>
    </header>

    <div v-if="fees._error">
      <slot name="feeError">
        <v-alert color="error" icon="warning" outlined>{{ fees._error.message }}</v-alert>
      </slot>
    </div>
    <v-slide-y-transition v-if="!fees._error" class="fee-list px-3">
      <div>
        <slot v-if="fees.items.length === 0 && fees.preSelection" name="preSelection">
          <fee-line-item :line-item="fees.preSelection" :no-fee="false" />
          <fee-line-item :no-fee="false" :service-fee="fees.preSelection.serviceFee" />
        </slot>
        <slot v-for="lineItem, i in fees.items" :key="`${lineItem.code}-${i}`" name="lineItem">
          <fee-line-item :line-item="lineItem" no-fee />
        </slot>
        <slot name="serviceFee" :fees="fees">
          <fee-line-item no-fee :service-fee="totalServiceFee" />
        </slot>
      </div>
    </v-slide-y-transition>

    <v-row v-if="!fees._error" class="fee-total py-6 px-3" no-gutters>
      <v-col class="fee-total__name" cols="8">Total Fees</v-col>
      <v-col class="fee-total__currency">CAD</v-col>
      <v-col class="fee-total__value" cols="auto" align-self="end">
        <v-slide-y-reverse-transition name="slide" mode="out-in">
          <div v-html="displayFee(totalFees, false, fees.items.length > 0)" />
        </v-slide-y-reverse-transition>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup lang="ts">
import { useFeeCalculator } from '@/composables'
import { FeeLineItem } from '.'

const { fees, displayFee, totalFees, totalServiceFee } = useFeeCalculator()
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

header {
  color: #fff;
  background: $BCgovBlue5;
}

.fee-list {
  border-bottom: 1px solid $gray3;
}

.fee-total {
  flex-flow: row nowrap;
  line-height: 1.2rem;
  font-size: 0.875rem;
  letter-spacing: -0.01rem;

  &__name {
    flex: 1 1 auto;
    margin-right: auto;
    font-weight: 700;
  }

  &__currency {
    margin-right: 0.5rem;
    color: $gray5;
    font-weight: 500;
  }

  &__value {
    font-size: 1.65rem;
    font-weight: 700;
  }
}
</style>
