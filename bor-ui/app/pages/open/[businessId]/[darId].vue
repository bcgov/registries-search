<script setup lang="ts">
const { t } = useI18n()
const localePath = useLocalePath()

const { params, query } = useRoute()
const businessId = params.businessId as string
const darId = params.darId as string
const status = query.status as string
const registryHomeUrl = useRuntimeConfig().public.registryHomeUrl

definePageMeta({
  layout: 'search-view-docs',
  middleware: 'connect-auth',
  onAccountChange: (_oldAccount: ConnectAccount, newAccount: ConnectAccount) => {
    useConnectAccountStore().switchCurrentAccount(newAccount.id)
    useBcrosNavigate().redirect(useRuntimeConfig().public.baseUrl)
    return true
  }
})

const docAccessStore = useDocAccessStore()
const { docAccess, docAccessLoading } = storeToRefs(docAccessStore)
const date = computed(() => {
  const date = toDate(docAccess.value?.paymentCompletionDate || '')
  return date ? toPacificDateTime(date) : `[${t('text.unknown')}]`
})

const { setPublicDefault } = useBusinessTombstone()

const { getDocAccessDocument, getDocumentList } = useBusinessSearchApi()

const getFilingDocument = async (doc: BusinessDocument, businessId: string, filingId: string | number) => {
  return await getDocAccessDocument(businessId, doc.link.split('/').pop()!, filingId) as Blob
}

const downloadingKey = ref<string | undefined>(undefined)
const download = async (document: Doc) => {
  downloadingKey.value = document.documentKey
  const documentBlob = await getDocAccessDocument(businessId, document.documentKey)
  downloadFile(documentBlob, t(`docAccess.${document.documentType}`) + '.pdf')
  downloadingKey.value = undefined
}

const showLedger = computed(() => {
  return docAccess.value?.paymentCompletionDate && docAccess.value.documents.find(
    val => val.documentType === DocAccessType.BUSINESS_SUMMARY_FILING_HISTORY)
})

onMounted(() => {
  if (status === 'UEFZTUVOVF9DQU5DRUxMRUQ=') {
    // payment cancelled
    useRouter().push(localePath(`/open/${businessId}`))
  }
  setBreadcrumbs([
    { to: registryHomeUrl + 'dashboard', label: t('label.bcregDash') },
    { to: localePath('/'), label: t('label.businessPersonSearch') },
    { to: localePath(`/open/${businessId}`), label: businessId },
    { label: t('label.purchasedDocuments') }
  ])
  setPublicDefault(businessId)
  docAccessStore.init(darId)
})
</script>

<template>
  <div class="py-10">
    <div v-if="!docAccessLoading" class="">
      <Divide class="divide-y-3 *:py-5" orientation="vertical">
        <div class="space-y-5">
          <h2>{{ $t('text.purchasedDocumentsAsOf', { date }) }}</h2>
          <p>{{ $t('text.yourDocumentsAreNowAvailable') }}</p>
          <p>
            {{ $t('text.ifYouWishToPurchaseAdditional') }}
            <UButton
              class="p-0 underline text-base"
              :label="$t('text.conductANewSearch')"
              :to="localePath(`/open/${businessId}`)"
              variant="link"
            />
          </p>
        </div>
        <div class="space-y-5">
          <div>
            <h2>{{ $t('label.businessDocuments') }}</h2>
            <div class="p-5 bg-shade-inverted rounded space-y-2">
              <div v-for="doc in docAccess?.documents" :key="doc.id">
                <UButton
                  :label="$t(`docAccess.${doc.documentType}`)"
                  :loading="downloadingKey === doc.documentKey"
                  variant="ghost"
                  icon="i-mdi-file-pdf-outline"
                  @click.stop="download(doc)"
                />
              </div>
            </div>
          </div>
          <BusinessLedgerWrapper
            v-if="showLedger"
            :business-id
            :date="docAccess?.paymentCompletionDate"
            hide-receipts
            :override-get-document-fn="getFilingDocument"
            :override-get-filing-documents-fn="getDocumentList"
          >
            <template #header>
              <h2>{{ $t('label.historyDocuments') }}</h2>
            </template>
          </BusinessLedgerWrapper>
        </div>
      </Divide>
    </div>
    <div v-else class="space-y-5">
      <USkeleton class="h-15 w-full rounded" />
      <USkeleton class="h-15 w-full rounded" />
      <USkeleton class="h-15 w-full rounded" />
    </div>
  </div>
</template>
