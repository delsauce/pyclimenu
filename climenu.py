#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
This module is used to create *simple* menu-based CLI programs in Python.

This package is **highly** inspired by Click (http://click.pocoo.org).
'''

# Imports #####################################################################
from __future__ import print_function
import os
import sys

# Metadata ####################################################################
__author__ = 'Timothy McFadden'
__creationDate__ = '06-APR-2017'
__version__ = '1.0.0'


# Globals #####################################################################
__all__ = ['menu', 'group', 'settings']
(IS_WIN, IS_LIN) = ('win' in sys.platform, 'lin' in sys.platform)
MENU_ITEMS = []


def _show_main_menu(menu_items):
    '''Show the main menu and return the selected item.'''

    while True:
        print(settings.text['main_menu_title'])

        for index, menu_group in enumerate(menu_items):
            print("%2i : %s" % (index + 1, menu_group.title))

        print()
        value = get_user_input(settings.text['main_menu_prompt'])

        if value in settings.back_values:
            return None

        if not(value.isdigit()) or (int(value) > len(menu_items)):
            print(settings.text['invalid_selection'])
            continue

        return menu_items[int(value) - 1]


def _show_group_menu(menu_group):
    '''Show a submenue and return the selected item.'''
    while True:
        print(menu_group.title)

        submenu_items = menu_group.menus
        for index, submenu in enumerate(submenu_items):
            print("%2i : %s" % (index + 1, submenu.title))

        print()
        value = get_user_input(settings.text['submenu_prompt'])

        if value in settings.back_values:
            return None

        if not(value.isdigit()) or (int(value) > len(submenu_items)):
            print(settings.text['invalid_selection'])
            continue

        return submenu_items[int(value) - 1]


def run():
    '''
    Runs the menuing system.
    '''
    menu_stack = []
    current_group = None

    if not MENU_ITEMS:
        raise ValueError("No menu items defined")

    while True:
        # Clear the screen in-between each menu
        if settings.clear_screen:
            clear_screen()

        if not current_group:
            menu_item = _show_main_menu(MENU_ITEMS)
            if not menu_item:
                break
        else:
            menu_item = _show_group_menu(current_group)

        if (not menu_item) and menu_stack:
            back_one = menu_stack.pop()
            if back_one != current_group:
                current_group = back_one
            elif menu_stack:
                # Pop another one off
                current_group = menu_stack.pop()
            else:
                # Show the main menu (nothing left in the stack)
                current_group = None
            continue

        # Check for a sub-menu.  Sub-menu's don't
        # have a callback, so just set the current
        # group and loop.
        if isinstance(menu_item, MenuGroup):
            menu_stack.append(menu_item)
            current_group = menu_item
            continue

        # If we should show the *main* menu, then
        # ``menu_item`` will be None here.
        if menu_item:
            menu_item.callback()
            get_user_input(settings.text['continue'])
        else:
            # Nothing left in the stack; make
            # ``current_group == None`` so we'll
            # show the main menu the next time through
            # the loop.
            current_group = None


def clear_screen():
    '''Clears the terminal window'''
    if IS_WIN:
        os.system('cls')
    elif IS_LIN:
        os.system('clear')
    else:
        raise NotImplementedError("Your platform has not been implemented: %s" % sys.platform)


def get_user_input(prompt=None, test_value=None):
    '''
    Prompt the user for input.

    :param str prompt: The text to show the user
    :param var test_value: If this is not none, the user will not be prompted
        and this value is returned.
    '''
    if prompt:
        print(prompt, end='')

    if test_value is not None:
        return test_value

    if sys.version_info.major == 2:
        return raw_input()
    else:
        return input()


class Menu(object):
    '''A sinlge menu item with a callback'''
    def __init__(self, title, callback):
        self.callback = callback
        self.title = title


class MenuGroup(object):
    '''A group of Menu items'''
    def __init__(self, title, menus=None):
        self.title = title
        self.menus = menus or []

    def menu(self, *args, **kwargs):  # pylint: disable=W0613
        '''Decorator to add a menu item to our list'''
        def decorator(decorated_function):
            '''create a menu item decorator'''
            menu_ = Menu(
                kwargs.get('title') or decorated_function.__doc__,
                callback=decorated_function)
            self.menus.append(menu_)
            return menu_
        return decorator

    def group(self, *args, **kwargs):  # pylint: disable=W0613
        '''Decorator to add a menu group to our list'''
        def decorator(decorated_function):
            '''create a menu group decorator'''
            menu_ = MenuGroup(kwargs.get('title') or decorated_function.__doc__)
            self.menus.append(menu_)
            return menu_
        return decorator


def group(title=None):
    '''A decorator to create a new MenuGroup'''
    def decorator(decorated_function):
        '''create a menu group decorator'''
        group_ = MenuGroup(title or decorated_function.__doc__)
        MENU_ITEMS.append(group_)
        return group_
    return decorator


def menu(title=None):
    '''A decorator to create a single menu item'''
    def decorator(decorated_function):
        '''create a menu item decorator'''
        menu_ = Menu(title or decorated_function.__doc__, callback=decorated_function)
        MENU_ITEMS.append(menu_)
        return menu_
    return decorator


class Settings(object):
    '''
    This class is used to store the settings for ``climenu``.
    '''
    clear_screen = True
    text = {
        'main_menu_title': 'Main Menu',
        'main_menu_prompt': 'Enter the selection (0 to exit): ',

        'submenu_prompt': 'Enter the selection (0 to return): ',

        'invalid_selection': 'Invalid selection.  Please try again. ',

        'continue': 'Press Enter to continue: ',
    }

    # Add ``''`` to this list to go back one level if the user doesn't
    # enter anything
    back_values = ['0']


settings = Settings()  # pylint: disable=C0103