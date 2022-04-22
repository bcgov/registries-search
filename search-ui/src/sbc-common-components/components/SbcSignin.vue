<template>
  <loading-screen :is-loading="isLoading"></loading-screen>
</template>

<script setup lang="ts">
import { Role, LoginSource, Pages } from 'sbc-common-components/src/util/constants'
import KeyCloakService from '@/sbc-common-components/services/keycloak.services'
import LoadingScreen from './LoadingScreen.vue'
import { getModule } from 'vuex-module-decorators'
import AccountModule from 'sbc-common-components/src/store/modules/account'
import AuthModule from 'sbc-common-components/src/store/modules/auth'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { useNavigation } from '@/sbc-common-components/composables'
import {  useStore } from 'vuex'
import { ref } from 'vue'

const isLoading = ref(true)

const props = defineProps({
  idpHint: { type: String, default: 'bcsc'},
  redirectUrlLoginFail: { type: String, default: '' },
  inAuth: { type: Boolean, default: false }
})

const store  = useStore()
// set modules
if (!store.hasModule('account')) store.registerModule('account', AccountModule)
if (!store.hasModule('auth')) store.registerModule('auth', AuthModule)

getModule(AccountModule, store)
getModule(AuthModule, store)

const { redirectToPath } = useNavigation()

const loadUserInfo = async () => { await store.dispatch('account/loadUserInfo') }
const updateUserProfile = async () => { await store.dispatch('account/updateUserProfile') }
const syncAccount = async () => { await store.dispatch('account/syncAccount') }
const getCurrentUserProfile = async (inAuth: boolean) => { 
  await store.dispatch('account/getCurrentUserProfile', inAuth) }

const emit = defineEmits(['sync-user-profile-ready'])

// Initialize keycloak session
const kcInit = KeyCloakService.initializeKeyCloak(props.idpHint, store)
kcInit
  .then(async (authenticated: boolean) => {
    if (authenticated) {
      // eslint-disable-next-line no-console
      console.info(
        '[SignIn.vue]Logged in User. Init Session and Starting refreshTimer'
      )
      // Set values to session storage
      await KeyCloakService.initSession()
      // tell KeycloakServices to load the user info
      await loadUserInfo()
      const userInfo = store.state.account.currentUser as KCUserProfile
      // update user profile
      await updateUserProfile()
      // sync the account if there is one
      await syncAccount()
      // if not from the sbc-auth, do the checks and redirect to sbc-auth
      if (!props.inAuth) {
        // redirect to create account page if the user has no 'account holder' role
        const isRedirectToCreateAccount =
          userInfo.roles.includes(Role.PublicUser) &&
          !userInfo.roles.includes(Role.AccountHolder)
        //CHANGE  
        const currentUser = await getCurrentUserProfile(props.inAuth)
        if (
          userInfo?.loginSource !== LoginSource.IDIR &&
          !currentUser?.userTerms?.isTermsOfUseAccepted
        ) {
          console.log('[SignIn.vue]Redirecting. TOS not accepted')
          redirectToPath(props.inAuth, Pages.USER_PROFILE_TERMS)
        } else if (isRedirectToCreateAccount) {
          console.log('[SignIn.vue]Redirecting. No Valid Role')
          switch (userInfo.loginSource) {
            case LoginSource.BCSC:
              redirectToPath(props.inAuth, Pages.CREATE_ACCOUNT)
              break
            case LoginSource.BCEID:
              redirectToPath(props.inAuth, Pages.CHOOSE_AUTH_METHOD)
              break
          }
        }
      }
      emit('sync-user-profile-ready')
    }
  })
  .catch(() => {
    if (props.redirectUrlLoginFail) {
      window.location.assign(decodeURIComponent(props.redirectUrlLoginFail))
    }
  })
</script>

<style lang="scss" scoped></style>
