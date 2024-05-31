<template>
  <div class="app-container flex flex-col" data-cy="default-layout">
    <bcros-header />
    <bcros-system-banner
      class="justify-center"
      :message="systemMessage"
    />
    <bcros-breadcrumb v-if="crumbConstructors.length > 0" :crumb-constructors="crumbConstructors" />
    <div class="app-body grow">
      <slot />
    </div>
    <bcros-footer :about-text="'BCROS Search UI v' + version" />
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const crumbConstructors = computed(() => (route?.meta?.breadcrumbs || []) as (() => BreadcrumbI)[])

const systemMessage = ref('')
onMounted(async () => {
  await useBcrosLaunchdarkly().ldClient.waitUntilReady()
  systemMessage.value = useBcrosLaunchdarkly().getStoredFlag('banner-text')
})

const version = useRuntimeConfig().public.version
</script>

<style scoped>

</style>
