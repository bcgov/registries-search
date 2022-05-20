<template>
  <v-app id="app" class="app-container">
    <sbc-header class="sbc-header" :in-auth="false" :show-login-menu="false" />
    <bcrs-breadcrumb :breadcrumbs="breadcrumbs" v-if="breadcrumbs.length > 0" />
    <sbc-system-banner
      v-if="systemMessage != null"
      :setShow="systemMessage != null"
      :setType="systemMessageType"
      :setMessage="systemMessage"
    />
    <v-expand-transition>
      <entity-info v-if="showEntityInfo" />
    </v-expand-transition>
    <div class="app-body py-4">
      <main>
        <router-view
          :appReady="appReady"
          :isJestRunning="isJestRunning"
          @error="handleError($event)"
          @haveData="haveData = $event"
        />
      </main>
    </div>

    <sbc-footer :aboutText="aboutText" />
  </v-app>
</template>

<script setup lang="ts">
// External
import { computed, ref, watch } from 'vue'
import * as Sentry from '@sentry/vue'
import { useRoute } from 'vue-router'

// BC Registry
import { SbcFooter, SbcHeader, SbcSystemBanner } from '@/sbc-common-components'
// Bcrs shared components
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
// Local
import { ErrorI } from '@/interfaces'
import { BcrsBreadcrumb } from '@/bcrs-common-components'
import { EntityInfo } from '@/components'
import { useEntity } from '@/composables'
import { RouteNames } from '@/enums'

const aboutText: string = process.env.ABOUT_TEXT
const appReady = ref(true)
const haveData = ref(true)
const route = useRoute()
const { entity } = useEntity()

/** True if Jest is running the code. */
const isJestRunning = computed((): boolean => {
  return (process.env.JEST_WORKER_ID !== undefined)
})

const systemMessage = computed((): string => {
  // if SYSTEM_MESSAGE does not exist this will return 'undefined'. Needs to be null or str
  const systemMessage = sessionStorage.getItem('SYSTEM_MESSAGE')
  if (systemMessage) return systemMessage
  return null
})
const systemMessageType = computed((): string => {
  // if SYSTEM_MESSAGE_TYPE does not exist this will return 'undefined'. Needs to be null or str
  const systemMessageType = sessionStorage.getItem('SYSTEM_MESSAGE_TYPE')
  if (systemMessageType) return systemMessageType
  return null
})

const breadcrumbs = computed((): Array<BreadcrumbIF> => {
  return route?.meta?.breadcrumb as BreadcrumbIF[] || []
})

const showEntityInfo = computed((): boolean => {
  return [RouteNames.BUSINESS_INFO].includes(route.name as RouteNames)
})

const handleError = (error: ErrorI) => {
  console.error(error)
  // FUTURE: add account info with error information 
  Sentry.captureException(error)
}
watch(entity._error, (error) => { if (error) handleError(error) })
</script>
