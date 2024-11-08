<script setup lang="ts">
import { ContactInfo } from '@/components'
import { BcRegistries } from '@/resources/contact-info'

defineProps<{
  title: string
  errorText: string
  hasBcRegContact: { type: string, required: false, default: false }
}>()
</script>

<template>

  <div class="errorBox">
    <div class="content">
      <v-icon color="red">mdi-alert</v-icon>
      <span class="title">{{ title }}:</span>
      <span class="errorText">{{ errorText }}</span>
    </div>
    <div class="contactInfo">
      <contact-info v-if="hasBcRegContact" class="font-normal font-16 mt-4" :contacts="BcRegistries" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.errorBox {
  border: 1px solid #d3272c;
  background-color: #FAE9E9;
  padding: 16px;
}

.content {
  padding-bottom: 4px;
}

.title {
  font-weight: bold;
  padding: 4px;
}

.errorText {
  font-weight: normal;
}
</style>
