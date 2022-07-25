<template>
  <v-dialog class="base-dialog" :attach="attach" :model-value="display" persistent>
    <v-card v-if="options" class="px-10 py-9">
      <v-row no-gutters>
        <v-col cols="11">
          <h2 class="dialog-title">{{ options.title }}</h2>
        </v-col>
        <v-col cols="1">
          <v-btn
            class="close-btn float-right"
            icon
            :ripple="false"
            @click="emit('proceed', false)"
          >
            <v-icon siz="32">mdi-window-close</v-icon>
          </v-btn>
        </v-col>
      </v-row>
      <div class="pt-9">
        <!-- can be replaced with <template v-slot:content> -->
        <slot name="content">
          <dialog-content
            :setBaseText="options.text"
            :setExtraText="options.textExtra"
          />
        </slot>
      </div>
      <div class="pt-7">
        <!-- can be replaced with <template v-slot:buttons> -->
        <slot name="buttons">
          <dialog-buttons
            :acceptText="options.acceptText"
            :cancelText="options.cancelText"
            @proceed="emit('proceed', $event)"
          />
        </slot>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { DialogOptionsIF } from '@/interfaces'
import { DialogButtons, DialogContent } from './slot-templates'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  attach: { default: '' },
  display: { default: false },
  options: Object as () => DialogOptionsIF
})

const emit = defineEmits<{(e:'proceed', value: boolean): void}>()
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.base-dialog {
  margin: auto;
  max-width: 720px;
  width: calc(100% - 50px) !important;
}
.close-btn, .close-btn:hover, .close-btn::before {
  background-color: transparent !important;
  box-shadow: none;
  color: $primary-blue;
  height: 24px;
  width: 24px;
}
</style>
