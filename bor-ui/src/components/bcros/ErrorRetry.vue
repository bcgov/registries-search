<template>
  <div class="bg-transparent text-center" data-cy="error-retry">
    <p data-cy="error-retry-custom-msg" v-html="message" />
    <p data-cy="error-retry-base-msg">
      If this issue persists please contact us.
    </p>
    <UButton
      class="mx-auto mt-5 p-3"
      color="primary"
      icon="i-mdi-reload"
      label="Retry"
      :loading="loading"
      trailing
      variant="outline"
      data-cy="error-retry-btn"
      @click="handleRetry()"
    />
    <bcros-contact-info class="max-w-[310px] mx-auto mt-5" :contacts="HelpdeskInfo" />
  </div>
</template>
<script setup lang="ts">
// external
import { ref } from 'vue'
import _ from 'lodash'
// local
import { HelpdeskInfo } from '@/resources/contact-info'

const props = defineProps<{
  action:(...args: any[]) => any
  actionArgs?: any[]
  message: string
}>()

const loading = ref(false)

const handleRetry = _.debounce(async () => {
  loading.value = true
  // wait 1 sec (give loader time to be shown)
  await new Promise(resolve => setTimeout(resolve, 1000))
  if (props.actionArgs) { await props.action(...props.actionArgs) } else { await props.action() }
  loading.value = false
}, 300)
</script>
