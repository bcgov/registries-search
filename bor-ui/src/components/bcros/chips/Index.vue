<template>
  <div
    class="grid grid-flow-col gap-1 py-1 px-3 rounded bg-primary text-white"
    data-cy="bcrosChip"
  >
    <slot name="col-span-4">
      <span class="align-middle text-[10px] leading-tight p-0 uppercase">
        {{ label }}
      </span>
    </slot>
    <div v-if="hasClose" class="float-right">
      <slot name="icon">
        <span class="h-full w-full">
          <UIcon
            name="i-mdi-close font-bold align-middle"
            data-cy="close-icon"
            @click.stop.prevent="$emit('chipCloseClicked')"
          />
        </span>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<(e: 'chipCloseClicked') => void>()
defineProps({
  label: { type: String, required: true },
  hasClose: { type: Boolean, default: false }
})
</script>
