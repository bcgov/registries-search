<template>
  <!-- NB: set icon="null" to prevent v-alert default icon + vue complains if set to "" -->
  <v-alert
    v-model="show"
    class="py-2"
    :type="type"
    icon="null"
    :dismissible="dismissible"
    data-cy="bcros-banner"
  >
    <div class="container px-4 ma-auto">
      <v-icon v-if="icon !== ''" class="mr-2" size="34">
        {{ icon }}
      </v-icon>
      <span v-html="message" />
    </div>
  </v-alert>
</template>

<script setup lang="ts">
const props = defineProps({
  dismissible: { type: Boolean, default: false },
  icon: { type: String, default: 'mdi-information' }, // See https://material.io/resources/icons/?style=baseline for accepted values
  message: { type: String, default: '' },
  setShow: { type: Boolean, default: false },
  type: { type: String, default: 'warning' }
})

const show = computed(() => props.setShow)
</script>

<style lang="scss" scoped>
.v-alert {
  display: flex;
  border-radius: 0;
  padding: 0;
  max-height: 48px;
}
:deep(.v-alert__prepend) {
  height: 0;
  width: 0;
  margin-inline-end: 0;
}

.v-alert :deep(.v-alert__wrapper) {
  margin: 0;
  overflow: hidden;
}

:deep(.v-alert__content) {
  max-width: 1360px;  // should match sbc header / breadcrumb max widths
  width: 100%;
}
</style>
