<template>
  <div>
    <strong v-if="title" class="title">
      {{ title }}
    </strong>
    <slot name="content">
      <p v-if="content" data-cy="content">
        {{ content }}
      </p>
    </slot>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  content?: string
}>()
</script>

<style lang="scss" scoped>
.title {
  @apply tracking-wider font-bold text-[smaller] italic;
}
</style>
