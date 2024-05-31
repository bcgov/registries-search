<template>
  <div>
    <a :href="getItemDetailsLink(role)" target="_blank">
      {{ role.relatedName }}
      <UIcon
        v-if="!isModernized(role)"
        class="text-base align-text-bottom"
        color="primary"
        name="i-mdi-open-in-new"
      />
    </a>
    <BcrosAddressDisplay
      v-if="role.relatedAddresses"
      :address="role.relatedAddresses[0]"
      class="my-2"
    />
    <div>
      {{ role.relatedIdentifier }}
    </div>
    <div>
      {{ role.relatedBN }}
    </div>
  </div>
</template>
<script setup lang="ts">
defineProps<{ role: SearchResultRoleI }>()

// business details link
const config = useRuntimeConfig().public
const isModernized = (role: SearchResultRoleI) => {
  const modernizedTypes = [
    CorpTypeCdE.BENEFIT_COMPANY,
    CorpTypeCdE.COOP,
    CorpTypeCdE.SOLE_PROP,
    CorpTypeCdE.PARTNERSHIP
  ]
  return modernizedTypes.includes(role.relatedLegalType)
}
const getItemDetailsLink = (role: SearchResultRoleI) => {
  if (isModernized(role)) {
    return `${config.businessSearchURL}?identifier=${role.relatedIdentifier}`
  }
  return config.bcolURL
}
</script>
