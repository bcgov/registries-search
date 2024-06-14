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
    <div v-if="role.relatedAddresses" class="flex mt-3">
      <div>
        <UIcon class="text-[20px]" name="i-mdi-truck-outline" />
      </div>
      <div class="ml-1">
        <BcrosAddressDisplay
          :address="role.relatedAddresses[0]"
        />
      </div>
    </div>
    <div class="flex mt-3">
      <div>
        <UIcon class="text-[20px]" name="i-mdi-pound" />
      </div>
      <div class="ml-1 flex flex-col">
        <span>{{ role.relatedIdentifier }}</span>
        <span>{{ role.relatedBN }}</span>
      </div>
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
