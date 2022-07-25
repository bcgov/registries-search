<template>
  <v-row justify="center" no-gutters>
    <v-col v-if="cancelText" cols="auto">
      <v-btn id="cancel-btn" class="outlined dialog-btn" outlined @click="emit('proceed', false)">
        {{ cancelText }}
      </v-btn>
    </v-col>
    <v-col v-if="acceptText" :class="{ 'pl-3': cancelText }" cols="auto">
      <v-btn id="accept-btn" class="primary dialog-btn" @click="emit('proceed', true)">
        {{ acceptText }}
      </v-btn>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  acceptText?: string
  cancelText?: string
}>()

const emit = defineEmits<{(e: 'proceed', value: boolean): void}>()
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#accept-btn {
  font-weight: normal;
}
</style>
