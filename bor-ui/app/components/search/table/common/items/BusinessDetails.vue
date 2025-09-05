<script setup lang="ts">
defineProps<{ role: SearchResultRole }>()

const isModernized = (role: SearchResultRole) => {
  return ModernizedTypes.includes(role.relatedLegalType)
}
</script>

<template>
  <div>
    <UButton
      class="text-start underline p-0 *:whitespace-normal inline-block"
      color="primary"
      :label="role.relatedName"
      :icon="!isModernized(role) ? 'i-mdi-open-in-new' : ''"
      trailing
      variant="link"
      :ui="{ trailingIcon: '-mb-1 ml-1' }"
      @click="goToOpenBusiness(role.relatedIdentifier, isModernized(role))"
    />
    <div v-if="role.relatedAddresses" class="flex mt-3">
      <div>
        <UIcon class="text-[20px]" name="i-mdi-truck-outline" />
      </div>
      <div class="ml-1">
        <ConnectAddressDisplay
          :address="formatAddress(role.relatedAddresses[0])"
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
