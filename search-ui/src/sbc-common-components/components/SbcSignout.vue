<template>
  <loading-screen :is-loading="isLoading"></loading-screen>
</template>

<script setup lang="ts">
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'

import LoadingScreen from './LoadingScreen.vue'

const isLoading = true
const props = defineProps({
  redirectUrl: {
    type: String,
    default: ''
  }
})

await KeyCloakService.logout(
  props.redirectUrl ? decodeURIComponent(props.redirectUrl) : undefined
)
</script>

<style lang="scss" scoped></style>
