export const goToOpenBusiness = (identifier: string, modernized = false) => {
  const { accessLevel } = useSearchAccessStore()
  const { bconlineUrl, businessDashURL, registriesSearchUrl } = useRuntimeConfig().public

  if (modernized) {
    if (accessLevel !== SearchAccess.EXTENDED) {
      // will redirect to business search document purchase page for given identifier
      useBcrosNavigate().redirect(registriesSearchUrl, { identifier }, '_blank')
    } else {
      // will redirect to business dashboard for given identifier
      useBcrosNavigate().redirect(businessDashURL + identifier, {}, '_blank')
    }
  } else {
    useBcrosNavigate().redirect(bconlineUrl, {}, '_blank')
  }
}
