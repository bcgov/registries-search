<template>
  <v-app class="app-container" data-cy="default-layout">
    <bcros-header />
    <bcros-system-banner
      v-if="systemMessage != null"
      class="justify-center"
      :set-show="systemMessage != null"
      :message="systemMessage"
      type="warning"
    />
    <bcros-breadcrumb v-if="crumbConstructors.length > 0" :crumb-constructors="crumbConstructors" />
    <div class="app-body container mx-auto px-4">
      <slot />
    </div>
    <bcros-footer :about-text="'Business and Person Search UI v' + version" />
  </v-app>
</template>

<script setup lang="ts">
const route = useRoute()
const crumbConstructors = computed(() => (route?.meta?.breadcrumbs || []) as (() => BreadcrumbI)[])

const message = await useBcrosLaunchdarkly().getStoredFlag('banner-text')
const systemMessage = computed((): string | null => {
  if (message?.trim()) { return message.trim() }
  return null
})
const version = useRuntimeConfig().public.version
</script>

<style scoped>

</style>
