"""File Download wrapper."""
from __future__ import annotations

import os
import sys

from workflow import Workflow3
from workflow.background import is_running, run_in_background


def string_from_percent(pct: float) -> str | None:
    """Return a fancy string to show in the workflow from the count item."""
    # blue = "\\U0001F535\\U0000FE0F"
    white = "\U000026AA\U0000FE0F"
    black = "\U000026AB\U0000FE0F"

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

    return ret[mod:][0:20]


def build_wf_entry(wf: Workflow3) -> None:
    """Build workflow entry."""
    if is_running("emoji_init"):
        """Update status."""
        phase : str = wf.stored_data("phase")
        log.info("--dbg:\tIs Running with phase [%s]", phase)
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

            title = f"Downloading {file} [{progress}]"
            subtitle = string_from_percent(pct) + " " + str(pct) + "%"
            wf.add_item(title, subtitle=subtitle)

        if phase == "processing":

            try:
                emoji_count = wf.stored_data("emoji_count")
                subtitle = f"Parsed {emoji_count} emoji"
            except Exception as e:
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

    log.debug("--dbg:\tmain Function")

    try:
        count = int(os.environ["count"])
        first_time = False
    except KeyError:
        count = 0
        first_time = True

    if is_running("emoji_init"):
        first_time = False

    if first_time:
        wf.rerun = 0.5
        wf.store_data("download_percent", 0)
        wf.store_data("phase", "downloading")
        wf.store_data("emoji_count", 0)
        wf.add_item("Starting background process")
        run_in_background(
            "emoji_init", ["/usr/bin/python3", wf.workflowfile("src/bg_downloader.py")]
        )
        log.debug("Launching background task")
    else:
        build_wf_entry(wf)

    wf.setvar("count", count)

    wf.send_feedback()


if __name__ == "__main__":
    wf = Workflow3()
    log = wf.logger
    log.info("Emoji Init Started")
    sys.exit(wf.run(main))
