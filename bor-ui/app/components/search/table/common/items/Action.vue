<script setup lang="ts">
defineProps<{ showBtn: boolean, tooltipMsg: string }>()
const emit = defineEmits<{ (e: 'action', value: boolean): void }>()
</script>

<template>
  <div>
    <UButton
      v-if="showBtn"
      class="px-7 py-2"
      color="primary"
      label="Open"
      @click="emit('action', true)"
    />
    <UTooltip
      v-else
      arrow
      :delay-duration="200"
      :text="tooltipMsg"
      :content="{
        side: 'bottom',
      }"
      :ui="{
        content: 'max-w-xs *:text-wrap *:whitespace-normal h-20',
      }"
    >
      <div>
        <UIcon class="text-[24px] text-primary" name="i-mdi-information-outline" />
      </div>
    </UTooltip>
  </div>
</template>
