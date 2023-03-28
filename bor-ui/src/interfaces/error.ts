// generic error interface
import { ErrorCode, ErrorCategory } from '@/enums'
export interface ErrorI {
  category: ErrorCategory,
  detail?: string,
  message: string,
  statusCode: number,
  type: ErrorCode
}
