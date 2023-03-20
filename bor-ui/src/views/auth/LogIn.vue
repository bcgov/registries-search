<template>
  <SbcLogin :redirectUrl="redirectUrl" />
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import SbcLogin from '@/sbc-common-components/components/SbcLogin.vue'

const route = useRoute()
const redirectUrl = route.query.redirect as string
</script>

<style lang="scss" scoped></style>
