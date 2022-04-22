<template>
  <SbcLogin :redirectUrl="redirectUrl" />
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import SbcLogin from 'sbc-common-components/src/components/SbcLogin.vue';

const route = useRoute()
const redirectUrl = computed(() => route.query.redirect)
</script>

<style lang="scss" scoped></style>
