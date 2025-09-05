<script setup lang="ts">
const prop = defineProps<{ item: SearchResult }>()
const taxResidency = prop.item.taxResidencies ? (prop.item.taxResidencies[0] === 'CA' ? 'Canada' : 'Other') : ''
const LOCATION_ADDRESS_TYPE = 'RESIDENCE'
</script>

<template>
  <div class="information">
    <!-- NB: if the UIcons are not wrapped in dev they render at differring sizes -->
    <div v-if="item.email" class="flex">
      <div>
        <UIcon class="text-[20px]" name="i-mdi-at" />
      </div>
      <div class="ml-1 overflow-auto">
        {{ item.email }}
      </div>
    </div>
    <span v-if="item.entityAddresses">
      <div
        v-for="(address, index) in item.entityAddresses"
        :key="index"
        class="flex"
      >
        <div>
          <UIcon
            class="text-[20px]"
            :name="address.addressType === LOCATION_ADDRESS_TYPE ? 'i-mdi-map-marker-outline' : 'i-mdi-email-outline'"
          />
        </div>
        <ConnectAddressDisplay class="ml-1" :address="formatAddress(address)" />
      </div>
    </span>
    <div v-if="item.phoneNumber" class="flex">
      <div>
        <UIcon class="text-[20px]" name="i-mdi-phone" />
      </div>
      <div class="ml-1">
        {{ item.phoneNumber }}
      </div>
    </div>
    <div v-if="item.taxResidencies || item.taxNumber" class="flex">
      <div>
        <UIcon class="text-[20px]" name="i-mdi-bank-outline" />
      </div>
      <div class="ml-1">
        <DetailsInfoBox
          v-if="item.taxResidencies"
          class="mb-2"
          title="Tax Residency"
          :content="taxResidency"
        />
        <div v-if="item.taxNumber">
          {{ item.taxNumber }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.information > div:not(:first-child) {
  margin-top: 8px;
}
</style>
