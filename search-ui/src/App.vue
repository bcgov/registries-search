<template>
  <v-app id="app" class="app-container">
    <loading-screen v-if="appLoading" :is-loading="appLoading" />
    <sbc-header v-if="auth.tokenInitialized" class="sbc-header" :in-auth="false" :show-login-menu="false" />
    <bcrs-breadcrumb :breadcrumbs="breadcrumbs" v-if="breadcrumbs.length > 0" />
    <sbc-system-banner
      v-if="systemMessage != null"
      class="justify-center"
      :setShow="systemMessage != null"
      :setType="systemMessageType"
      :setMessage="systemMessage"
    />
    <v-expand-transition>
      <div v-if="showEntityInfo">
        <entity-info />
      </div>
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
import { computed, onMounted, ref, watch } from 'vue'
import * as Sentry from '@sentry/vue'
import { useRoute, useRouter } from 'vue-router'
import { StatusCodes } from 'http-status-codes'
// BC Registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { LoadingScreen, SbcFooter, SbcHeader, SbcSystemBanner } from '@/sbc-common-components'
// Bcrs shared components
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
// Local
import { ErrorCategories, ErrorCodes, ProductCode, RouteNames } from '@/enums'
import { ErrorI } from '@/interfaces'
import { BcrsBreadcrumb } from '@/bcrs-common-components'
import { EntityInfo } from '@/components'
import { useAuth, useEntity, useFeeCalculator, useFilingHistory, useSearch, useSuggest } from '@/composables'
import { navigate } from '@/utils'

const aboutText: string = process.env.ABOUT_TEXT
const appLoading = ref(false)
const appReady = ref(false)
const haveData = ref(true)

const route = useRoute()
const router = useRouter()
const { auth, hasProductAccess, isStaff, loadAuth, startTokenService } = useAuth()
const { entity } = useEntity()
const { filingHistory } = useFilingHistory()
const { fees } = useFeeCalculator()
const { search } = useSearch()
const { suggest } = useSuggest()

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

onMounted(async () => {
  appLoading.value = true
  await router.isReady() // otherwise below will process before route name is determined
  const searchRoutes = [RouteNames.SEARCH, RouteNames.BUSINESS_INFO]
  if (searchRoutes.includes(route.name as RouteNames)) {
    // do any preload items here
    if (!appReady.value && !isJestRunning.value) {
      // intitialize token
      await startTokenService()
      // if no token then push to the login page
      if (!sessionStorage.getItem(SessionStorageKeys.KeyCloakToken)) {
        await router.push({ name: RouteNames.LOGIN, query: { redirect: '/' } })
        appLoading.value = false
        return
      }
      // wait to allow time for sbc header stuff to load (i.e. current account)
      console.info('Loading account...')
      // check every second for up to 10 seconds
      for (let i=0; i<10; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        if (sessionStorage.getItem(SessionStorageKeys.SessionSynced) === 'true') break
      }
      console.info('Loading account authorizations...')
      // initialize auth stuff
      await loadAuth()
    }
    console.info('Verifying user access...')
    // verify user has access to business search product
    if (!hasProductAccess(ProductCode.BUSINESS_SEARCH) && !isStaff.value) {
      handleError({
        category: ErrorCategories.ACCOUNT_ACCESS,
        message: 'This account does not have access to Business Search',
        statusCode: StatusCodes.UNAUTHORIZED,
        type: ErrorCodes.AUTH_PRODUCTS_ERROR
      })
    }
    appReady.value = true
    console.info('App ready.')
  }
  appLoading.value = false
})

const handleError = (error: ErrorI) => {
  console.error(error)
  // FUTURE: add account info with error information, add dialog popups for specific errors
  switch (error.category) {
    case ErrorCategories.ACCOUNT_ACCESS:
      navigate(sessionStorage.getItem('REGISTRY_URL'))
  }
  Sentry.captureException(error)
}
// watchers for errors
watch(auth, (val) => { if (val._error) handleError(val._error) })
watch(entity, (val) => { if (val._error) handleError(val._error) })
watch(fees, (val) => { if (val._error) handleError(val._error) })
watch(filingHistory, (val) => { if (val._error) handleError(val._error) })
watch(search, (val) => { if (val._error) handleError(val._error) })
watch(suggest, (val) => { if (val._error) handleError(val._error) })
</script>
