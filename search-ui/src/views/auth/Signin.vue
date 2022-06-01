<template>
  <SbcSignin @sync-user-profile-ready="onProfileReady()" />
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { navigate } from '@/utils'
// Components
import SbcSignin from '@/sbc-common-components/components/SbcSignin.vue'

const route = useRoute()
const props = defineProps({
  registryUrl: {
    type: String,
    default: sessionStorage.getItem('REGISTRY_URL')
  }
})
const emit = defineEmits(['profileReady'])

/** Called when user profile is ready (ie, the user is authenticated). */
function onProfileReady() {
  // let App know that data can now be loaded
  emit('profileReady', true)

  if (route.query.redirect) navigate(route.query.redirect as string)
  else {
    console.error('Signin page missing redirect param')// eslint-disable-line no-console
    navigate(props.registryUrl)
  }
}
</script>

<style lang="scss" scoped></style>
