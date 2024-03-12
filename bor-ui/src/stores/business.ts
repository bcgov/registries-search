import Axios from 'axios'
import { StatusCodes } from 'http-status-codes'
import { defineStore } from 'pinia'

/** Manages bcros business data */
export const useBcrosBusiness = defineStore('bcros/business', () => {
  const currentBusiness: Ref<BusinessI> = ref({} as BusinessI)
  const currentFolioNumber: Ref<string> = ref('')

  const currentBusinessIdentifier = computed((): string => currentBusiness.value.identifier)
  const currentBusinessName = computed((): string => {
    if (currentBusiness.value.alternateNames && currentBusiness.value.legalType === BusinessTypeE.SP) {
      return currentBusiness.value.alternateNames[0].operatingName
    }
    return currentBusiness.value.legalName
  })
  const currentBusinessContact = ref({} as ContactBusinessI)
  // errors
  const errors: Ref<ErrorI[]> = ref([])
  // api request variables
  const axios = addAxiosInterceptors(Axios.create())
  const apiURL = useRuntimeConfig().public.legalApiURL
  const authApiURL = useRuntimeConfig().public.authApiURL

  /** Return the business details for the given identifier */
  async function getBusinessDetails (identifier: string, params?: object) {
    return await axios.get<{ business: BusinessI }>(`${apiURL}/businesses/${identifier}`, { params })
      .then((response) => {
        const data = response?.data
        if (!data || !data.business) { throw new Error(`Invalid LEGAL API response ${data}`) }
        return data.business
      })
      .catch((error) => {
        console.warn('Error fetching business details for', identifier)
        errors.value.push({
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          category: ErrorCategoryE.ENTITY_BASIC
        })
      })
  }

  /** Return the business contacts for the given identifier */
  async function getBusinessContact (identifier: string, params?: object) {
    // NOTE: this data will be moved to the legal-api eventually
    return await axios.get<ContactsBusinessResponseI>(`${authApiURL}/entities/${identifier}`, { params })
      .then((response) => {
        const data = response?.data
        if (!data || !data.contacts) { throw new Error(`Invalid AUTH API response ${data}`) }
        if (data.contacts.length === 0) { return {} as ContactBusinessI }

        if (data?.folioNumber) {
          currentFolioNumber.value = data.folioNumber
        }

        return {
          businessIdentifier: data.businessIdentifier,
          ...data.contacts[0]
        }
      })
      .catch((error) => {
        console.warn('Error fetching business contacts for', identifier)
        errors.value.push({
          statusCode: error?.response?.status || StatusCodes.INTERNAL_SERVER_ERROR,
          message: error?.response?.data?.message,
          category: ErrorCategoryE.ENTITY_BASIC
        })
      })
  }

  async function loadBusiness (identifier: string, force = false) {
    const businessCached = currentBusiness.value && identifier === currentBusinessIdentifier.value
    if (!businessCached || force) {
      currentBusiness.value = await getBusinessDetails(identifier, { slim: true }) || {} as BusinessI
    }
  }

  async function loadBusinessContact (identifier: string, force = false) {
    const contactCached = currentBusinessContact.value && identifier === currentBusinessContact.value.businessIdentifier
    if (!contactCached || force) {
      currentBusinessContact.value = await getBusinessContact(identifier) || {} as ContactBusinessI
    }
  }

  return {
    currentBusiness,
    currentBusinessIdentifier,
    currentBusinessName,
    currentBusinessContact,
    currentFolioNumber,
    getBusinessContact,
    getBusinessDetails,
    loadBusiness,
    loadBusinessContact
  }
})
