/** Manages account product data */
export const useAccountProductStore = defineStore('accountProduct', () => {
  const { $authApi } = useNuxtApp()
  const account = useConnectAccountStore()
  const activeProducts: Ref<Product[]> = ref([])

  /** Get all the current account products. */
  function getAccountProducts(): Promise<Product[]> {
    const config = { params: { include_hidden: true }, parseResponse: JSON.parse }
    return $authApi<Product[]>(`orgs/${account.currentAccount.id}/products`, config)
  }

  /** Check if the current account has the product. */
  function hasProductAccess(code: ProductCode) {
    // check if product code in activeProducts
    return !!activeProducts.value?.find(product => product.code === code)
  }

  /** Set the active products for the current account. */
  async function setActiveProducts() {
    try {
      const products = await getAccountProducts()
      activeProducts.value = products.filter(product => product.subscriptionStatus === ProductStatus.ACTIVE)
    } catch (error) {
      logFetchError(error, '[Account Product Store] - Error during setActiveProducts')
    }
  }

  function $reset() {
    activeProducts.value = []
  }

  return {
    activeProducts,
    setActiveProducts,
    hasProductAccess,
    $reset
  }
})
