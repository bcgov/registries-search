<template>
  <ul class="contacts pl-0">
    <li v-for="contact, i in contacts" :key="'contact-' + i" class="contacts__item">
      <!-- NB: *weird bug* - the UIcon is not rendering unless there is a comment below containing the name for it -->
      <!-- <UIcon name="i-mdi-phone" /> -->
      <!-- <UIcon name="i-mdi-email" /> -->
      <UIcon
        class="text-[18px] text-primary-600"
        :name="contact.icon"
        data-cy="contact-icon"
      />
      <label class="px-2" data-cy="contact-label">{{ contact.label }}:</label>
      <a :href="contact.href" data-cy="contact-value">{{ contact.value }}</a>
    </li>
  </ul>
</template>

<script setup lang="ts">
defineProps<{ contacts: ContactInfoI[] }>()
</script>

<style lang="scss" scoped>
.contacts {
  text-align: start;
  width: fit-content;

  &__item {
    display: flex;

    &__icon {
      padding-top: 5px;
    }

    &__link {
      color: theme('colors.blue.500')
    }
  }
}
</style>
