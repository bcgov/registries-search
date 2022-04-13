<template>
  <v-app id="app" class="app-container">
    <sbc-header
      class="sbc-header"
      :in-auth="false"
      :show-login-menu="false"
    />

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
            :appLoadingData="!haveData"
            :appReady="appReady"
            :isJestRunning="isJestRunning"
            @error="handleError($event)"
            @haveData="haveData = $event"
          />
        </v-container>
      </main>
    </div>

    <sbc-footer :aboutText=aboutText />
  </v-app>
</template>

<script lang="ts">
// External
import { defineComponent } from 'vue'
// Local
import { SbcFooter, SbcHeader, SbcSystemBanner } from '@/sbc-common-components'

export default defineComponent({
  name: 'App',
  components: {
    SbcHeader,
    SbcFooter,
    SbcSystemBanner
  },
  setup() {
    return {
      //
    }
  },
})
</script>
