<template>
  <UModal
    :attach="attach || ''"
    :model-value="display"
    data-cy="base-dialog"
  >
    <div v-if="options" class="px-10 py-9">
      <div class="flex">
        <div class="grow">
          <h1 data-cy="base-dialog-title">
            {{ options.title }}
          </h1>
        </div>
        <UButton
          v-if="!options.hideClose"
          color="primary"
          icon="i-heroicons-x-mark-20-solid"
          variant="ghost"
          data-cy="base-dialog-close-btn"
          @click="close()"
        />
      </div>
      <div class="pt-9" data-cy="base-dialog-text">
        <!-- can be replaced with <template v-slot:content> -->
        <slot name="content" :options="options">
          <dialog-content
            :base-text="options.text"
            :extra-text="options.textExtra"
          />
        </slot>
      </div>
      <slot name="extra-content" :options="options" />
      <div class="pt-7">
        <!-- can be replaced with <template v-slot:buttons> -->
        <slot name="buttons" :options="options">
          <div class="flex justify-center">
            <div v-for="button, i in options.buttons" :key="'dialog-btn-' + i">
              <slot :name="'dialog-btn-slot-' + button.slotId">
                <dialog-button :button="button" data-cy="base-dialog-btn" @close="emit('close')" />
              </slot>
            </div>
          </div>
        </slot>
      </div>
    </div>
  </UModal>
</template>

<script setup lang="ts">
import { DialogButton, DialogContent } from './slot-templates'

const props = defineProps<{
  attach?: string,
  display: boolean,
  options: DialogOptionsI | null
}>()

const emit = defineEmits<{(e:'close'): void}>()

const close = () => {
  if (props.options?.onClose && props.options.onCloseArgs) {
    props.options.onClose(...props.options.onCloseArgs)
  } else if (props.options?.onClose) {
    props.options.onClose()
  }

  emit('close')
}
</script>
