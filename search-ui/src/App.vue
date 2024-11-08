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
    <sbc-header v-if="auth.tokenInitialized" :in-auth="false" :show-login-menu="false" />

    <!-- Alert banner -->
    <v-alert v-if="bannerText" class="alert-banner ma-0 px-0 py-2" color="warning" max-height="45px">
      <div class="container mx-auto px-4">
        <v-row no-gutters>
          <v-col cols="auto"><v-icon size="30">mdi-alert-circle</v-icon></v-col>
          <v-col style="text-align: center;"><span v-html="bannerText" /></v-col>
        </v-row>
      </div>
    </v-alert>

    <bcrs-breadcrumb :breadcrumbs="breadcrumbs" v-if="breadcrumbs.length > 0" />
    <v-expand-transition>
      <div v-if="showEntityInfo">
        <entity-info />
      </div>
    </v-expand-transition>
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
import { computed, onMounted, ref, Ref, watch } from 'vue'
import * as Sentry from '@sentry/vue'
import { useRoute, useRouter } from 'vue-router'
import { StatusCodes } from 'http-status-codes'
// BC Registry
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { LoadingScreen, SbcFooter, SbcHeader } from '@/sbc-common-components'
// Bcrs shared components
import { BreadcrumbIF, DialogOptionsI, ErrorI } from '@/interfaces'
// Local
import { ErrorCategories, ErrorCodes, ProductCode, RouteNames } from '@/enums'
import { BcrsBreadcrumb } from '@/bcrs-common-components'
import { BaseDialog, EntityInfo } from '@/components'
import {
  useAuth,
  useDocumentAccessRequest,
  useEntity,
  useFeeCalculator,
  useFilingHistory,
  useSearch,
  useSuggest
} from '@/composables'
import {
  AuthAccessError,
  DefaultError,
  EntityLoadError,
  PayBcolError,
  PayDefaultError,
  PayPadError,
  ReportError
} from '@/resources/error-dialog-options'
import { HelpdeskInfo } from '@/resources/contact-info'
import { getFeatureFlag } from '@/utils'
import ContactInfo from './components/common/ContactInfo.vue'
import { DocumentAccessRequestStatus } from '@/enums/document-access-request'
import { PaymentCancelledError } from '@/resources/error-dialog-options/payment-canceled'

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
const { auth, hasProductAccess, isStaff, loadAuth, startTokenService } = useAuth()
const { entity } = useEntity()
const { filingHistory } = useFilingHistory()
const { fees } = useFeeCalculator()
const { search } = useSearch()
const { suggest } = useSuggest()
const { cancelAccessRequest, documentAccessRequest, loadAccessRequestHistory, getAccessRequestById }
  = useDocumentAccessRequest()

/** True if Jest is running the code. */
const isJestRunning = computed((): boolean => {
  return (process.env.JEST_WORKER_ID !== undefined)
})

const bannerText = computed((): string => {
  return getFeatureFlag('banner-text')?.trim() || null
})

const breadcrumbs = computed((): Array<BreadcrumbIF> => {
  return route?.meta?.breadcrumb as BreadcrumbIF[] || []
})

const showEntityInfo = computed((): boolean => {
  return [RouteNames.BUSINESS_INFO, RouteNames.DOCUMENT_REQUEST].includes(route.name as RouteNames)
})

onMounted(async () => {
  appLoading.value = true
  // clear any previous auth errors
  auth._error = null
  await router.isReady() // otherwise below will process before route name is determined
  const searchRoutes = [RouteNames.SEARCH, RouteNames.BUSINESS_INFO, RouteNames.DOCUMENT_REQUEST]
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
    // verify user has access to business search product
    if (!hasProductAccess(ProductCode.BUSINESS_SEARCH) && !isStaff.value) {
      handleError({
        category: ErrorCategories.ACCOUNT_ACCESS,
        message: 'This account does not have access to Business Search',
        statusCode: StatusCodes.UNAUTHORIZED,
        type: ErrorCodes.AUTH_PRODUCTS_ERROR
      })
    }
    const loadedHistory = loadAccessRequestHistory()
    if (route.query?.identifier) {
      router.push({
        name: RouteNames.BUSINESS_INFO,
        params: { identifier: route.query?.identifier }
      })
    } else if (route.query?.documentAccessRequestId) {
      const darId = Number(route.query?.documentAccessRequestId)
      let currentDar = await getAccessRequestById(darId)

      if (currentDar?.status === DocumentAccessRequestStatus.CREATED &&
        route.query?.status === 'UEFZTUVOVF9DQU5DRUxMRUQ=' // this is PAYMENT_CANCELLED
      ) {
        await cancelAccessRequest(entity, currentDar.id)
        currentDar =  await getAccessRequestById(darId)
      } else if (currentDar?.status === DocumentAccessRequestStatus.CREATED) {
        // wait 10 seconds to see if the document gets into the paid state
        for (let i = 0; i < 10; i++) {
          await new Promise(resolve => setTimeout(resolve, 1000))
          currentDar =  await getAccessRequestById(darId)
          if (currentDar.status !== DocumentAccessRequestStatus.CREATED) {
            break
          }
        }
      }

      if (currentDar?.status === DocumentAccessRequestStatus.COMPLETED) {
        router.push({ name: RouteNames.DOCUMENT_REQUEST, params: { darId } })
      }

      documentAccessRequest.currentRequest = currentDar
    } else if (route.query?.docAccessId) {
      await loadedHistory
      documentAccessRequest.currentRequest = documentAccessRequest.requests
        .find(request => request.id === Number(route.query?.docAccessId))
      if (documentAccessRequest.currentRequest) {
        const identifier = documentAccessRequest.currentRequest.businessIdentifier
        const date = documentAccessRequest.currentRequest.submissionDate
        await useEntity().loadEntity(identifier)
        await useFilingHistory().loadFilingHistory(identifier, date)
        router.push({ name: RouteNames.DOCUMENT_REQUEST, params: { identifier } })
      }
    }
    appReady.value = true
    console.info('App ready.')
  }
  appLoading.value = false
})

