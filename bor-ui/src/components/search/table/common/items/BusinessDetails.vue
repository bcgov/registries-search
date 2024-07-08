<template>
  <div>
    <UButton
      class="text-start underline"
      color="primary"
      :label="role.relatedName"
      :icon="!isModernized(role) ? 'i-mdi-open-in-new' : ''"
      trailing
      variant="link"
      :ui="{ inline: 'inline-block', icon: { base: 'align-bottom ml-1', size: { sm: 'h-4 w-4' } } }"
      @click="goToOpenBusiness(role.relatedIdentifier, role.relatedLegalType)"
    />
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

const isModernized = (role: SearchResultRoleI) => {
  return ModernizedTypes.includes(role.relatedLegalType)
}
</script>
