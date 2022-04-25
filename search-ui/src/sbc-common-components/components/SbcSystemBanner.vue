<template>
  <v-alert tile v-model="show" :type="type" :icon="icon" :dismissible="dismissible">
    <span v-html="message"></span>
  </v-alert>
</template>

<script lang="ts">
// External
import { computed, defineComponent, reactive } from 'vue'

export default defineComponent({
  name: 'SbcSystemBanner',
  props: {
    setDismissible: { default: false },
    setIcon: { default: 'mdi-information' }, // See https://material.io/resources/icons/?style=baseline for accepted values
    setMessage: { default: '' },
    setShow: { default: false },
    setType: { default: 'warning' }, // Accepted values are 'info', 'warning', 'danger', 'success',
  },
  setup(props) {
    const state = reactive({
      dismissible: computed(() => { return props.setDismissible }),
      icon: computed(() => { return props.setIcon }),
      message: computed(() => { return props.setMessage }),
      show: computed(() => { return props.setShow }),
      type: computed(() => { return props.setType }),
    })
    return {
     ...state
    }
  },
})
</script>

<style lang="scss" scoped>
.v-alert {
  margin: 0;
  padding: 0;
}

.v-alert ::v-deep .v-alert__wrapper {
  margin: 0 auto;
  padding: 1.25rem 0.75rem;
  overflow: hidden;
}
</style>
