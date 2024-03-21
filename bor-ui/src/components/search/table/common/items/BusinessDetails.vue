<template>
  <div v-if="item.roles">
    <a :href="getItemDetailsLink(item)" target="_blank">
      {{ item.roles[0].relatedName }}
      <v-icon
        v-if="!isModernized(item)"
        class="mb-1"
        color="primary"
        icon="mdi-open-in-new"
        size="small"
      />
    </a>
    <br>
    {{ item.roles[0].relatedIdentifier }}
    <br>
    {{ item.roles[0].relatedBN }}
  </div>
  <span v-else>N/A</span>
</template>
<script setup lang="ts">
defineProps<{ item: SearchResultI }>()

// business details link
const config = useRuntimeConfig().public
const isModernized = (item: SearchResultI) => {
  const modernizedTypes = [
    CorpTypeCdE.BENEFIT_COMPANY,
    CorpTypeCdE.COOP,
    CorpTypeCdE.SOLE_PROP,
    CorpTypeCdE.PARTNERSHIP
  ]
  return modernizedTypes.includes(item.roles[0].relatedLegalType)
}
const getItemDetailsLink = (item: SearchResultI) => {
  if (isModernized(item)) {
    return `${config.businessSearchURL}?identifier=${item.roles[0].relatedIdentifier}`
  }
  return config.bcolURL
}
</script>
