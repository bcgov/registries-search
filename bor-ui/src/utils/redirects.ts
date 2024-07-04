export const goToOpenBusiness = (identifier: string) => {
  const { businessSearchURL } = useRuntimeConfig().public
  useBcrosNavigate().redirect(businessSearchURL, { identifier }, '_blank')
}
