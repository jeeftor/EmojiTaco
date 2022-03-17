"""File Download wrapper."""
from __future__ import annotations

import os
import sys
from typing import Any

from workflow import Workflow3
from workflow.background import is_running, run_in_background


def string_from_percent(pct: float) -> str | None:
    """Return a fancy string to show in the workflow from the count item."""
    # blue = "\\U0001F535\\U0000FE0F"
    white = "\\U000026AA\\U0000FE0F"
    black = "\\U000026AB\\U0000FE0F"

    ret: str = (
        white
        + white
        + white
        + white
        + white
        + white
        + white
        + white
        + white
        + white
        + white
        + black
        + black
        + black
        + black
        + black
        + black
        + black
        + black
        + black
        + black
    )

    mod = 2 * (10 - (int(pct / 10) % 10))

    # encoding = 'UTF-8'
    return ret.decode("unicode_escape")[mod:][0:20]


def build_wf_entry(wf: Workflow3) -> None:
    """Build workflow entry."""
    if is_running("bg"):
        """Update status"""
        phase = wf.stored_data("phase")
        log.info("PHASE: ", phase)
        if phase != "done":
            wf.rerun = 0.5
        if phase == "downloading":
            pct = None
            while pct is None:
                try:
                    pct = wf.stored_data("download_percent")
                except:
                    pass

            progress = wf.stored_data("download_progress")
            file = wf.stored_data("download_file")

            # wf.rerun = 0.5

            title = f"Downloading {file} [{progress}]"
            subtitle = string_from_percent(pct) + " " + str(pct) + "%"
            wf.add_item(title, subtitle=subtitle)

        if phase == "processing":

            try:
                emoji_count = wf.stored_data("emoji_count")
                subtitle = f"Parsed {emoji_count} emoji"
            except:
                subtitle = "Parsed ... emoji"
                pass

            title = "Parsing Emoji"
            wf.add_item(title, subtitle=subtitle)

    else:
        """Last case"""
        wf.add_item(
            "Complete",
            subtitle="Emoji searching is now ready to use",
            icon="images/Checkmark.png",
        )


def main(wf: Workflow3) -> None:
    """Define Main function."""
    try:
        count = int(os.environ["count"])
        first_time = False
    except:
        count = 0
        first_time = True

    if first_time:

        wf.rerun = 0.5
        wf.store_data("download_percent", 0)
        wf.store_data("phase", "downloading")
        wf.store_data("emoji_count", 0)
        wf.add_item("Starting background process")
        run_in_background(
            "bg", ["/usr/bin/python3", wf.workflowfile("src/bg_downloader.py")]
        )

    else:
        build_wf_entry(wf)

    wf.setvar("count", count)

    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
