import { ActionContext } from 'vuex'
import { BaseStateI } from './base-state'

export interface ActionI {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (x: ActionContext<BaseStateI, any>, y: any): void
}
