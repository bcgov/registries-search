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
    <bcros-footer :about-text="'Director Search UI v' + version" />
  </v-app>
</template>

<script setup lang="ts">
const route = useRoute()
const crumbConstructors = computed(() => (route?.meta?.breadcrumbs || []) as (() => BreadcrumbI)[])
async function getSystemMessage () {
  await useBcrosLaunchdarkly().ldClient?.waitUntilReady()
  return useBcrosLaunchdarkly().getFeatureFlag('banner-text')
}
const message = await getSystemMessage()
const systemMessage = computed((): string | null => {
  if (message?.trim()) { return message.trim() }
  return null
})
const version = useRuntimeConfig().public.version
</script>

<style scoped>

</style>
