<template>
  <div class="flex space-x-2">
    <UIcon v-if="icon" class="text-xl" :name="icon" />
    <span v-html="legalName" />
  </div>
  <BaseDetailsInfoBox
    v-if="item.alternateName"
    class="info-section"
    title="Preferred Name"
    :content="item.alternateName"
  />
  <BaseDetailsInfoBox
    v-if="item.birthDate"
    class="info-section"
    title="Born"
    :content="item.birthDate"
  />
</template>

<script setup lang="ts">

const prop = defineProps<{ icon?: string, item: SearchResultI }>()
const { highlightMatch } = useBcrosSearch()

const legalName = highlightMatch(prop.item.legalName.toUpperCase())
</script>

<style lang="scss" scoped>
.info-section {
  margin-top: 10px;
}

.birthdate {
  font-size: smaller;
}
</style>
