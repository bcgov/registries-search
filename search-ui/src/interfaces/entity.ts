import { BusinessStatuses, BusinessTypes, CorpTypeCd } from '@/enums'
import { ErrorI } from '@/interfaces';

export interface EntityI {
  bn?: string,
  identifier: string,
  incorporationDate: string,
  legalType: BusinessTypes | CorpTypeCd,
  name: string,
  state: BusinessStatuses,
  _error: ErrorI,
  _loading: boolean,
}