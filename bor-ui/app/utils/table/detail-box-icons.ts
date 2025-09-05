import { type ControlColumnIcon, PersonControlType } from '#imports'
// @ts-expect-error - Cannot find module due to ts not recognizing the alias
import BeneficialOwnerIcon from 'BeneficialOwnerIcon'
// @ts-expect-error - Cannot find module due to ts not recognizing the alias
import DirectorsDirectControlIcon from 'DirectorsDirectControlIcon'
// @ts-expect-error - Cannot find module due to ts not recognizing the alias
import DirectorsIndirectControlIcon from 'DirectorsIndirectControlIcon'
// @ts-expect-error - Cannot find module due to ts not recognizing the alias
import DirectorsSignificanInfluenceIcon from 'DirectorsSignificanInfluenceIcon'
// @ts-expect-error - Cannot find module due to ts not recognizing the alias
import IndirectControlIcon from 'IndirectControlIcon'
// @ts-expect-error - Cannot find module due to ts not recognizing the alias
import RegisteredOwnerIcon from 'RegisteredOwnerIcon'
// @ts-expect-error - Cannot find module due to ts not recognizing the alias
import OtherIcon from 'OtherIcon'

export const convertDetailsToIcon = (details: string | undefined): ControlColumnIcon | undefined => {
  const t = useNuxtApp().$i18n.t
  switch (details) {
    case PersonControlType.SHARES_BEN_OWNER:
    case PersonControlType.VOTES_BEN_OWNER: {
      return {
        src: BeneficialOwnerIcon,
        alt: t('text.control.icon.beneficialOwner'),
        tooltip: t('text.control.icon.beneficialOwner'),
        displayName: t('text.control.icon.beneficialOwnerDisplay')
      }
    }
    case PersonControlType.SHARES_INDIRECT:
    case PersonControlType.VOTES_INDIRECT: {
      return {
        src: IndirectControlIcon,
        alt: t('text.control.icon.indirectControl'),
        tooltip: t('text.control.icon.indirectControl'),
        displayName: t('text.control.icon.indirectControlDisplay')
      }
    }
    case PersonControlType.SHARES_REG_OWNER:
    case PersonControlType.VOTES_REG_OWNER: {
      return {
        src: RegisteredOwnerIcon,
        alt: t('text.control.icon.registeredOwner'),
        tooltip: t('text.control.icon.registeredOwner'),
        displayName: t('text.control.icon.registeredOwnerDisplay')
      }
    }
    // directors control
    case PersonControlType.DIRS_DIRECT: {
      return {
        src: DirectorsDirectControlIcon,
        alt: t('text.control.icon.directControl'),
        tooltip: t('text.control.icon.directControl'),
        displayName: t('text.control.icon.directControlDisplay')
      }
    }
    case PersonControlType.DIRS_INDIRECT: {
      return {
        src: DirectorsIndirectControlIcon,
        alt: t('text.control.icon.indirectControlDir'),
        tooltip: t('text.control.icon.indirectControlDir'),
        displayName: t('text.control.icon.indirectControlDisplay')
      }
    }
    case PersonControlType.DIRS_SIG_INFL: {
      return {
        src: DirectorsSignificanInfluenceIcon,
        alt: t('text.control.icon.significantInfluence'),
        tooltip: t('text.control.icon.significantInfluence'),
        displayName: t('text.control.icon.significantInfluenceDisplay')
      }
    }
    case PersonControlType.OTHER: {
      return {
        src: OtherIcon,
        alt: t('text.control.icon.other'),
        tooltip: t('text.control.icon.other'),
        displayName: t('label.other')
      }
    }

    default: {
      return undefined
    }
  }
}
