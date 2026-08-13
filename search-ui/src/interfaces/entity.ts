import { BusinessStatuses, BusinessTypes, CorpTypeCd } from '@/enums'
import { ErrorI } from '@/interfaces';
import { AmalgamatedIntoI, StateFilingI } from '@/interfaces/legal-api-responses'

export interface EntityI {
  alternateNames?: { name: string, identifier: string }[]
  amalgamatedInto?: AmalgamatedIntoI,
  bn?: string,
  identifier: string,
  incorporationDate?: string,
  legalType: BusinessTypes | CorpTypeCd,
  name: string,
  status: BusinessStatuses,
  stateFiling?: string,
  _error?: ErrorI,
  _loading?: boolean,
  _stateFilingInfo?: StateFilingI,
  goodStanding: boolean,
  inDissolution: boolean
}