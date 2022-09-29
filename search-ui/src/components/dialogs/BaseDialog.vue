<template>
  <v-dialog class="base-dialog" :attach="attach" :model-value="display" persistent>
    <v-card v-if="options" class="px-10 py-9">
      <v-row no-gutters>
        <v-col :cols="options.hideClose ? '12' : '11'">
          <h2 class="base-dialog__title">{{ options.title }}</h2>
        </v-col>
        <v-col v-if="!options.hideClose" cols="1">
          <v-btn
            class="base-dialog__close-btn float-right"
            icon
            :ripple="false"
            @click="close()"
          >
            <v-icon siz="32">mdi-window-close</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <div class="pt-9">
        <!-- can be replaced with <template v-slot:content> -->
        <slot name="content" :options="options">
          <dialog-content
            class="base-dialog__text"
            :baseText="options.text"
            :extraText="options.textExtra"
          />
        </slot>
      </div>
      <slot name="extra-content" :options="options" />
      <div class="base-dialog__btn-container pt-7">
        <!-- can be replaced with <template v-slot:buttons> -->
        <slot name="buttons" :options="options">
          <v-row justify="center" no-gutters>
            <v-col v-for="button, i in options.buttons" :key="'dialog-btn-' + i" cols="auto">
              <slot :name="'dialog-btn-slot-' + button.slotId">
                <dialog-button class="base-dialog__btn" :button="button" @close="emit('close')" />
              </slot>
            </v-col>
          </v-row>
        </slot>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { DialogOptionsI } from '@/interfaces'
import { DialogButton, DialogContent } from './slot-templates'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  attach?: string,
  display: boolean,
  options: DialogOptionsI
}>()

const emit = defineEmits<{(e:'close'): void}>()

const close = () => {
  if (props.options.onClose && props.options.onCloseArgs) props.options.onClose(...props.options.onCloseArgs)
  else if (props.options.onClose) props.options.onClose()

  emit('close')
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.base-dialog {
  margin: auto;
  max-width: 720px;
  width: calc(100% - 50px) !important;

  &__title {
    color: $gray9;
    font-size: 1.5rem;
    line-height: 1.625rem;
  }

  &__text {
    color: $gray7;
    font-size: 1rem;
    line-height: 1.5rem;
  }

  &__close-btn {
    background-color: transparent !important;
    box-shadow: none;
    color: $primary-blue;
    height: 24px;
    width: 24px;
  }

  &__btn-container {
    :deep(.v-btn--size-default) { min-width: 100px;}
  }

  :deep(.v-overlay__content) { width: 100%; }
}
</style>
