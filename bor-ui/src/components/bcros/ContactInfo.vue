<template>
  <ul data-cy="contact-info">
    <li v-for="contact, i in contacts" :key="'contact-' + i" class="flex" data-cy="contact-info-item">
      <!-- NB: *weird bug* - the UIcon is not rendering unless there is a comment below containing the name for it -->
      <!-- <UIcon name="i-mdi-phone" /> -->
      <!-- <UIcon name="i-mdi-email" /> -->
      <UIcon
        class="text-[18px] text-primary-600 mt-[3px]"
        :name="contact.icon"
        data-cy="contact-icon"
      />
      <label class="px-2" data-cy="contact-label">{{ contact.label }}:</label>
      <a class="text-blue-500" :href="contact.href" data-cy="contact-value">{{ contact.value }}</a>
    </li>
  </ul>
</template>

<script setup lang="ts">
defineProps<{ contacts: ContactInfoI[] }>()
</script>
