<template>
  <div class="information">
    <div v-if="item.taxNumber">
      {{ item.taxNumber }}
    </div>
    <div v-if="item.email">
      {{ item.email }}
    </div>
    <div v-if="item.entityAddresses">
      <span v-if="street">
        {{ street }}<br>
      </span>
      <span v-if="cityAndRegion">
        {{ cityAndRegion }}<br>
      </span>
      <span v-if="country">
        {{ country }}
      </span>
    </div>
  </div>
  <BaseDetailsInfoBox
    v-if="locationDescription"
    title="Location Description"
    :content="locationDescription"
    class="info-box"
  />
  <BaseDetailsInfoBox
    v-if="item.taxResidencies"
    title="Tax Residency"
    :content="taxResidency"
    class="info-box"
  />
</template>

<script setup lang="ts">
const prop = defineProps<{ item: SearchResultI }>()
const taxResidency = prop.item.taxResidencies ? (prop.item.taxResidencies[0] === 'CA' ? 'Canada' : 'Other') : ''
const street = prop.item.entityAddresses ? prop.item.entityAddresses[0].streetAddress : ''
const cityAndRegion = prop.item.entityAddresses
  ? (`${prop.item.entityAddresses[0].addressCity} ${prop.item.entityAddresses[0].addressRegion} ` +
    `${prop.item.entityAddresses[0].postalCode}`).trim()
  : ''
const country = prop.item.entityAddresses ? prop.item.entityAddresses[0].addressCountry : ''
const locationDescription = prop.item.entityAddresses ? prop.item.entityAddresses[0].locationDescription : ''

</script>

<style lang="scss" scoped>
.information > div:not(:first-child) {
  margin-top: 8px;
}

.info-box {
  margin-top: 10px;
}
</style>
