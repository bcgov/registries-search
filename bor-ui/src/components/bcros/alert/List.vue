<template>
  <div data-cy="alerts-display">
    <UAccordion
      color="black"
      variant="outline"
      size="sm"
      :items="alerts"
    >
      <template #default="{ item, open }">
        <BcrosAlert
          :alert="item"
          :open="open"
          :show-description="false"
          :contact="contact"
        />
      </template>
      <template #item="{ item, open }">
        <BcrosAlert :open="open" :alert="item" :show-header="false" :contact="contact" />
      </template>
    </UAccordion>
  </div>
</template>

<script setup lang="ts">
defineProps<{ alerts: Array<Partial<AlertI>>, contact: boolean }>()
</script>
