<template>
  <Menu as="div" class="relative z-[200]">
    <div>
      <MenuButton class="flex flex-nowrap content-center p-2 hover:bg-primary-500/[0.2]">
        <slot name="menu-button-text">
          {{ menuButtonText || '' }}
        </slot>
        <UIcon class="ml-1 self-center text-xl" name="i-mdi-menu-down" />
      </MenuButton>
    </div>
    <transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <MenuItems :class="menuItemsClasses">
        <div class="divide-y-2 divide-bcGovGray-100 text-bcGovGray-700 min-w-[300px]">
          <div v-for="menuList, i in menuLists" :key="(menuList.header || '') + i" class="py-3" data-cy="menu-list">
            <slot :name="'menu-list-header-' + i">
              <h3 v-if="menuList.header" class="px-4 pb-2 font-bold text-bcGovGray-900" data-cy="menu-list-header">
                {{ menuList.header }}
              </h3>
            </slot>
            <BcrosHeaderMenuItem
              v-for="menuItem in menuList.items"
              :key="menuItem.label"
              :item-info="menuItem"
            />
          </div>
        </div>
      </MenuItems>
    </transition>
  </Menu>
</template>

<script setup lang="ts">
import { Menu, MenuButton, MenuItems } from '@headlessui/vue'
defineProps<{
  menuButtonText?: string
  menuLists?: {
    header?: string,
    items?: HeaderMenuItemI[]
  }[]
}>()

const menuItemsClasses = 'absolute right-0 top-0 origin-top-right rounded-md ' +
  'bg-white ring-1 ring-bcGovGray-200 shadow-xl'

</script>
