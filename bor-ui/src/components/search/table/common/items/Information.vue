<template>
  <div class="information">
    <div v-if="item.taxNumber">
      {{ item.taxNumber }}
    </div>
    <div v-if="item.email">
      {{ item.email }}
    </div>
    <div v-if="item.entityAddresses">
      {{ item.entityAddresses[0].streetAddress }}
      <br>
      <span>
        {{ item.entityAddresses[0].addressCity }}
        {{ item.entityAddresses[0].addressRegion }} {{ item.entityAddresses[0].postalCode }}
        <br>
        {{ item.entityAddresses[0].addressCountry }}
      </span>
    </div>
  </div>
  <BaseDetailsInfoBox
    v-if="item.taxResidencies"
    title="Tax Residency"
    :content="taxResidency"
    class="tax-residency"
  />
</template>

<script setup lang="ts">
const prop = defineProps<{ item: SearchResultI }>()
const taxResidency = ref()
onMounted(() => {
  if (prop.item.taxResidencies) {
    taxResidency.value = prop.item.taxResidencies[0] === 'CA' ? 'Canada' : 'Other'
  }
})
</script>

<style lang="scss" scoped>
.information > div:not(:first-child) {
  margin-top: 8px;
}

.tax-residency {
  margin-top: 10px;
}
</style>
