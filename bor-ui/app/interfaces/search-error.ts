export interface SearchError {
  category: ErrorCategory
  detail?: string
  message: string
  statusCode: number | null
  type?: ErrorCode
}
