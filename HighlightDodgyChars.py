#!/usr/bin/python
# -*- coding: utf-8 -*-
import sublime, sublime_plugin

class HighlightDodgyChars(sublime_plugin.EventListener): 
    def on_activated(self, view):
        self.get_settings()
        self.view = view
        self.has_been_modified = False
        self.delay_update = False

        # highlight dodgy characters when the file is opened
        self.highlight()

    def get_settings(self):
        settings = sublime.load_settings('HighlightDodgyChars.sublime-settings')

        self.whitelist = settings.get('whitelist_chars')

        if isinstance(self.whitelist, list):
            self.whitelist = ''.join(self.whitelist)

        if self.whitelist is None:
            self.whitelist = ''

        # for some reason the sublime.IGNORECASE -flag did not work so lets
        # duplicate the chars as lower and upper :(
        self.whitelist += self.whitelist.upper()

    def on_modified_async(self, view):
        # call highlight max 4 times a second
        if self.delay_update:
            # if a modification happens during cooldown, an update is needed afterwards
            self.has_been_modified = True
        else:
            self.highlight()
            # 250 ms cooldown
            self.delay_update = True
            sublime.set_timeout(self.end_cooldown, 250)

    def end_cooldown(self):
        self.delay_update = False;
        if self.has_been_modified:
            self.has_been_modified = False;
            self.highlight()

    def highlight(self):
        # allow newline, forward-tick and tabulator
        default_whitelist = u'\n´\u0009'
        # search for non-ascii characters that are not on the whitelist
        needle = '[^\x00-\x7F' + default_whitelist + self.whitelist + ']'
        
        self.view.add_regions('HighlightDodgyCharsRegion', self.view.find_all(needle), "invalid", "", sublime.DRAW_EMPTY | sublime.DRAW_NO_OUTLINE
