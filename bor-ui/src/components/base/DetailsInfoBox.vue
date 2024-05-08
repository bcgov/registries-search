<template>
  <div>
    <p v-if="title" class="title">
      {{ title }}
    </p>
    <p v-if="content" data-cy="content">
      {{ content }}
    </p>
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
  letter-spacing: 0.05rem;
  font-weight: bold;
  font-size: smaller;
  font-style: italic;
}
</style>
