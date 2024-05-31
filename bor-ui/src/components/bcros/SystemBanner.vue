<template>
  <UAlert
    v-show="!!message && !close"
    class="border-b-2 border-yellow-400"
    color="yellow"
    :description="message"
    variant="solid"
    :close-button="{ class: 'pr-2 text-gray-900' }"
    :ui="{ rounded: 'rounded-none', padding: 'p-0' }"
    @close="close = true"
  >
    <template #icon>
      <!-- NB: needed due to icon sizing via app.config / ui config for alert is not getting applied -->
      <UIcon class="ml-[-2px] text-[34px]" :name="icon" />
    </template>
  </UAlert>
</template>

<script setup lang="ts">
defineProps({
  dismissible: { type: Boolean, default: false },
  icon: { type: String, default: 'i-mdi-information' },
  message: { type: String, default: '' }
})
const close = ref(false)
</script>
