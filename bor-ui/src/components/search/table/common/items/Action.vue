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
      :text="tooltipMsg"
      :popper="{
        placement: 'bottom',
        arrow: true
      }"
      :ui="{
        width: 'max-w-xs',
        base: 'whitespace-normal'
      }"
    >
      <div>
        <UIcon class="text-[24px] text-primary-500" name="i-mdi-information-outline" />
      </div>
    </UTooltip>
  </div>
</template>
<script setup lang="ts">

defineProps<{ showBtn: boolean, tooltipMsg: string }>()
const emit = defineEmits<{(e: 'action', value: boolean): void }>()

</script>
