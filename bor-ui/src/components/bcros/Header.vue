<template>
  <header id="appHeader" class="app-header" data-cy="bcros-header">
    <div class="container px-4 mx-auto">
      <v-row justify="end" no-gutters style="align-items: center">
        <v-col>
          <a class="brand" @click="goToBcrosHome()">
            <picture>
              <source media="(max-width:600px)" srcset="@/assets/images/gov_bc_logo_vert.png">
              <img src="@/assets/images/gov_bc_logo_horiz.png" alt="Government of British Columbia Logo">
            </picture>
            <span class="brand__title ml-4">
              BC Registries <span class="brand__title--wrap">and Online Services</span>
            </span>
          </a>
        </v-col>
        <v-col align-self="end" cols="auto">
          <v-row class="app-header__actions" no-gutters style="align-items: center">
            <v-col cols="auto">
              <!-- Login Menu -->
              <v-menu
                v-if="!authenticated"
                fixed
                bottom
                left
                width="330"
                transition="slide-y-transition"
              >
                <template #activator="{ props }">
                  <v-btn
                    id="loginBtn"
                    large
                    text
                    dark
                    class="mx-1 pr-2 pl-3"
                    aria-label="log in"
                    variant="text"
                    v-bind="props"
                  >
                    <span>Log in</span>
                    <v-icon class="ml-1">
                      mdi-menu-down
                    </v-icon>
                  </v-btn>
                </template>
                <v-card>
                  <div>
                    <v-card-title class="body-2 font-weight-bold">
                      Select login method
                    </v-card-title>
                    <v-divider />
                  </div>
                  <v-list density="compact">
                    <v-list-item
                      v-for="loginOption in loginOptions"
                      :key="loginOption.idpHint"
                      class="pr-6"
                      :prepend-icon="loginOption.icon"
                      :title="loginOption.option"
                      @click="goToBcrosLogin(loginOption.idpHint)"
                    />
                  </v-list>
                </v-card>
              </v-menu>
            </v-col>
            <v-col cols="auto">
              <!-- Account -->
              <v-menu
                v-if="authenticated"
                bottom
                left
                transition="slide-y-transition"
              >
                <template #activator="{ props }">
                  <v-btn variant="text" size="large" class="user-account-btn" aria-label="my account" v-bind="props">
                    <v-avatar
                      tile
                      left
                      color="#4d7094"
                      size="32"
                      class="user-avatar white-text"
                    >
                      {{ userFullName.slice(0,1) }}
                    </v-avatar>
                    <div class="user-info">
                      <div class="user-name" data-test="user-name">
                        {{ userFullName }}
                      </div>
                      <div class="account-name" data-test="account-name">
                        {{ currentAccountName }}
                      </div>
                    </div>
                    <v-icon class="ml-1">
                      mdi-menu-down
                    </v-icon>
                  </v-btn>
                </template>

                <v-card>
                  <!-- User Profile -->
                  <v-list density="compact" lines="two">
                    <v-list-item class="user-info">
                      <template #prepend>
                        <v-avatar
                          tile
                          color="#4d7094"
                          size="36"
                          class="user-avatar white-text"
                        >
                          {{ userFullName.slice(0,1) }}
                        </v-avatar>
                      </template>
                      <v-list-item-title class="user-name" data-test="menu-user-name">
                        {{ userFullName }}
                      </v-list-item-title>
                      <v-list-item-subtitle class="account-name" data-test="menu-account-name">
                        {{ currentAccountName }}
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                  <v-list density="compact">
                    <v-list-item
                      v-if="canCreateAccount"
                      prepend-icon="mdi-account-outline"
                      title="Edit Profile"
                      @click="goToEditProfile()"
                    />
                    <!-- END -->
                    <v-list-item
                      prepend-icon="mdi-logout-variant"
                      title="Log out"
                      @click="logout(config.public.registryHomeURL)"
                    />
                  </v-list>

                  <v-divider />

                  <!-- Account Settings -->
                  <v-list v-if="currentAccount" density="compact">
                    <v-list-subheader>ACCOUNT SETTINGS</v-list-subheader>
                    <v-list-item
                      prepend-icon="mdi-information-outline"
                      title="Account Info"
                      @click="goToAccountInfo()"
                    />
                    <v-list-item
                      prepend-icon="mdi-account-group-outline"
                      title="Team Members"
                      @click="goToTeamMembers()"
                    />
                    <v-list-item
                      v-if="showTransactions"
                      prepend-icon="mdi-file-document-outline"
                      title="Transactions"
                      @click="goToTransactions()"
                    />
                  </v-list>

                  <v-divider />

                  <!-- Switch Account -->
                  <div v-if="currentAccount.accountType != AccountTypeE.STAFF">
                    <v-list
                      v-if="userAccounts.length > 1"
                      class="switch-account"
                      density="compact"
                    >
                      <v-list-subheader>SWITCH ACCOUNT</v-list-subheader>
                      <v-list-item
                        v-for="acc, index in userAccounts"
                        :key="index"
                        :class="{ 'v-list-item--active': acc.id === currentAccount.id }"
                        color="primary"
                        :title="acc.label"
                        @click="switchAccount(acc.id)"
                      >
                        <template #prepend>
                          <v-icon
                            v-if="acc.id === currentAccount.id"
                            :class="acc.additionalLabel ? 'mt-n4' : ''"
                            color="primary"
                          >
                            mdi-check
                          </v-icon>
                        </template>
                        <v-list-item-subtitle
                          v-if="acc.additionalLabel"
                          class="font-italic"
                          :class="{'primary--text' : acc.id === currentAccount.id}"
                        >
                          {{ `- ${acc.additionalLabel}` }}
                        </v-list-item-subtitle>
                      </v-list-item>
                    </v-list>

                    <v-divider />

                    <!-- Create a New Account -->
                    <v-list v-if="canCreateAccount" density="compact">
                      <v-list-item
                        prepend-icon="mdi-plus"
                        title="Create account"
                        @click="createAccount()"
                      />
                    </v-list>
                  </div>
                </v-card>
              </v-menu>

              <v-btn
                v-if="!authenticated"
                variant="text"
                size="large"
                @click="createAccount()"
              >
                Create Account
              </v-btn>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </div>
  </header>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'

