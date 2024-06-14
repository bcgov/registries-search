import { type ControlColumnIconI, PersonControlTypeE } from '#imports'

export const convertDetailsToIcon = (details: string): ControlColumnIconI => {
  const t = useNuxtApp().$i18n.t
  switch (details) {
    case PersonControlTypeE.SHARES_BEN_OWNER:
    case PersonControlTypeE.VOTES_BEN_OWNER: {
      return {
        src: '/icons/shares-votes/beneficial-owner.svg',
        alt: t('text.control.icon.beneficialOwner'),
        tooltip: t('text.control.icon.beneficialOwner'),
        displayName: t('label.control.icon.beneficialOwner')
      }
    }
    case PersonControlTypeE.SHARES_INDIRECT:
    case PersonControlTypeE.VOTES_INDIRECT: {
      return {
        src: '/icons/shares-votes/indirect-control.svg',
        alt: t('text.control.icon.indirectControl'),
        tooltip: t('text.control.icon.indirectControl'),
        displayName: t('label.control.icon.indirectControl')
      }
    }
    case PersonControlTypeE.SHARES_REG_OWNER:
    case PersonControlTypeE.VOTES_REG_OWNER: {
      return {
        src: '/icons/shares-votes/registered-owner.svg',
        alt: t('text.control.icon.registeredOwner'),
        tooltip: t('text.control.icon.registeredOwner'),
        displayName: t('label.control.icon.registeredOwner')
      }
    }
    // directors control
    case PersonControlTypeE.DIRS_DIRECT: {
      return {
        src: '/icons/directors/direct-control.svg',
        alt: t('text.control.icon.directControl'),
        tooltip: t('text.control.icon.directControl'),
        displayName: t('label.control.icon.directControl')
      }
    }
    case PersonControlTypeE.DIRS_INDIRECT: {
      return {
        src: '/icons/directors/indirect-control.svg',
        alt: t('text.control.icon.indirectControl'),
        tooltip: t('text.control.icon.indirectControl'),
        displayName: t('label.control.icon.indirectControl')
      }
    }
    case PersonControlTypeE.DIRS_SIG_INFL: {
      return {
        src: '/icons/directors/significant-influence.svg',
        alt: t('text.control.icon.significantInfluence'),
        tooltip: t('text.control.icon.significantInfluence'),
        displayName: t('label.control.icon.significantInfluence')
      }
    }
    case PersonControlTypeE.OTHER: {
      return {
        src: '/icons/other.svg',
        alt: t('text.control.icon.other'),
        tooltip: t('text.control.icon.other'),
        displayName: t('label.control.other')
      }
    }

    default: {
      return null
    }
  }
}
