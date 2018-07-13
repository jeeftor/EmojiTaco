# encoding: utf-8

from workflow import Workflow3, ICON_INFO

def main(wf):
    if wf.update_available:

        wf.add_item('A newer version is available',
                    '↩ to install update',
                    autocomplete='workflow:update',
                    icon='update-available.png')

    query = None
    if len(wf.args):
        query = wf.args[0]

    log.debug('query : {!r}'.format(query))


    #
    # wf.add_item("workflow:magic", "List available magic arguments.", arg="workflow:magic",
    #             autocomplete="workflow:magic", icon=ICON_INFO)
    wf.add_item("workflow:help",
                "Open workflow’s help URL in default web browser. This URL is specified in the help_url argument to Workflow.",
                arg="workflow:help", autocomplete="workflow:help", icon=ICON_INFO)
    wf.add_item("workflow:openlog", "Open the Workflow’s log file in the default app.", arg="workflow:openlog",
                autocomplete="workflow:openlog", icon=ICON_INFO)

    wf.add_item("workflow:version", "Display the installed version of the workflow (if one is set).",
                arg="workflow:version", autocomplete="workflow:version", icon=ICON_INFO)
    wf.add_item("workflow:delcache", "Delete the Workflow’s cache.", arg="workflow:delcache",
                autocomplete="workflow:delcache", icon=ICON_INFO)
    wf.add_item("workflow:deldata", "Delete the Workflow’s saved data.", arg="workflow:deldata",
                autocomplete="workflow:deldata", icon=ICON_INFO)
    wf.add_item("workflow:delsettings",
                "Delete the Workflow’s settings file (which contains the data stored using Workflow.settings).",
                arg="workflow:delsettings", autocomplete="workflow:delsettings", icon=ICON_INFO)
    wf.add_item("workflow:foldingdefault", "Reset diacritic folding to workflow default", arg="workflow:foldingdefault",
                autocomplete="workflow:foldingdefault", icon=ICON_INFO)
    wf.add_item("workflow:foldingoff", "Never fold diacritics in search keys", arg="workflow:foldingoff",
                autocomplete="workflow:foldingoff", icon=ICON_INFO)
    wf.add_item("workflow:foldingon", "Force diacritic folding in search keys (e.g. convert ü to ue)",
                arg="workflow:foldingon", autocomplete="workflow:foldingon", icon=ICON_INFO)
    wf.add_item("workflow:opencache", "Open the Workflow’s cache directory.", arg="workflow:opencache",
                autocomplete="workflow:opencache", icon=ICON_INFO)
    wf.add_item("workflow:opendata", "Open the Workflow’s data directory.", arg="workflow:opendata",
                autocomplete="workflow:opendata", icon=ICON_INFO)
    wf.add_item("workflow:openterm", "Open a Terminal window in the Workflow’s root directory.",
                arg="workflow:openterm", autocomplete="workflow:openterm", icon=ICON_INFO)
    wf.add_item("workflow:openworkflow", "Open the Workflow’s root directory (where info.plist is).",
                arg="workflow:openworkflow", autocomplete="workflow:openworkflow", icon=ICON_INFO)
    wf.add_item("workflow:reset", "Delete the Workflow’s settings, cache and saved data.", arg="workflow:reset",
                autocomplete="workflow:reset", icon=ICON_INFO)
    wf.add_item("workflow:update",
                "Check for a newer version of the workflow using GitHub releases and install the newer version if one is available.",
                arg="workflow:update", autocomplete="workflow:update", icon=ICON_INFO)
    wf.add_item("workflow:noautoupdate", "Turn off automatic checks for updates.", arg="workflow:noautoupdate",
                autocomplete="workflow:noautoupdate", icon=ICON_INFO)
    wf.add_item("workflow:autoupdate", "Turn automatic checks for updates on.", arg="workflow:autoupdate",
                autocomplete="workflow:autoupdate", icon=ICON_INFO)
    wf.add_item("workflow:prereleases", "Enable updating the workflow to pre-release versions.",
                arg="workflow:prereleases", autocomplete="workflow:prereleases", icon=ICON_INFO)
    wf.add_item("workflow:noprereleases", "Disable updating the workflow to pre-release versions (default).",
                arg="workflow:noprereleases", autocomplete="workflow:noprereleases", icon=ICON_INFO)


    wf.send_feedback()


UPDATE_SETTINGS = {'github_slug': 'jeeftor/alfredToday'}
HELP_URL = 'https://github.com/jeeftor/alfredToday/blob/master/README.md'


if __name__ == '__main__':
    wf = Workflow3(libraries=['./lib'],
                   help_url=HELP_URL,
                   update_settings={
                       'github_slug': 'jeeftor/alfredToday',
                       'frequency': 7}
                   )
    log = wf.logger
    wf.run(main)