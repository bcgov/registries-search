<template>
  <v-row v-for="actions, i in props.actionsList" :key="'fee-action-'+i" class="pt-4" no-gutters>
    <v-col v-for="item, i in actions" :key="'fee-action-item-'+i" cols="12" :md="actions.length > 1 ? '6' : '12'">
      <base-action :fee-action="item" />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { PropType } from 'vue'
// local
import { FeeAction } from '@/interfaces'
import { BaseAction } from '.'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  actionsList: null as PropType<FeeAction[][]>
})

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
