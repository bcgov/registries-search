import { BusinessStateE } from '~/enums/business-state-e'
import { BusinessTypeE } from '~/enums/business-type-e'

export interface BusinessI {
  adminFreeze: boolean
  alternateNames: { operatingName: string }[]
  goodStanding: boolean
  identifier: string
  legalName: string
  legalType: BusinessTypeE
  state: BusinessStateE
  taxId?: string
}
