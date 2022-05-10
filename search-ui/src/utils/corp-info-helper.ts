import { CorpInfoArray } from '@/resources'
import { CorpTypeCd } from '@/enums'
import { CorpInfo } from '@/types'
  /**
   * Given corp type code, returns the corp info object.
   * @param cd the corp type code to get
   * @returns the corp info object (or undefined if not found)
   */
  export function GetCorpInfoObject (cd: CorpTypeCd): CorpInfo {
    return CorpInfoArray.find(obj => (cd === obj.corpTypeCd))
  }
  
  /**
   * Given corp type code, returns corp full description.
   * @param cd the corp type code to get
   * @returns the description (or '' if not found)
   */
  export function GetCorpFullDescription (cd: CorpTypeCd): string {
    const item = CorpInfoArray.find(obj => (cd === obj.corpTypeCd))
    return (item && item.fullDesc) || ''
  }
  
  /**
   * Given corp type code, returns corp "numbered" description.
   * @param cd the corp type code to get
   * @returns the description (or '' if not found)
   */
  export function GetCorpNumberedDescription (cd: CorpTypeCd): string {
    const item = CorpInfoArray.find(obj => (cd === obj.corpTypeCd))
    return (item && item.numberedDesc) || ''
  }