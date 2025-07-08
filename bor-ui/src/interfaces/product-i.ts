import type { ProductCodeE, ProductStatusE } from '#imports'

export interface ProductI {
  code: ProductCodeE
  subscriptionStatus: ProductStatusE
  // more unused vars in api response that we don't use
}
