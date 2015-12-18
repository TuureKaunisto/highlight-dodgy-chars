import sublime, sublime_plugin
users_whitelist = ''

def plugin_loaded():
    # Is there a way to get a reference to the plugin instance here?
    # It would be nice to avoid having to use the global user_whitelist variable.
    HighlightDodgyChars.getSettings()

class HighlightDodgyChars(sublime_plugin.EventListener): 

    def getSettings():
        global users_whitelist
        settings = sublime.load_settings('HighlightDodgyChars.sublime-settings')

        users_whitelist = settings.get('whitelist_chars')

        if isinstance(users_whitelist, list):
            users_whitelist = "".join(users_whitelist)

        # for some reason the sublime.IGNORECASE -flag did not work so lets
        # duplicate the chars as lower and upper :(
        users_whitelist += users_whitelist.upper()

    def on_modified_async(self, view):
        self.highlight(view)

    def on_load_async(self, view):
        # load highlights as soon as the file is opened
        self.highlight(view)

    def highlight(self, view):
        highlights = []
        whitelist = u'\n´\u0009' # allow newline, forward-tick and tabulator
        # search for non-ascii characters that are not on the whitelist
        needle = '[^\x00-\x7F'+whitelist+users_whitelist+']'

        # search the view
        for pos in view.find_all(needle):
            highlights.append(pos)

        # if something dodgy was found, highlight the dodgy parts
        if highlights:
            view.add_regions("zero-width-and-bad-chars", highlights, "invalid", "", sublime.DRAW_SOLID_UNDERLINE)
        else:
            view.erase_regions("zero-width-and-bad-chars") 