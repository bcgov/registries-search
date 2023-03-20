<template>
  <div class="error-retry">
    <p class="error-retry__custom-msg" v-html="message" />
    <p class="error-retry__base-msg">If this issue persists please contact us.</p>
    <v-btn class="error-retry__btn btn-basic-outlined mx-auto mt-5" :loading="loading" @click="handleRetry()">
      <v-icon color="primary" size="18">mdi-reload</v-icon>
      <span>Retry</span>
    </v-btn>
    <contact-info class="mx-auto mt-5" :contacts="HelpdeskInfo" />
  </div>
</template>
<script setup lang="ts">
// external
import { ref } from 'vue'
import _ from 'lodash'
// local
import { ContactInfo } from '@/components'
import { HelpdeskInfo } from '@/resources/contact-info'

const props = defineProps<{
  action: (...args: any[]) => any
  actionArgs?: any[]
  message: string
}>()

const loading = ref(false)

const handleRetry = _.debounce(async () => {
  loading.value = true
  // wait 1 sec (give loader time to be shown)
  await new Promise(resolve => setTimeout(resolve, 1000))
  if (props.actionArgs) await props.action(...props.actionArgs)
  else await props.action()
  loading.value = false
}, 300)
</script>
<style lang="scss" scoped>
.error-retry {
  background-color: transparent;
  text-align: center;
}
</style>