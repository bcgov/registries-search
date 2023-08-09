import { ProductCode, ProductStatus } from '@/enums'

export interface AuthApiProductI {
  code: ProductCode
  subscriptionStatus: ProductStatus
  // more unused vars in api response that we don't use
}
