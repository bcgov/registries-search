<template>
  <div data-cy="address-display">
    <div
      v-for="addressLine, i in addressData"
      :key="addressLine + i"
      data-cy="address-line"
    >
      {{ addressLine }}
    </div>
    <BcrosDetailsInfoBox
      v-if="address.locationDescription"
      class="mt-2"
      :content="address.locationDescription"
      title="Location Description"
      data-cy="location-description"
    />
  </div>
</template>

<script setup lang="ts">
import { getName } from 'country-list'

const props = defineProps<{ address: Partial<AddressI> }>()

const addressData = computed((): string[] => {
  return [
    props.address.streetAddress,
    props.address.streetAdditional,
    [props.address.addressCity, props.address.addressRegion, props.address.postalCode].filter(val => !!val).join(' '),
    // NOTE: getName throws an error when called with undefined
    getName(props.address.addressCountry ?? '') || props.address.addressCountry
  ].filter(val => !!val)
})
</script>
