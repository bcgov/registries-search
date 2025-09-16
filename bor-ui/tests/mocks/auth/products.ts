import { ProductCode } from '../../../app/enums/product-code'
import { ProductStatus } from '../../../app/enums/product-status'

export const ProductsExtended: Product[] = [
  { code: ProductCode.BUSINESS_SEARCH, subscriptionStatus: ProductStatus.ACTIVE },
  { code: ProductCode.NDS, subscriptionStatus: ProductStatus.NOT_SUBSCRIBED },
  { code: ProductCode.CA_SEARCH, subscriptionStatus: ProductStatus.ACTIVE }
]

export const ProductsLimited: Product[] = [
  { code: ProductCode.BUSINESS_SEARCH, subscriptionStatus: ProductStatus.ACTIVE },
  { code: ProductCode.NDS, subscriptionStatus: ProductStatus.ACTIVE },
  { code: ProductCode.CA_SEARCH, subscriptionStatus: ProductStatus.NOT_SUBSCRIBED }
]

export const ProductsNone: Product[] = [
  { code: ProductCode.BUSINESS_SEARCH, subscriptionStatus: ProductStatus.NOT_SUBSCRIBED },
  { code: ProductCode.NDS, subscriptionStatus: ProductStatus.NOT_SUBSCRIBED },
  { code: ProductCode.CA_SEARCH, subscriptionStatus: ProductStatus.NOT_SUBSCRIBED }
]

export const ProductsPublic: Product[] = [
  { code: ProductCode.BUSINESS_SEARCH, subscriptionStatus: ProductStatus.ACTIVE },
  { code: ProductCode.NDS, subscriptionStatus: ProductStatus.NOT_SUBSCRIBED },
  { code: ProductCode.CA_SEARCH, subscriptionStatus: ProductStatus.NOT_SUBSCRIBED }
]
