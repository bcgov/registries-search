import { ErrorCategoryE } from '~/enums/error-category-e'
import { ErrorCodeE } from '~/enums/error-code-e'

export interface ErrorI {
  category: ErrorCategoryE,
  detail?: string,
  message: string,
  statusCode: number | null,
  type?: ErrorCodeE
}
