<script setup lang="ts">
const { staffPayment } = storeToRefs(useStaffPaymentStore())
</script>

<template>
  <ConnectLayout>
    <template #header>
      <ConnectHeaderAuth />
    </template>
    <template #bottomHeaders>
      <ConnectTombstone />
    </template>
    <template #body>
      <ConnectLayoutPayBody>
        <slot />
        <template #actions>
          <ConnectInput
            id="1"
            v-model="staffPayment.folioNumber"
            class="mt-4"
            :label="$t('label.folioNumberOpt')"
            :ui="{ base: 'bg-shade-inverted' }"
          />
          <ConnectButtonControl />
        </template>
      </ConnectLayoutPayBody>
    </template>
  </ConnectLayout>
</template>
