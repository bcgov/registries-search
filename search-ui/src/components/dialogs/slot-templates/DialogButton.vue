<template>
  <v-btn
    :class="[button.outlined ? 'btn-basic-outlined' : 'btn-basic', button.class || '']"
    :color="button.color ? button.color : ''"
    @click="handleClick()"
  >
    {{ button.text }}
  </v-btn>
</template>

<script setup lang="ts">
import { DialogButtonI } from '@/interfaces'

const props = defineProps<{ button: DialogButtonI }>()
const emit = defineEmits<{(e:'close'): void}>()

const handleClick = () => {
  if (props.button.onClick && props.button.onClickArgs) props.button.onClick(...props.button.onClickArgs)
  else if (props.button.onClick) props.button.onClick()

  if (props.button.onClickClose) emit('close')
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>
