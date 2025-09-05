/* eslint-disable max-len */
export default defineAppConfig({
  connect: {
    header: {
      localeSelect: false
    }
  },
  ui: {
    accordion: {
      slots: {
        root: 'divide-y',
        item: 'border-gray-400',
        body: 'text-neutral p-3',
        trigger: 'm-0 p-3 text-neutral-highlighted font-bold bg-shade hover:bg-shade-highlighted rounded-none'
      }
    },
    badge: {
      compoundVariants: [
        {
          color: 'neutral',
          variant: 'solid',
          class: 'bg-shade-secondary text-highlighted'
        }
      ]
    },
    checkbox: {
      slots: {
        base: 'group-hover:before:bg-transparent group-active:before:bg-transparent has-data-[state=checked]:hover:before:bg-transparent has-data-[state=checked]:active:before:bg-transparent'
      }
    },
    input: {
      slots: {
        trailingIcon: 'text-neutral'
      }
    },
    selectMenu: {
      slots: {
        base: 'items-start',
        content: 'rounded-sm min-w-fit',
        group: 'px-0 py-2',
        trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200 text-(--ui-text) group-data-[state=open]:text-primary group-focus:text-primary',
        item: 'my-0.75 min-w-[150px] text-neutral-highlighted before:rounded-none data-highlighted:not-data-disabled:text-primary data-highlighted:not-data-disabled:before:bg-shade data-[state=checked]:text-primary data-[state=checked]:bg-blue-50',
        itemLeadingIcon: 'group-data-[state=checked]:text-primary group-data-highlighted:not-data-disabled:text-primary text-neutral-highlighted'
      },
      variants: {
        variant: {
          bcGov: 'peer rounded-t-sm rounded-b-none bg-shade focus:ring-0 focus:outline-none shadow-input data-[state=open]:shadow-input-focus focus:shadow-input-focus text-neutral-highlighted'
        }
      },
      defaultVariants: {
        color: 'primary',
        variant: 'bcGov'
      }
    },
    toast: {
      slots: {
        root: 'bg-neutral text-inverted',
        progress: 'bg-transparent',
        title: 'text-inverted',
        close: 'hover:text-shade'
      }
    }
  }
})
