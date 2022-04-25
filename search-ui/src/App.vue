<template>
  <v-app id="app" class="app-container">
    <sbc-header class="sbc-header" :in-auth="false" :show-login-menu="false" />

    <div class="app-body">
      <main>
        <sbc-system-banner
          v-if="systemMessage != null"
          v-bind:show="systemMessage != null"
          v-bind:type="systemMessageType"
          v-bind:message="systemMessage"
          align="center"
          icon=" "
        />
        <v-container class="view-container pa-0 ma-0">
          <router-view
            :appReady="appReady"
            :isJestRunning="isJestRunning"
            @error="handleError($event)"
            @haveData="haveData = $event"
          />
        </v-container>
      </main>
    </div>

    <sbc-footer :aboutText="aboutText" />
  </v-app>
</template>

<script setup lang="ts">
// External
import { computed, ref } from 'vue'
import * as Sentry from '@sentry/vue'
// BC Registry
import { SbcFooter, SbcHeader, SbcSystemBanner } from '@/sbc-common-components'
// Local
import { ErrorI } from '@/interfaces'

const aboutText: string = process.env.ABOUT_TEXT
const appReady = ref(true)
const haveData = ref(true)

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

const handleError = (error: ErrorI) => {
  console.error(error)
  // FUTURE: add account info with error information 
  Sentry.captureException(error)
}
</script>
