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
    <div v-if="item.entityAddresses" class="flex">
      <div>
        <UIcon class="text-[20px]" name="i-mdi-email-outline" />
      </div>
      <BcrosAddressDisplay class="ml-1" :address="item.entityAddresses[0]" />
    </div>
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
        <BaseDetailsInfoBox
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

<script setup lang="ts">
const prop = defineProps<{ item: SearchResultI }>()
const taxResidency = prop.item.taxResidencies ? (prop.item.taxResidencies[0] === 'CA' ? 'Canada' : 'Other') : ''

</script>

<style lang="scss" scoped>
.information > div:not(:first-child) {
  margin-top: 8px;
}
.information-icon {
  @apply mr-1 text-[20px]
}
</style>
