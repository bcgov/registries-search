<template>
  <div :data-cy="name">
    <div class="flex">
      <UIcon v-if="showAddressIcons" name="i-mdi-truck" class="mr-5 text-2xl bg-primary" />
      <div class="flex flex-col w-3/4" :class="showAddressIcons ? '' : 'ml-10'">
        <div class="text-gray-900 pb-1">
          {{ $t('label.address.addressType.delivery') }}
        </div>
        <BcrosAddressDisplay :address="address.deliveryAddress" />
      </div>
    </div>
    <div class="flex pt-3">
      <UIcon v-if="showAddressIcons" name="i-mdi-email-outline" class="mr-5 text-2xl bg-primary" />
      <div class="flex flex-col w-3/4" :class="showAddressIcons ? '' : 'ml-10'">
        <div class="text-gray-900 pb-1">
          {{ $t('label.address.addressType.mailing') }}
        </div>
        <BcrosAddressDisplay
          v-if="differentMailingAddress(address)"
          :address="address.mailingAddress"
        />
        <div v-else>
          {{ $t('text.general.saveAsAbove') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  name: { type: String, required: true },
  address: { type: Object as PropType<deliveryAndMailingAddressI>, required: true },
  showAddressIcons: { type: Boolean, default: false }
})

const differentMailingAddress = (address: deliveryAndMailingAddressI) => {
  return !isSame(address.deliveryAddress, address.mailingAddress, ['id', 'addressType'])
}
</script>
