<template>
  <sbc-signout :redirect-url="logoutURL" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
// Components
import SbcSignout from '@/sbc-common-components/components/SbcSignout.vue'

const logoutURL = computed(
  () => `${sessionStorage.getItem('REGISTRY_URL')}?logout=true`
)
</script>

<style lang="scss" scoped></style>
