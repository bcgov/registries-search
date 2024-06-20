import { BusinessStatuses, BusinessTypes, CorpTypeCd } from '@/enums'
import { ErrorI } from '@/interfaces';

export interface EntityI {
  alternateNames?: { name: string, identifier: string }[]
  bn?: string,
  identifier: string,
  incorporationDate?: string,
  legalType: BusinessTypes | CorpTypeCd,
  name: string,
  status: BusinessStatuses,
  _error?: ErrorI,
  _loading?: boolean,
  goodStanding: boolean,
  inDissolution: boolean
}