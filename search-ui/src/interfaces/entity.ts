import { BusinessStatuses, BusinessTypes, CorpTypeCd } from '@/enums'
import { ErrorI } from '@/interfaces';

export interface EntityI {
  bn?: string,
  identifier: string,
  incorporationDate?: string,
  legalType: BusinessTypes | CorpTypeCd,
  name: string,
  status: BusinessStatuses,
  _error?: ErrorI,
  _loading?: boolean,
  goodStanding: boolean
}