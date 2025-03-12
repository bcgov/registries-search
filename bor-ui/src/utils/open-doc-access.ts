export const goToOpenDocAccess = (docAccessItem: DocAccessI) => {
  const { businessSearchURL } = useRuntimeConfig().public
  useBcrosNavigate().redirect(businessSearchURL, { documentAccessRequestId: String(docAccessItem.id) }, '_blank')
}
