<script setup lang="ts">
defineProps<{
  title?: string
  content?: string
}>()
</script>

<template>
  <div>
    <strong v-if="title" class="tracking-wider text-[smaller] italic">
      {{ title }}
    </strong>
    <slot name="content">
      <p v-if="content" data-testid="content">
        {{ content }}
      </p>
    </slot>
  </div>
</template>
