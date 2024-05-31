export default defineAppConfig({
  ui: {
    primary: 'blue',
    gray: 'bcGovGray',
    strategy: 'merge',
    accordion: {
      wrapper: 'divide-y',
      container: 'border-gray-400',
      default: {
        class: 'm-0 p-3 text-gray-900 font-bold bg-gray-100 hover:bg-gray-200 rounded-none'
      }
    },
    alert: {
      // NB: gap classes are applied to the div underneath the wrapper
      gap: 'max-w-[1360px] p-4 mx-auto',
      inner: 'pt-2',
      color: {
        yellow: {
          solid: 'bg-yellow-400 text-gray-900',
          soft: 'bg-yellow-50 text-gray-900'
        }
      },
      default: {
        closeButton: {
          icon: 'i-heroicons-x-mark-20-solid',
          variant: 'link',
          padded: false
        }
      }
    },
    button: {
      padding: 'p-0'
    },
    checkbox: {
      base: 'cursor-pointer',
      label: 'cursor-pointer'
    },
    formGroup: {
      error: 'text-red-600',
      help: 'text-gray-700'
    },
    input: {
      base: 'relative text-gray-900 border-0 border-b-[1px] border-gray-500 ring-0 focus:ring-0',
      placeholder: 'placeholder-gray-700',
      rounded: 'rounded-none rounded-t-md',
      size: {
        sm: 'h-[40px]',
        lg: 'h-[56px]'
      },
      color: {
        gray: {
          outline: 'bg-gray-100 ring-0 hover:bg-gray-200 hover:border-gray-600 ' +
            'focus:border-primary-500 focus:border-b-2 focus:ring-0'
        },
        primary: {
          outline: 'bg-primary-50 ring-0 border-primary-500 hover:bg-gray-200 focus:border-b-2 focus:ring-0'
        },
        red: {
          outline: 'bg-gray-100 ring-0 border-red-600 hover:bg-gray-200 ' +
            'focus:border-red-600 focus:border-b-2 focus:ring-0'
        }
      },
      icon: {
        base: 'text-gray-700',
        color: 'text-{color}-500',
        trailing: {
          padding: {
            sm: 'px-0 pr-2.5',
            md: 'px-0 pr-2.5',
            lg: 'px-0 pr-2.5',
            xl: 'px-0 pr-2.5'
          }
        }
      },
      trailing: {
        padding: {
          sm: 'pe-7',
          md: 'pe-7',
          lg: 'pe-7',
          xl: 'pe-7'
        }
      },
      default: {
        size: 'lg',
        color: 'gray',
        variant: 'outline'
      }
    },
    modal: {
      base: 'xs:min-w-[90vw] md:min-w-[720px] text-gray-700'
    },
    notification: {
      title: 'text-white',
      description: 'text-white',
      background: 'bg-gray-700',
      progress: {
        background: 'bg-transparent'
      },
      default: {
        closeButton: {
          class: 'hover:text-gray-100',
          color: 'gray'
        }
      }
    },
    notifications: {
      position: 'bottom-5 left-[40%]'
    },
    radio: {
      base: 'h-5 w-5 mt-[3px]',
      inner: 'ms-1',
      label: 'cursor-pointer text-base'
    },
    select: {
      base: 'bg-white border-b-[1px] border-gray-500 ring-0 focus:border-b-2 focus:ring-0',
      rounded: 'rounded-none rounded-t-md',
      size: {
        sm: 'h-[40px]',
        lg: 'h-[56px]'
      },
      color: {
        gray: {
          outline: 'bg-gray-100 ring-0 hover:bg-gray-200 hover:border-gray-600 ' +
            'focus:border-primary-500 focus:border-b-2 focus:ring-0',
          none: 'ring-0 hover:border-gray-600 focus:border-primary-500 focus:border-b-2 focus:ring-0'
        },
        primary: {
          outline: 'bg-primary-50 ring-0 border-primary-500 hover:bg-gray-200 focus:border-b-2 focus:ring-0',
          none: 'ring-0 border-primary-500 focus:border-b-2 focus:ring-0'
        },
        red: {
          outline: 'ring-0 border-red-600 hover:bg-gray-200 ' +
            'focus:border-red-600 focus:border-b-2 focus:ring-0'
        }
      },
      icon: {
        base: 'text-gray-700',
        trailing: {
          padding: {
            '2xs': 'px-0 pr-2',
            xs: 'px-0 pr-2.5',
            sm: 'px-0 pr-2.5'
          }
        }
      },
      trailing: {
        padding: {
          '2xs': 'pe-6',
          xs: 'pe-6',
          sm: 'pe-7'
        }
      },
      default: {
        size: 'lg',
        color: 'gray',
        variant: 'outline'
      }
    },
    selectMenu: {
      label: 'text-gray-700',
      rounded: 'rounded-none',
      padding: 'p-0',
      ring: 'ring-0',
      select: 'cursor-pointer inline-block',
      width: 'min-w-max',
      option: {
        padding: 'px-3 py-2',
        rounded: 'rounded-none',
        active: 'text-primary-500',
        selected: 'text-primary-500 bg-gray-100',
        icon: {
          active: 'text-primary-500'
        },
        selectedIcon: {
          base: 'text-primary-500'
        }
      }
    },
    tooltip: {
      base: 'h-full p-3',
      background: 'bg-gray-700',
      color: 'text-white',
      ring: 'ring-0',
      width: 'max-w-none',
      arrow: {
        ring: 'before:ring-0',
        background: 'before:bg-gray-700'
      }
    }
  }
})
