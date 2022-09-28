<template>
  <ul class="contacts pl-0">
    <li v-for="contact, i in contacts" :key="'contact-' + i" class="contacts__item">
      <v-icon v-if="contact.icon" color="darkBlue" class="contacts__item__icon" size="18px">
        {{ contact.icon }}
      </v-icon>
      <label class="px-2">{{ contact.label }}:</label>
      <a :href="contact.href" class="contacts__item__value contacts__item__link">{{ contact.value }}</a>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { ContactInfoI } from '@/interfaces'
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ contacts: ContactInfoI[] }>()
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.contacts {
  text-align: start;
  width: fit-content;

  &__item {
    display: flex;

    &__icon {
      padding-top: 5px;
    }

    &__link {
      color: $primary-blue
    }
  }
}
</style>
