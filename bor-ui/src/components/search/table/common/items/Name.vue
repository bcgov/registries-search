<template>
  <div class="flex space-x-2">
    <div>
      <UIcon v-if="icon" class="text-xl" :name="icon" />
    </div>
    <div class="flex flex-col">
      <span v-html="legalName" />
      <BcrosDetailsInfoBox
        v-if="item.alternateName"
        class="info-section"
        title="Preferred Name"
        :content="item.alternateName"
      />
      <BcrosDetailsInfoBox
        v-if="item.birthDate"
        class="info-section"
        title="Born"
        :content="item.birthDate"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
type NameInfoT = {
  legalName: string
  alternateName?: string
  birthDate?: string
}
const prop = defineProps<{ icon?: string, item: NameInfoT }>()
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
