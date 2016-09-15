# -*- coding: utf-8 -*-
from workflow import Workflow3
from workflow.notify import  notify
from bs4 import BeautifulSoup
import sys

import  base64
import urllib2



def main(wf):

    def convert_to_unicode(str):
        """Takes a string in the form of U+XXX and turns it into a \UXXXXXXXX """
        ret = ""
        for uni in str.replace("U+", "").split(" "):
            ret += "\U00000000"[:-len(uni)] + uni

        # Apply Emoji Selector to the end
        ret += "\U0000FE0F"
        return ret

    # Print / write the output as needed
    def print_result(print_name):
        output = ','.join([str(number) + ".png", print_name, code.decode('unicode_escape'), code, raw_code_string, keywords])
        csv.write(output.encode('utf-8') + "\n")


    notify(title=u'Emoji Taco', text=u'Initializing emoji data', sound=None)

    #html = open('full-emoji-list.html', 'r').read()
    html = urllib2.urlopen('http://unicode.org/emoji/charts/full-emoji-list.html').read()

    notify(title=u'Emoji Taco', text=u'Converting emoji data', sound=None)

    soup = BeautifulSoup(html, "lxml")

    tables = soup.findAll('table')

    # Used to handle alias situations
    alias_dict = {}

    # Open the output file
    csv = open('emoji.csv', 'w')

    notify(title=u'Emoji Taco', text=u'Parsing emoji data', sound=None)


    for table in tables:

        rows = table.findAll('tr')

        for tr in rows:
            cols = tr.findAll(['th', 'td'])

            # Extract the raw unicode string - basically turn it into something python can print
            raw_code_string = str(cols[1].text)

            if raw_code_string == u'Code':
                # Skip header lines
                continue

            # Unicode code
            code = convert_to_unicode(raw_code_string)
            # The apple column - if we have no data here we prob dont care about the emoji because it isnt in osx
            apple = cols[4].text
            # The name of the emoji
            names = cols[15].text.replace(u'amp;', u'').split(u'≊ ')
            # The number
            number = int(cols[0].text)

            # Zero out alias and name
            alias = None
            name = None

            keywords = cols[18].text.replace("|", '')

            # Ignore non apple unicodes
            if apple != u'':
                continue


            # With default Beautiful soup parser use this line
            # img_data = base64.b64decode(cols[4].contents[0].attrs[2][1].split(',')[1])
            # With lxml parser use this
            img_data = base64.b64decode(cols[4].contents[0].attrs['src'].split(',')[1])
            with open("img/" + str(number) + '.png', 'wb') as f:
                f.write(img_data)


            if len(names) > 1:  # We have an alias definition
                name = names[0]
                alias = names[1]
                alias_dict[alias] = name
            elif names[0].islower():

                # Split on comma
                names = names[0].split(', ')
                name = alias_dict.get(names[0],names[0])
                if len(names) > 1:
                    name += " "
                    name += names[1]
            else:
                name = names[0]

            if alias:
                print_result(alias.upper())

            print_result(name)

    notify(title=u'Emoji Taco', text=u'Is ready for use', sound=None)


if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
