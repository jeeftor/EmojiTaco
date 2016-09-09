from workflow import Workflow3
import sys
import os

name_match = []
keyword_match = []


def main(wf):

    if os.path.isfile('emoji.csv'):
        pass
    else:
        wf.add_item('Emoji not initialized.  Type "init emoji"', 'The init script requires you to be connected to the internet')
        wf.send_feedback()
        exit()


    query = str(wf.args[0])

    with open('emoji.csv') as f:
        for line in f:
            img, name, code, raw_code, keywords = line.strip().split(',')

            if query in name.lower():
                name_match.append([img,name,raw_code,keywords])
            elif query in keywords:
                keyword_match.append([img,name,raw_code,keywords])



    for array in name_match + keyword_match:
        img, title, raw_code, subtile = array
        wf.add_item(title, subtitle=subtile,
                    icon="img/" + img,
                    arg=raw_code.decode('unicode_escape'),
                    valid=True)

    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
