<script setup lang="ts">
const { params } = useRoute()
const businessId = params.businessId as string

const { t } = useI18n()
const localePath = useLocalePath()
const registryHomeUrl = useRuntimeConfig().public.registryHomeUrl

definePageMeta({
  layout: 'search-purchase-docs',
  middleware: 'connect-auth',
  onAccountChange: (_oldAccount: ConnectAccount, newAccount: ConnectAccount) => {
    useConnectAccountStore().switchCurrentAccount(newAccount.id)
    useBcrosNavigate().redirect(useRuntimeConfig().public.baseUrl)
    return true
  }
})

const businessStore = useBusinessStore()
const { business, businessName, businessAlerts } = storeToRefs(businessStore)

const { submitDocAccess } = useDocAccessStore()

const { getDocumentList } = useBusinessSearchApi()

const { fees } = storeToRefs(useConnectFeeStore())

const documentSelect = ref<{ $el: HTMLElement } | null>(null)
const submit = async () => {
  if (fees.value && Object.keys(fees.value).length && business.value) {
    if (
      [AccountType.STAFF, AccountType.SBC_STAFF].includes(
        useConnectAccountStore().currentAccount?.accountType)
    ) {
      const staffModal = useModal().staffPaymentModal
      staffModal.open({
        onSubmit: async () => {
          await submitDocAccess(businessId, businessName.value || '')
          staffModal.close()
        }
      })
    } else {
      await submitDocAccess(businessId, businessName.value || '')
    }
  } else {
    setAlertText(t('text.selectDocumentsToDownload'), 'right', 1)
    documentSelect.value?.$el.scrollIntoView({ behavior: 'smooth' })
  }
}

const { setButtonControl, setAlertText } = useConnectButtonControl()
setButtonControl({
  leftGroup: { buttons: [] },
  rightGroup: {
    buttons: [
      {
        label: t('label.backToSearchResults'),
        class: 'min-w-[300px] justify-center',
        leadingIcon: 'i-mdi-chevron-left',
        removeAlertSpacing: true,
        variant: 'outline',
        onClick: () => { useRouter().push(localePath('/')) }
      },
      {
        label: t('label.payAndUnlockDocuments'),
        class: 'min-w-[300px] justify-center font-bold',
        trailingIcon: 'i-mdi-chevron-right',
        onClick: submit
      }
    ],
    stacked: true
  }
})

const { setPublicDefault } = useBusinessTombstone()

const hiddenAlertTypes = [BusinessAlert.FROZEN, BusinessAlert.DISABLED, BusinessAlert.MISSINGINFO]
const alerts = computed(() => businessAlerts.value?.filter(val => !hiddenAlertTypes.includes(val.type)) || [])

onMounted(() => {
  fees.value = {}
  setBreadcrumbs([
    { to: registryHomeUrl + 'dashboard', label: t('label.bcregDash') },
    { to: localePath('/'), label: t('label.businessPersonSearch') },
    { label: businessId }
  ])
  businessStore.$reset()
  setPublicDefault(businessId)
})
</script>

<template>
  <div class="py-10">
    <Divide class="divide-y-3 *:py-10" :orientation="'vertical'">
      <BusinessAlerts v-if="alerts.length" :alert-info="alerts" />
      <HowToPurchaseDocs />
      <DocAccessSelection ref="documentSelect" />
      <BusinessLedgerWrapper
        :business-id
        hide-receipts
        locked-documents
        :locked-documents-tooltip="$t('text.selectBusinessSummaryAndFilingHistory')"
        :override-get-filing-documents-fn="getDocumentList"
      />
    </Divide>
  </div>
</template>
