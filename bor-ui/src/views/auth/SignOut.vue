<template>
  <SbcSignOut :redirect-url="logoutURL" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
// Components
import SbcSignOut from '@/sbc-common-components/components/SbcSignOut.vue'

const logoutURL = computed(
  () => `${sessionStorage.getItem('REGISTRY_URL')}?logout=true`
)
</script>

<style lang="scss" scoped></style>
