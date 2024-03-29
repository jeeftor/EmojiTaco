"""Data file builder."""
import base64
import os
import shutil
import sys
from urllib.request import urlopen

from bs4 import BeautifulSoup
from urllib3.exceptions import HTTPError
from workflow import Workflow3
from workflow.notify import notify


class DataFilerBuilder:
    """Data File Builder class."""

    def __init__(self) -> None:
        """Initialize the download percent."""
        self.last_download_percent = 0

    @staticmethod
    def my_super_copy(what, where):
        """Super copy method."""
        try:
            shutil.copy(what, where)
        except OSError:
            os.chmod(where, 777)  # ?? still can raise exception
            shutil.copy(what, where)

    @staticmethod
    def build_headers(cols) -> dict:
        """Extacts a mapping of column number to name -- hopefully to help future proof this script."""
        headers = {}

        for i in range(0, len(cols)):
            headers[cols[i].text] = i
            # print("Header : " + cols[i].text)
        return headers

    def download_chunk_report(self, bytes_so_far, chunk_size, total_size):
        """Report download progress."""
        percent = float(bytes_so_far) / total_size
        percent = int(round(percent * 100, 2))

        if int(self.last_download_percent) < int(percent):
            print(f"Downloaded {bytes_so_far} of {total_size} bytes {percent:0.2f}%")
            log.debug(
                f"Downloaded {bytes_so_far} of {total_size} bytes {percent:0.2f}%"
            )
            self.last_download_percent = int(percent)
            sys.stdout.write(
                "Downloaded %d of %d bytes (%0.2f%%)\r"
                % (bytes_so_far, total_size, percent)
            )
            log.debug(
                "Downloaded %d of %d bytes (%0.2f%%)\r"
                % (bytes_so_far, total_size, percent)
            )

            # if bytes_so_far >= total_size:
            # sys.stdout.write('\n')

    def download_chunk_read(
        self, response, chunk_size=8192, output_file=None, report_hook=None
    ):
        """Read streaming download chunk by chunk."""
        total_size = response.info().getheader("Content-Length").strip()
        total_size = int(total_size)
        bytes_so_far = 0

        while 1:
            chunk = response.read(chunk_size)
            bytes_so_far += len(chunk)

            if not chunk:
                print("breaking")
                break

            output_file.write(chunk)

            if report_hook:
                report_hook(bytes_so_far, chunk_size, total_size)

        return bytes_so_far

    def buildData(self, wf, test_mode=False):
        """Build out some data files."""

        def convert_to_unicode(str):
            r"""Take a string in the form of U+XXX and turns it into a \UXXXXXXXX."""
            ret = ""
            for uni in str.replace("U+", "").split(" "):
                ret += "\U00000000"[: -len(uni)] + uni

            # Apply Emoji Selector to the end
            ret += "\U0000FE0F"
            return ret

        def parse_html_files() -> None:

            # Open the output file
            csv = open("../emoji.tab", "w")

            parse_html_file(csv, "../unicode.html", "Converting emoji data")
            parse_html_file(csv, "../skin-tones.html", "Converting skin-tone data")

        def parse_html_file(csv, file_name, message):

            # Print / write the output as needed
            def print_result(print_name):
                output = "\t".join(
                    [
                        str(number) + ".png",
                        print_name,
                        code.decode("unicode_escape"),
                        code,
                        raw_code_string,
                        keywords,
                    ]
                )
                csv.write(output.encode("utf-8") + "\n")

            html = open(file_name, "rb").read()

            if not test_mode:
                notify(title="Emoji Taco", text=message, sound=None)
                # soup = BeautifulSoup(html, "lxml")
                # Trying out native parsing - adios lxml??
                soup = BeautifulSoup(html, features="html.parser")
            else:
                soup = BeautifulSoup(html)

            tables = soup.findAll("table")

            # Used to handle alias situations
            alias_dict = {}

            if not test_mode:
                notify(title="Emoji Taco", text="Parsing emoji data", sound=None)

            headers = None

            emoji_count = 0

            for table in tables:

                rows = table.findAll("tr")

                for tr in rows:
                    cols = tr.findAll(["th", "td"])

                    if not headers:
                        headers = self.build_headers(cols)

                    if len(headers) < 3:
                        # " Bad header detected ... lets abort for now"
                        headers = None
                        continue

                    # March 15 - Ignore the sub-header lines like "Face neutral" and stuff
                    # March 15 - Ignore the strange lines that have some emoji - probably are the ones that aren't decided on yet (like star-struck)
                    if len(cols) < 7:
                        continue

                    # Extract the raw unicode string - basically turn it into something python can print
                    # raw_code_string = str(cols[1].text)
                    raw_code_string = str(cols[headers["Code"]].text)

                    if raw_code_string == "Code":
                        # Skip header lines
                        continue

                    # Unicode code
                    code = convert_to_unicode(raw_code_string)
                    # The apple column - if we have no data here we prob don't care about the emoji because it isn't in osx
                    apple = cols[headers["Appl"]].text

                    # March 15th - File format changed so sometimes we get funky text like this in a case where there is no apple emoji - skip these items
                    if apple == "…     …":
                        continue

                    try:
                        names = (
                            cols[headers["CLDR Short Name"]]
                            .text.replace("amp;", "")
                            .split("≊ ")
                        )
                    except:
                        # March 29th - added a table to the bottom of the page listing out totals of emoji type - it breaks here so we must skip over it
                        continue

                    # The number
                    number = int(cols[headers["№"]].text)

                    # Zero out alias and name
                    alias = None
                    name = None

                    keywords = (
                        cols[headers["CLDR Short Name"]]
                        .text.replace("|", "")
                        .replace("  ", " ")
                        .replace("  ", " ")
                    )

                    image_filename = "img/" + str(number) + ".png"

                    # Ignore non apple unicodes
                    if apple != "":
                        self.my_super_copy("na.png", image_filename)
                        # continue
                    else:
                        # With default Beautiful soup parser use this line
                        # img_data = base64.b64decode(cols[4].contents[0].attrs[2][1].split(',')[1])
                        # With lxml parser use this
                        img_data = base64.b64decode(
                            cols[headers["Appl"]].contents[0].attrs["src"].split(",")[1]
                        )
                        with open(image_filename, "wb") as f:
                            f.write(img_data)

                    emoji_count += 1

                    if not test_mode and (emoji_count % 500) == 0:
                        notify(
                            title="Emoji Taco",
                            text=f"Parsed {emoji_count} emoji",
                            sound=None,
                        )

                    if len(names) > 1:  # We have an alias definition
                        name = names[0]
                        alias = names[1]
                        alias_dict[alias] = name
                    elif names[0].islower():

                        # Split on comma
                        names = names[0].split(", ")
                        name = alias_dict.get(names[0], names[0])
                        if len(names) > 1:
                            name += " "
                            name += names[1]
                    else:
                        name = names[0]

                    if alias:
                        print_result(alias.upper())

                    print_result(name)

            if not test_mode:
                notify(
                    title="Emoji Taco",
                    text=f"Is ready for use. {emoji_count} emoji processed",
                    sound=None,
                )

        # def chunk_report(bytes_so_far, chunk_size, total_size):
        #     percent = float(bytes_so_far) / total_size
        #     percent = int(round(percent * 100, 2))
        #
        #     if int(self.last_pct) < int(percent):
        #         #print("Downloaded {} of {} bytes {:0.2f}%".format(bytes_so_far, total_size, percent))
        #         self.last_pct = int(percent)
        #         sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" % (bytes_so_far, total_size, percent))
        #
        #     #if bytes_so_far >= total_size:
        #         #sys.stdout.write('\n')
        #
        # def chunk_read(response, chunk_size=8192, report_hook=None):
        #     total_size = response.info().getheader('Content-Length').strip()
        #     total_size = int(total_size)
        #     bytes_so_far = 0
        #
        #     while 1:
        #         chunk = response.read(chunk_size)
        #         bytes_so_far += len(chunk)
        #
        #         if not chunk:
        #             break
        #
        #         if report_hook:
        #             report_hook(bytes_so_far, chunk_size, total_size)
        #
        #     return bytes_so_far

        ###################################
        # END INTERNAL FUNCTION definition
        ###################################

        url_set1 = [
            "http://unicode.org/emoji/charts-beta/full-emoji-list.html",
            "http://unicode.org/emoji/charts-beta/full-emoji-modifiers.html",
        ]
        url_set2 = [
            "http://unicode.org/emoji/charts/full-emoji-list.html",
            "http://unicode.org/emoji/charts/full-emoji-modifiers.html",
        ]

        if not test_mode:
            notify(title="Emoji Taco", text="Initializing base emoji data", sound=None)

        with open("../unicode.html", "wb") as unicode_file:

            try:
                try:
                    if test_mode:
                        print("Querying: ", url_set1[0])
                    html = urlopen(url_set1[0], timeout=5000)
                    self.download_chunk_read(
                        html,
                        report_hook=self.download_chunk_report,
                        output_file=unicode_file,
                    )

                except Exception as e:
                    if test_mode:
                        print("Fall back query: ", url_set2[0])
                    html = urlopen(url_set2[0], timeout=5000)
                    self.download_chunk_read(
                        html,
                        report_hook=self.download_chunk_report,
                        output_file=unicode_file,
                    )
                    print(e)
            except HTTPError as e:
                if not test_mode:
                    notify(title="ERROR: base-unicode ", text=str(e))
                exit()
            except Exception as e:
                if not test_mode:
                    notify(title="Error: base-unicode", text=str(e))
                else:
                    print(str(e))
                exit()

        if not test_mode:
            notify(
                title="Emoji Taco", text="Initializing skin-tone emoji data", sound=None
            )

        with open("../skin-tones.html", "wb") as unicode_file:

            try:
                try:
                    if test_mode:
                        print("Querying: ", url_set1[1])
                    else:
                        log.debug("Querying: ", url_set1[1])
                    html = urlopen(url_set1[1], timeout=5000)
                    self.download_chunk_read(
                        html,
                        report_hook=self.download_chunk_report,
                        output_file=unicode_file,
                    )

                except Exception as e:
                    if test_mode:
                        print("Fall back query: ", url_set2[1])
                    else:
                        log.debug("Fall back query: ", url_set2[1])
                    html = urlopen(url_set2[1], timeout=5000)
                    self.download_chunk_read(
                        html,
                        report_hook=self.download_chunk_report,
                        output_file=unicode_file,
                    )
                    print(e)
                    log.debug(e)
            except HTTPError as e:
                if not test_mode:
                    notify(title="ERROR: skin-tone", text=str(e))
                exit()
            except Exception as e:
                if not test_mode:
                    notify(title="Error: skin-tone", text=str(e))
                else:
                    print(str(e))
                    log.debug(e)
                exit()

        # OPEN UP THE FILE NOW FOR READING
        parse_html_files()


def main(wf: Workflow3):
    """Define main function."""
    dfb = DataFilerBuilder()
    dfb.buildData(wf, test_mode=False)


if __name__ == "__main__":
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
