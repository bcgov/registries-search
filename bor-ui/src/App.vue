<template>
  <v-app id="app" class="app-container">

    <base-dialog
      id="error-dialog"
      attach="#app"
      :display="errorDisplay"
      :options="errorInfo"
      @close="errorDisplay = false; errorInfo = null"
    >
      <template v-if="errorContactInfo" v-slot:extra-content>
        <p class="font-normal mt-7">If this issue persists, please contact us.</p>
        <contact-info class="font-normal font-16 mt-4" :contacts="HelpdeskInfo" />
      </template>
    </base-dialog>

    <loading-screen v-if="appLoading" :is-loading="appLoading" />
    <sbc-header v-if="auth._tokenInitialized" :in-auth="false" :show-login-menu="false" />
    <sbc-system-banner
      v-if="systemMessage != null"
      class="justify-center"
      :setShow="systemMessage != null"
      :setMessage="systemMessage"
      setType="warning"
    />
    <bcrs-breadcrumb :breadcrumbs="breadcrumbs" v-if="breadcrumbs.length > 0" />
    <div class="app-body pt-4 pb-16">
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
import { computed, onMounted, ref, watch, Ref } from 'vue'
import * as Sentry from '@sentry/vue'
import { useRoute, useRouter } from 'vue-router'
import { StatusCodes } from 'http-status-codes'
// BC Registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { LoadingScreen, SbcFooter, SbcHeader, SbcSystemBanner } from '@/sbc-common-components'
// Bcrs shared components
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
// Local
import { ErrorCategory, RouteName } from '@/enums'
import { DialogOptionsI, ErrorI } from '@/interfaces'
import { BcrsBreadcrumb } from '@/bcrs-shared-components'
import { BaseDialog } from '@/components'
import { useAuth, useSearch } from '@/composables'
import { AuthAccessError, DefaultError } from '@/resources/error-dialog-options'
import { HelpdeskInfo } from '@/resources/contact-info'
import { getFeatureFlag } from '@/utils'
import ContactInfo from './components/common/ContactInfo.vue'

const aboutText: string = 'Search UI v' + process.env.VUE_APP_VERSION
const appLoading = ref(false)
const appReady = ref(false)
const haveData = ref(true)
// errors
const errorDisplay = ref(false)
const errorContactInfo = ref(false)
const errorInfo: Ref<DialogOptionsI> = ref(null)

const route = useRoute()
const router = useRouter()
const { auth, loadAuth, startTokenService } = useAuth()
const { search } = useSearch()

/** True if Jest is running the code. */
const isJestRunning = computed((): boolean => {
  return (process.env.JEST_WORKER_ID !== undefined)
})

const systemMessage = computed((): string => {
  // if SYSTEM_MESSAGE does not exist this will return 'undefined'. Needs to be null or str
  const systemMessage = getFeatureFlag('banner-text')
  if (systemMessage?.trim()) return systemMessage?.trim()
  return null
})

const breadcrumbs = computed((): Array<BreadcrumbIF> => {
  return route?.meta?.breadcrumb as BreadcrumbIF[] || []
})

onMounted(async () => {
  appLoading.value = true
  await router.isReady() // otherwise below will process before route name is determined
  const searchRoutes = [RouteName.SEARCH]
  if (searchRoutes.includes(route.name as RouteName)) {
    // do any preload items here
    if (!appReady.value && !isJestRunning.value) {
      // intitialize token
      await startTokenService()
      // if no token then push to the login page
      if (!sessionStorage.getItem(SessionStorageKeys.KeyCloakToken)) {
        await router.push({ name: RouteName.LOGIN, query: { redirect: '/' } })
        appLoading.value = false
        return
      }
      if (auth._error) return
      console.info('Loading account...')
      // check every second for up to 10 seconds
      for (let i=0; i<10; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        if (sessionStorage.getItem(SessionStorageKeys.SessionSynced) === 'true') {
          break
        }
      }
      console.info('Loading account authorizations...')
      // initialize auth stuff
      await loadAuth()
    }
    if (auth._error) return
    console.info('Verifying user access...')
    if (!isJestRunning.value && !getFeatureFlag('ui-enabled')) {
      handleError({
        category: ErrorCategory.ACCOUNT_ACCESS,
        message: 'This account does not have access to Business and Person Search',
        statusCode: StatusCodes.UNAUTHORIZED,
        type: null
      })
    }
    appReady.value = true
    console.info('App ready.')
  }
  appLoading.value = false
})

const handleError = (error: ErrorI) => {
  console.info(error)
  switch (error.category) {
    case ErrorCategory.ACCOUNT_ACCESS:
      errorInfo.value = {...AuthAccessError}
      if (error.statusCode === StatusCodes.UNAUTHORIZED) {
        errorInfo.value.text = 'This account does not have Business Search selected as an active product.'
        errorInfo.value.textExtra = [
          'Please ensure Business Search is selected in account settings and try again.']
        // don't send error to sentry for ^
      } else {
        errorInfo.value.text = 'We are unable to determine your account access at this ' +
          'time. Please try again later.'
        Sentry.captureException(error)
      }
      errorContactInfo.value = true
      errorDisplay.value = true
      break
    case ErrorCategory.ACCOUNT_SETTINGS:
      errorInfo.value = {...DefaultError}
      errorContactInfo.value = true
      errorDisplay.value = true
      Sentry.captureException(error)
      break
    case ErrorCategory.SEARCH:
      // handled inline
      Sentry.captureException(error)
      break
    case ErrorCategory.SEARCH_UNAVAILABLE:
      // handled inline and no error msg needed
      break
    default:
      errorInfo.value = {...DefaultError}
      errorContactInfo.value = true
      errorDisplay.value = true
      Sentry.captureException(error)
  }
}

// watchers for errors
watch(auth, (val) => { if (val._error) handleError(val._error) })
watch(search, (val) => { if (val._error) handleError(val._error) })
</script>
