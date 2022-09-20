<template>
  <ul class="error-contact">
    <li>
      <v-icon class="error-contact__icon" size="18px">mdi-phone</v-icon>
      <label class="px-2">Canada and U.S. Toll Free:</label>
      <a class="error-contact__link" href="tel:+1-877-526-1526">1-877-526-1526</a>
    </li>
    <li>
      <v-icon class="error-contact__icon" size="18px">mdi-email</v-icon>
      <label class="px-2">Email:</label>
      <a class="error-contact__link" href="mailto:BCRegistries@gov.bc.ca">BCRegistries@gov.bc.ca</a>
    </li>
  </ul>
</template>

<script setup lang="ts">
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.error-contact {
  font-size: $px-14;
  color: $gray7;
  display: flex;

  &__icon {
    flex: 0 0 1.375rem;
    justify-content: flex-start;
    color: $app-dk-blue;  
    padding-top: 5px;   
  }

  &__link {
    color: $primary-blue;
    flex: 1 1;
  }
}
</style>
