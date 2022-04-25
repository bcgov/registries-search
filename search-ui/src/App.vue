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
import { SbcFooter, SbcHeader, SbcSystemBanner } from '@/sbc-common-components'
import { computed } from '@vue/runtime-core'

const aboutText: string = process.env.ABOUT_TEXT
const appReady = true
const haveData = true
const isJestRunning = false

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

const handleError = (error) => {
  console.log(error)
}
</script>
