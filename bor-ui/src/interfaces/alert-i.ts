import type { AlertTypesE, AlertSeverityE } from '#imports'

export interface AlertI {
  severity: AlertSeverityE | undefined
  alertType: AlertTypesE | undefined
  text: string | undefined
  description: string | undefined
  date: any | undefined
}
