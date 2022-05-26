<template>
  <aside id="fee-calculator" class="pl-5">
    <slot name="feeSummary">
      <fee-summary />
    </slot>
    <slot name="feeActions">
      <fee-actions :actions-list="feeActions" />
    </slot>
  </aside>
</template>

<script setup lang="ts">
import { onMounted, PropType } from 'vue'
// Local
import { useFeeCalculator } from '@/composables'
import { FeeAction, FeeI } from '@/interfaces'
import { FeeSummary, FeeActions } from './slot-templates'

const props = defineProps({
  preSelectItem: null as PropType<FeeI>,
  feeActions: null as PropType<FeeAction[][]>
})

const { fees } = useFeeCalculator()

onMounted(() => {
  fees.preSelection = props.preSelectItem
})
</script>
<style lang="scss" scoped>
#fee-calculator {
  width: 320px;
  position: sticky;
  top: 2rem;
}
</style>