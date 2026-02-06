<script setup lang="ts">
import { AccountType } from '#imports'

const { t } = useI18n()

const searchAccess = useSearchAccessStore()
const { hasExtendedAccess } = storeToRefs(searchAccess)

const account = useConnectAccountStore()
const { currentAccount, currentAccountName, userFullName } = storeToRefs(account)

const searchTitleText = t('label.businessPersonSearch')

const tabs = [
  { slot: 'search', label: t('label.findBusinessPerson'), icon: 'i-mdi-magnify' },
  { slot: 'documents', label: t('label.viewPurchasedDocuments'), icon: 'i-mdi-file-document-outline' }
]

definePageMeta({
  layout: 'connect-auth',
  middleware: [
    // Check for login redirect
    'connect-auth',
    // Initialize search access
    async () => {
      const searchAccess = useSearchAccessStore()
      await searchAccess.init()
    }
  ],
  onAccountChange: (_oldAccount: ConnectAccount, newAccount: ConnectAccount) => {
    useConnectAccountStore().switchCurrentAccount(newAccount.id)
    useBcrosNavigate().redirect(useRuntimeConfig().public.baseUrl)
    return true
  }
})

onBeforeMount(() => {
  const config = useRuntimeConfig().public
  setBreadcrumbs([
    { to: config.registryHomeUrl + 'dashboard', label: t('label.bcregDash') },
    { label: t('label.businessPersonSearch') }
  ])
})
</script>

<template>
  <div class="mt-8 mb-16" data-testid="search-page">
    <h1>{{ searchTitleText }}</h1>
    <div v-if="currentAccount?.id" class="flex mt-1 pt-2">
      <div class="pl-[2px] pr-5 border-r border-line" data-testid="account-name">
        <span v-if="currentAccount.accountType === AccountType.STAFF">BC Registries Staff</span>
        <span v-else>{{ currentAccountName }}</span>
      </div>
      <div class="pl-5" data-testid="user-name">
        {{ userFullName }}
      </div>
    </div>
    <DocHelp class="mt-3" />
    <UTabs
      v-if="!hasExtendedAccess"
      class="mt-5"
      :items="tabs"
      data-testid="search-tabs"
      color="neutral"
      :ui="{
        list: 'self-start bg-brand max-w-[600px]',
        trigger: [
          'hover:cursor-pointer',
          'data-[state=active]:bg-shade-inverted',
          'data-[state=active]:text-neutral-highlighted',
          'data-[state=inactive]:text-inverted',
          'hover:data-[state=inactive]:not-disabled:text-inverted',
        ],
      }"
    >
      <template #search>
        <Search />
      </template>
      <template #documents>
        <DocAccessHistory />
      </template>
    </UTabs>
    <Search v-else />
  </div>
</template>

<style scoped>
.tab-item-inactive {
  color: white;
  background-color: var(--ui-brand);
  box-shadow: inset 0 0 5px 1px var(--ui-neutral-highlighted);
  margin-top: 5px;
  transition: none !important;
}
.tab-item-inactive:hover {
  background-color: var(--ui-primary);
  box-shadow: none;
}

.tab-item-active {
  color: var(--color-gray-800);
  background-color: white;
  transition: none !important;
}

.tab-item-default {
  border-radius: 5px 5px 0 0 !important;
  font-size: 1.125rem;
  height: 67px;
  min-width: 50%;
  width: 50%;
}
</style>
