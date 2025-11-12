<script setup lang="ts">
const { t } = useI18n()

const { currentAccount } = storeToRefs(useConnectAccountStore())

const businessStore = useBusinessStore()
const { business } = storeToRefs(businessStore)

const feeStore = useConnectFeeStore()
const { feesCached, loading: loadingFees } = storeToRefs(feeStore)

const searchFeeEntityType = 'BUS'
feeStore.initFees(
  [
    { code: SearchFeeCode.BSRCH, entityType: searchFeeEntityType, label: t(`feeLabel.${SearchFeeCode.BSRCH}`) },
    { code: SearchFeeCode.CGOOD, entityType: searchFeeEntityType, label: t(`feeLabel.${SearchFeeCode.CGOOD}`) },
    { code: SearchFeeCode.CSTAT, entityType: searchFeeEntityType, label: t(`feeLabel.${SearchFeeCode.CSTAT}`) },
    { code: SearchFeeCode.LSEAL, entityType: searchFeeEntityType, label: t(`feeLabel.${SearchFeeCode.LSEAL}`) },
    { code: SearchFeeCode.SBSRCH, entityType: searchFeeEntityType, label: t(`feeLabel.${SearchFeeCode.SBSRCH}`) }
  ],
  { label: t('label.selectFromAvailableDocuments') }
)

const isStaff = [AccountType.STAFF, AccountType.SBC_STAFF].includes(currentAccount.value.accountType)
const allowedSummaryCorpTypes = [
  CorpTypeCd.BENEFIT_COMPANY, CorpTypeCd.COOP, CorpTypeCd.SOLE_PROP, CorpTypeCd.PARTNERSHIP]

const getPurchaseItems = () => [
  {
    code: isStaff ? SearchFeeCode.SBSRCH : SearchFeeCode.BSRCH,
    value: false,
    disabled: !businessStore.isLegalType(allowedSummaryCorpTypes),
    tooltip: t('text.theseDocumentsWillBeAvailableSoon')
  },
  ...(
    !businessStore.isFirm() && business.value?.state === EntityState.ACTIVE
      ? [
        {
          code: SearchFeeCode.CGOOD,
          value: false,
          disabled: !business.value.goodStanding,
          tooltip: t('text.theCOGSisOnlyAvailableIf')
        },
        { code: SearchFeeCode.CSTAT, value: false }]
      : []
  ),
  { code: SearchFeeCode.LSEAL, value: false }
]

const purchaseItems = ref(getPurchaseItems())

watch(() => business.value?.identifier, () => {
  purchaseItems.value = getPurchaseItems()
})

const getFeeLabel = (code: SearchFeeCode) => {
  if ([SearchFeeCode.BSRCH, SearchFeeCode.SBSRCH].includes(code)) {
    return $t(`feeLabel.${code}`) + ' ' + t('text.paperOnlyNotIncluded')
  }
  return $t(`feeLabel.${code}`)
}

const getFeeTotal = (code: SearchFeeCode) => {
  if (code in feesCached.value || {}) {
    const priceFormat = new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' })
    return priceFormat.format(feesCached.value[code]!.filingFees)
  }
}

const addRemoveFee = (item: { code: SearchFeeCode, value: boolean }) => {
  if (item.value) {
    feeStore.addReplaceFee(item.code)
  } else {
    feeStore.removeFee(item.code)
  }
}
</script>

<template>
  <div>
    <h2>{{ $t('label.availableDocumentsToDownload') }}</h2>
    <UCard class="*:*:space-y-3">
      <div v-if="!loadingFees">
        <UTooltip
          v-for="item, i in purchaseItems"
          :key="i"
          arrow
          :content="{ align: 'start', side: 'top', sideOffset: 10 }"
          :disabled="!item.disabled"
          :text="item.tooltip"
          :ui="{ content: 'max-w-xs h-full py-3 *:text-wrap *:whitespace-normal' }"
        >
          <div class="flex">
            <UCheckbox
              v-model="item.value"
              :label="getFeeLabel(item.code)"
              :disabled="item.disabled"
              :ui="{ label: 'font-bold' }"
              @change="addRemoveFee(item)"
            />
            <p class="ml-auto">
              <strong>{{ getFeeTotal(item.code) }}</strong>
            </p>
          </div>
        </UTooltip>
      </div>
      <div v-else class="space-y-5">
        <USkeleton class="h-5 w-full rounded" />
        <USkeleton class="h-5 w-full rounded" />
        <USkeleton class="h-5 w-full rounded" />
        <USkeleton class="h-5 w-full rounded" />
      </div>
    </UCard>
  </div>
</template>
