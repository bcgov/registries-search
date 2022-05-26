import { computed, reactive } from 'vue'
import { StatusCodes } from 'http-status-codes'
// bcregistry
import FeeServices from 'sbc-common-components/src/services/fee.services'
import { FilingData } from 'sbc-common-components/src/models'
// local
import { ErrorCategories, FeeCodes } from '@/enums'
import { CachedFeeItem, FeeI, FeesI } from '@/interfaces'

const fees = reactive({
  folioNumber: '',
  items: [],
  preSelection: null,
  _error: null
} as FeesI)

const _cachedFeeItems = [] as CachedFeeItem[]

export const useFeeCalculator = () => {
  const addFeeItem = async (code: FeeCodes, quantity: number) => {
    const itemAdded = _addCachedFeeItem(code, quantity)
    if (!itemAdded) {
      const feeInfo = await getFeeInfo(code)
      if (feeInfo) fees.items.push(feeInfo)
    }
  }
  const clearFees = () => {
    // keeps preselection
    fees.folioNumber = ''
    fees.items = []
    fees._error = null
  }
  const displayFee = (fee: number, noFee: boolean) => {
    if (fee === 0 && noFee) return 'No Fee'
    if (fee === 0) return '$ &#8211;'
    // split decimal for padding zeros
    const feeParts = String(fee).split('.')
    if (feeParts.length === 1) feeParts.push('00')
    // return formatted fee
    return `$${feeParts[0]}.${feeParts[1].padEnd(2, '0')}`
  }
  const getFeeInfo = async (code: FeeCodes): Promise<FeeI> => {
    // FUTURE support multiple fees
    // FUTURE make entity type an enum and pass it in
    const filingDataItem = { filingTypeCode: code, entityType: 'BUS' } as FilingData
    const url = sessionStorage.getItem('PAY_API_URL')
    const payResp = await FeeServices.getFee([filingDataItem], url)
    if (payResp && payResp.length > 0) {
      // future get description from fee code
      const item = {
        code: code,
        fee: payResp[0].fee,
        label: payResp[0].filingType,
        quantity: 1,
        serviceFee: payResp[0].serviceFees 
      }
      _cachedFeeItems.push({ [code]: item })
      return item
    }
    // only get here if error
    fees._error = {
      category: ErrorCategories.FEE_INFO,
      message: 'Unable to get fees.',
      statusCode: StatusCodes.NOT_FOUND,
      type: null
    }
    return null
  }
  const removeFeeItem = (code: FeeCodes, quantity: number) => {
    const item = fees.items.find(item => item.code === code)
    if (item) item.quantity -= quantity
    if (item && item.quantity < 1) {
      const items = fees.items.filter(item => item.code !== code)
      fees.items = items
    }
  }
  const totalFees = computed(() => {
    let totalFee = 0
    for (const i in fees.items) totalFee += (fees.items[i].fee * fees.items[i].quantity)
    return totalFee + totalServiceFee.value
  })
  const totalServiceFee = computed(() => {
    let totalServiceFee = 0
    for (const i in fees.items) totalServiceFee += fees.items[i].serviceFee
    return totalServiceFee
  })
  const _addCachedFeeItem = (code: FeeCodes, quantity: number) => {
    const itemSelectedAlready = fees.items.find(item => item.code === code)
    if (itemSelectedAlready) {
      itemSelectedAlready.quantity = quantity
      return true
    }
    const foundItem = _cachedFeeItems.find(item => Object.keys(item)[0] === code)
    if (foundItem) {
      foundItem[code].quantity = quantity
      fees.items.push(foundItem[code])
      return true
    }
    return false
  }
  return {
    fees,
    addFeeItem,
    clearFees,
    displayFee,
    getFeeInfo,
    removeFeeItem,
    totalFees
  }
}