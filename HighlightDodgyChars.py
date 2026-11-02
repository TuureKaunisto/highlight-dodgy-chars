#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sublime, sublime_plugin

SETTINGS_LISTENER_KEY = "highlight_dodgy_chars"


class HighlightDodgyChars(sublime_plugin.EventListener):
    def on_activated(self, view):
        self.get_settings()
        self.view = view
        self.syntax = view.settings().get("syntax")
        self.has_been_modified = False
        self.delay_update = False

        self.phantom_set = sublime.PhantomSet(view)

        # the syntax can change while the view stays focused, e.g. from the
        # status bar menu or when a new file is saved as .md
        view_settings = view.settings()
        view_settings.clear_on_change(SETTINGS_LISTENER_KEY)
        view_settings.add_on_change(
            SETTINGS_LISTENER_KEY, lambda: self.on_view_settings_changed(view)
        )

        # highlight dodgy characters when the file is opened
        self.highlight()

    def on_view_settings_changed(self, view):
        syntax = view.settings().get("syntax")
        if view.id() == self.view.id() and syntax != self.syntax:
            self.syntax = syntax
            sublime.set_timeout(self.highlight, 0)

    def syntax_is_disabled(self):
        # match on the name of the syntax file, which is all ST3 exposes
        path = self.view.settings().get("syntax") or ""
        names = [os.path.splitext(os.path.basename(path))[0]]

        # ST4 also knows the name shown in the status bar
        if hasattr(self.view, "syntax"):
            syntax = self.view.syntax()
            if syntax:
                names.append(syntax.name)

        return any(name.lower() in self.disabled_syntaxes for name in names)

    def get_settings(self):
        settings = sublime.load_settings("HighlightDodgyChars.sublime-settings")

        self.whitelist = settings.get("whitelist_chars")

        if isinstance(self.whitelist, list):
            self.whitelist = "".join(self.whitelist)

        if self.whitelist is None:
            self.whitelist = ""

        # for some reason the sublime.IGNORECASE -flag did not work so lets
        # duplicate the chars as lower and upper :(
        self.whitelist += self.whitelist.upper()

        disabled_syntaxes = settings.get("disabled_syntaxes") or []
        self.disabled_syntaxes = [name.lower() for name in disabled_syntaxes]

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
        self.delay_update = False
        if self.has_been_modified:
            self.has_been_modified = False
            self.highlight()

    def highlight(self):
        if self.view.settings().get("terminus_view"):
            return

        if self.syntax_is_disabled():
            # clear any markers left from before the syntax changed
            self.phantom_set.update([])
            return

        phantoms = []
        # allow newline, forward-tick and tabulator
        default_whitelist = "\n´\u0009"
        # search for non-ascii characters that are not on the whitelist
        needle = "[^\x00-\x7F" + default_whitelist + self.whitelist + "]"

        # search the view
        for pos in self.view.find_all(needle):
            phantoms.append(
                sublime.Phantom(
                    pos,
                    '<span style="color: var(--pinkish);">!</span>',
                    sublime.LAYOUT_INLINE,
                )
            )

        # if something dodgy was found, highlight the dodgy parts
        self.phantom_set.update(phantoms)
