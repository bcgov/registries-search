export const goToOpenBusiness = (identifier: string, modernized = false) => {
  const { accessLevel } = useSearchAccessStore()
  const { bconlineUrl, businessDashUrl, registriesSearchUrl } = useRuntimeConfig().public

  if (modernized) {
    if (accessLevel !== SearchAccess.EXTENDED) {
      // will redirect to business search document purchase page for given identifier
      useBcrosNavigate().redirect(registriesSearchUrl, { identifier }, '_blank')
    } else {
      // will redirect to business dashboard for given identifier
      useBcrosNavigate().redirect(businessDashUrl + identifier, {}, '_blank')
    }
  } else {
    useBcrosNavigate().redirect(bconlineUrl, {}, '_blank')
  }
}
