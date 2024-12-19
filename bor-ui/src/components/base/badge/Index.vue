<script setup lang="ts">
  type Props = {
    text: string,
    textColor?: string,
    color: string
  }

const props = withDefaults(defineProps<Props>(), {
  textColor: 'white'
})

const bgColor = computed(() => props.color)
</script>

<template>
  <UBadge
    :ui="{
      variant: {
        solid: `bg-${bgColor} dark:bg-${bgColor}`
      }
    }"
  >
    <span :class="`${textColor} uppercase`">{{ text }}</span>
  </UBadge>
</template>
