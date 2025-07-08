export const getAlertHeader = function(alert: Partial<AlertI>): string {
  const t = useNuxtApp().$i18n.t
  return t(alert.alertType ? 'alerts.headers.' + alert.alertType : alert.text)
}

export const getAlertIcon = function(alert: Partial<AlertI>): string {
  if (alert.alertType) {
    return 'i-mdi-alert'
  }

  switch (alert.severity?.toLowerCase()) {
    case 'error':
      return 'i-mdi-alert-circle'
    case 'warning':
      return 'i-mdi-alert'
    case 'info':
      return 'i-mdi-information'
    case 'success':
      return 'i-mdi-check'
    default:
      return 'i-mdi-alert-circle'
  }
}

export const getAlertColour = function(alert: Partial<AlertI>): string {
  if (alert.alertType) {
    return 'text-yellow-500'
  }

  switch (alert.severity?.toLowerCase()) {
    case 'error':
      return 'text-red-500'
    case 'warning':
      return 'text-yellow-500'
    case 'info':
      return 'text-blue-500'
    case 'success':
      return 'text-green-500'
    default:
      return 'text-yellow-500'
  }
}
