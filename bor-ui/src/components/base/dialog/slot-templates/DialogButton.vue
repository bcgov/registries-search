<template>
  <UButton
    :class="['px-10 py-2', button.class || '']"
    :color="button.color ? button.color : 'primary'"
    :label="button.text"
    @click="handleClick()"
  />
</template>

<script setup lang="ts">
const props = defineProps<{ button: DialogButtonI }>()
const emit = defineEmits<{(e:'close'): void}>()

const handleClick = () => {
  if (props.button.onClick && props.button.onClickArgs) {
    props.button.onClick(...props.button.onClickArgs)
  } else if (props.button.onClick) {
    props.button.onClick()
  }

  if (props.button.onClickClose) { emit('close') }
}
</script>
