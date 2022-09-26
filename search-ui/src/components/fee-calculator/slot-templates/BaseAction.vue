<template>
  <v-btn
    v-if="feeAction.compType === ActionComps.BUTTON"
    :class="feeAction.outlined ? 'btn-stacked__outlined' : 'btn-stacked'"
    :disabled="feeAction.disabled?.value"
    @click="feeAction.action()"
  >
    <v-icon v-if="feeAction.iconLeft" class="btn-stacked__icon">{{ feeAction.iconLeft }}</v-icon>
    {{ feeAction.text }}
    <v-icon v-if="feeAction.iconRight" class="btn-stacked__icon">{{ feeAction.iconRight }}</v-icon>
  </v-btn>
  <v-text-field 
    v-else-if="feeAction.compType === ActionComps.TEXTFIELD"
    filled
    hide-details
    :label="feeAction.text"
    @update:model-value="feeAction.action($event)"
  />
</template>

<script setup lang="ts">
import { PropType } from 'vue'
// local
import { ActionComps } from '@/enums'
import { FeeAction } from '@/interfaces';

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  feeAction: null as PropType<FeeAction>
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.btn-stacked {
  background-color: $primary-blue;
  box-shadow: none;
  color: white;
  font-size: 14px;
  font-weight: 700;
  width: 100%;
  &__outlined {
    background-color: transparent !important;
    border: 1px solid $primary-blue !important;
    box-shadow: none;
    color: $primary-blue; 
    font-size: 14px;    
    width: 100%;
  }
  &__icon {
    color: inherit;
    padding-top: 2px;
  }
}
:deep(.v-label.v-field-label) {
  color: $gray7;
  font-weight: normal;
}
:deep(.v-field .v-field__overlay) {
  background-color: white;
}
</style>