const handleError = (error: ErrorI) => {
  console.info(error)
  const bcolCodes = [
    ErrorCodes.BCOL_ACCOUNT_CLOSED, ErrorCodes.BCOL_ACCOUNT_INSUFFICIENT_FUNDS,
    ErrorCodes.BCOL_ACCOUNT_REVOKED, ErrorCodes.BCOL_ERROR, ErrorCodes.BCOL_INVALID_ACCOUNT,
    ErrorCodes.BCOL_UNAVAILABLE, ErrorCodes.BCOL_USER_REVOKED
  ]
  switch (error.category) {
    case ErrorCategories.ACCOUNT_ACCESS:
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
    case ErrorCategories.ACCOUNT_SETTINGS:
      errorInfo.value = {...DefaultError}
      errorContactInfo.value = true
      errorDisplay.value = true
      Sentry.captureException(error)
      break
    case ErrorCategories.DOCUMENT_ACCESS_REQUEST_CREATE:
      if (error.statusCode === StatusCodes.PAYMENT_REQUIRED) {
        if (error.type === ErrorCodes.ACCOUNT_IN_PAD_CONFIRMATION_PERIOD) {
          errorInfo.value = {...PayPadError}
          errorContactInfo.value = true
          errorDisplay.value = true
        } else if (bcolCodes.includes(error.type)) {
          errorInfo.value = {...PayBcolError}
          errorInfo.value.textExtra = [error.detail]
          errorContactInfo.value = false
          errorDisplay.value = true
        } else {
          errorInfo.value = {...PayDefaultError}
          errorContactInfo.value = true
          errorDisplay.value = true
        }
      } else {
        // FUTURE: change to CreateDocAccessError once design ready
        errorInfo.value = {...DefaultError}
        errorContactInfo.value = true
        errorDisplay.value = true
      }
      Sentry.captureException(error)
      break
    case ErrorCategories.DOCUMENT_ACCESS_REQUEST_HISTORY:
      // handled inline
      Sentry.captureException(error)
      break
    case ErrorCategories.ENTITY_BASIC:
      errorInfo.value = {...EntityLoadError}
      if (entity.name) {
        errorInfo.value.text = errorInfo.value.text.replace('this business', entity.name)
      }
      errorContactInfo.value = true
      errorDisplay.value = true
      Sentry.captureException(error)
      break
    case ErrorCategories.ENTITY_FILINGS:
      Sentry.captureException(error)
      // handled inline
      break
    case ErrorCategories.FEE_INFO:
      // handled inline
      Sentry.captureException(error)
      break
    case ErrorCategories.REPORT_GENERATION:
      errorInfo.value = {...ReportError}
      errorContactInfo.value = true
      errorDisplay.value = true
      Sentry.captureException(error)
      break
    case ErrorCategories.SEARCH:
      // handled inline
      Sentry.captureException(error)
      break
    case ErrorCategories.SEARCH_UNAVAILABLE:
    case ErrorCategories.DOCUMENT_ACCESS_PAYMENT_ERROR:
      // handled inline and no error msg needed
      break
    case ErrorCategories.DOCUMENT_ACCESS_PAYMENT_CANCELLED:
      errorInfo.value = {...PaymentCancelledError}
      errorContactInfo.value = false
      errorDisplay.value = true
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
watch(entity, (val) => { if (val._error) handleError(val._error) })
watch(fees, (val) => { if (val._error) handleError(val._error) })
watch(filingHistory, (val) => { if (val._error) handleError(val._error) })
watch(search, (val) => { if (val._error) handleError(val._error) })
watch(suggest, (val) => { if (val._error) handleError(val._error) })
watch(documentAccessRequest, (val)=> { if (val._error) handleError(val._error) })
</script>
<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.alert-banner {
  color: $gray9;
  height: 45px;
  vertical-align: top;
}
</style>
