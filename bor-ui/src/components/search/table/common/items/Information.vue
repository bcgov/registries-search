<template>
  <div class="information">
    <div v-if="item.taxNumber">
      {{ item.taxNumber }}
    </div>
    <div v-if="item.email">
      {{ item.email }}
    </div>
    <BcrosAddressDisplay
      v-if="item.entityAddresses"
      :address="item.entityAddresses[0]"
    />
    <BaseDetailsInfoBox
      v-if="item.taxResidencies"
      title="Tax Residency"
      :content="taxResidency"
    />
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
</style>
