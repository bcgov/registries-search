<script setup lang="ts">
import { useThrottleFn } from '@vueuse/core'

const props = defineProps<{
  action: (...args: any[]) => any
  actionArgs?: any[]
  message: string
}>()

const loading = ref(false)

const handleRetry = useThrottleFn(async () => {
  loading.value = true
  // wait 1 sec (give loader time to be shown)
  await new Promise(resolve => setTimeout(resolve, 1000))
  if (props.actionArgs) {
    await props.action(...props.actionArgs)
  } else {
    await props.action()
  }
  loading.value = false
}, 1000)
</script>

<template>
  <div class="bg-transparent text-center" data-testid="error-retry">
    <!-- eslint-disable-next-line vue/no-v-html ; Not a user input field -->
    <p data-testid="error-retry-custom-msg" v-html="message" />
    <p data-testid="error-retry-base-msg">
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
      data-testid="error-retry-btn"
      @click="handleRetry()"
    />
    <div class="flex w-full">
      <ConnectContactDisplay
        class="mt-5 mx-auto shrink *:text-start text-neutral"
        :contact="getContactInfo('helpDesk')"
      />
    </div>
  </div>
</template>
