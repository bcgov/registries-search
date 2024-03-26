<template>
  <v-row no-gutters>
    <v-col v-if="icon" cols="auto">
      <v-icon class="search-table__icon-name">
        {{ icon }}
      </v-icon>
    </v-col>
    <v-col :class="icon ? 'ml-2' : ''">
      <span v-html="legalName" />
      <BaseDetailsInfoBox
        v-if="item.alternateName"
        class="info-section"
        title="Preferred Name"
        :content="item.alternateName"
      />
      <div v-if="item.birthDate" class="info-section birthdate">
        {{ item.birthDate }}
      </div>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
const prop = defineProps<{ icon?: string, item: SearchResultI }>()
const { highlightMatch } = useBcrosSearch()

const legalName = ref()
onMounted(() => {
  legalName.value = highlightMatch(prop.item.legalName.toUpperCase())
})

</script>

<style lang="scss" scoped>
.info-section {
  margin-top: 10px;
}

.birthdate {
  font-size: smaller;
}
</style>
