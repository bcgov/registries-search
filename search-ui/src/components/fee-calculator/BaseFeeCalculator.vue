<template>
  <aside id="fee-calculator" class="pl-5">
    <slot name="feeSummary">
      <fee-summary />
    </slot>
    <slot name="feeActions">
      <fee-actions :actions-list="feeActions" />
    </slot>
    <slot name="errorMessage">
      <div v-if="errorMessage" class="error-messages ml-n2 mt-2">
        &lt; {{ errorMessage }}
      </div>
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
  feeActions: null as PropType<FeeAction[][]>,
  errorMessage: { default: '' }
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
  top: 2.5rem;
}

.error-messages {
  color: #D3272C;
  font-size: 14px;
  text-align: center;
  width: 320px;
}
</style>