defineProps<{ personMode?: boolean }>()

const config = useRuntimeConfig()
const {
  goToAccountInfo,
  goToBcrosHome,
  goToBcrosLogin,
  goToEditProfile,
  goToTeamMembers,
  goToTransactions
} = useBcrosNavigate()
// account / user
const account = useBcrosAccount()
const { currentAccount, currentAccountName, userFullName, userAccounts } = storeToRefs(account)
// kc / auth
const keycloak = useBcrosKeycloak()
const authenticated = computed(() => keycloak.kc.authenticated)
const { createAccount, logout } = useBcrosAuth()

function switchAccount (accountId: number) {
  account.switchCurrentAccount(accountId)
  // refresh the page so that account based checks are rerun
  window.location.search = '?accountid=' + accountId
}

const loginOptions = [
  { idpHint: IdpHintE.BCSC, option: 'BC Services Card', icon: 'mdi-account-card-details-outline' },
  { idpHint: IdpHintE.BCEID, option: 'BCeID', icon: 'mdi-two-factor-authentication' },
  { idpHint: IdpHintE.IDIR, option: 'IDIR', icon: 'mdi-account-group-outline' }
]

const canCreateAccount = computed((): boolean => {
  if ([LoginSourceE.BCROS, LoginSourceE.IDIR].includes(keycloak.kcUser?.loginSource)) {
    return false
  }
  return true
})

const showTransactions = computed(() => {
  return [AccountTypeE.PREMIUM, AccountTypeE.SBC_STAFF, AccountTypeE.STAFF].includes(currentAccount.value.accountType)
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

$app-header-font-color: #ffffff;

.app-header {
  height: 68px;
  border-bottom: 2px solid $BCgovGold5;
  color: white;
  background-color: $BCgovBlue5;

  .container {
    display: flex;
    align-items: center;
    height: 100%;
    padding-top: 0;
    padding-bottom: 0;
  }
}

.brand {
  display: flex;
  align-items: center;
  padding-right: 1rem;
  text-decoration: none;
  color: inherit;
}

.brand__image {
  display: block;
  margin-right: 1.25rem;
  max-height: 68px;
}

.brand__title {
  letter-spacing: -0.03rem;
  font-size: 1.125rem;
  font-weight: 700;
  color: inherit;
}

.user-avatar {
  border-radius: 0.15rem;
  font-size: 1.1875rem;
  font-weight: 700;
}

.white-text {
  color: white;
}
.switch-account{
  height:42vh;
  overflow-y: scroll;

}
@media (max-width: 900px) {
  .brand__image {
    margin-right: 0.75rem;
    margin-left: -0.15rem;
  }

  .brand__title {
    font-size: 1rem;
    line-height: 1.25rem;
  }

  .brand__title--wrap {
    display: block;
  }
}

.v-btn.user-account-btn {
  padding: 0 !important;
  text-align: left;
  letter-spacing: 0.02rem;
  font-size: 0.8rem;

  .user-avatar {
    margin-right: 0.75rem;
  }

  .user-name {
    line-height: 1.125rem;
    font-size: 0.875rem;
  }

  .account-name {
    margin-bottom: 0.01rem;
    font-size: 0.7rem;
    opacity: 0.75;
    max-width: 15rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.v-list-subheader {
  color: $gray9 !important;
  font-weight: 700;
}

:deep(.v-list-subheader__text) {
  opacity: 1 !important;
}

.menu-header {
  display: none;
}

@media (max-width: 1263px) {
  .v-btn.mobile-icon-only {
    min-width: 3rem !important;
    width: 3rem;

    .v-icon + span,
    span + .v-icon {
      display: none;
    }

    .v-icon {
      margin-right: 0;
    }
  }

  .v-btn.user-account-btn {
    min-width: auto !important;
    font-size: 0.8rem;

    .user-avatar {
      margin-right: 0;
    }

    .user-info,
    .v-icon {
      display: none;
    }
  }

  .v-btn.login-btn {
    .v-icon + span,
    span + .v-icon {
      display: none;
    }
  }

  .menu-header {
    display: block;
  }
}

@media (min-width: 1360px) {
  .v-menu__content {
    max-width: 22rem;
  }
}
</style>
