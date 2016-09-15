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

    try:
        query = str(wf.args[0])
    except:
        query = ''


    with open('emoji.csv') as f:
        for line in f:
            img, name, code, raw_code, code_string, keywords = line.strip().split(',')

            if query in name.lower():
                name_match.append([img,name,raw_code,keywords])
            elif query in keywords:
                keyword_match.append([img,name,raw_code,keywords])

    imgbase = 'file://' + wf.datadir + '/img/'

    for array in name_match + keyword_match:
        img, title, raw_code, subtitle = array
        item = wf.add_item(title, subtitle=subtitle.replace('  ',' '),
                    icon="img/" + img,
                    quicklookurl=imgbase + img,
                    arg=raw_code.decode('unicode_escape'),
                    valid=True)

        p_string = raw_code.replace('\\','\\\\')
        pd_string = '\"' + p_string +  '\".decode(\'unicode_escape\')'
        item.add_modifier("cmd", subtitle='Python String [' + p_string + ']', arg=p_string, valid=None)
        item.add_modifier("alt", subtitle='Unicode Value [' + code_string + ']', arg=code_string, valid=None)
        item.add_modifier("ctrl", subtitle='Python String (decoded) [' + pd_string + ']', arg=pd_string, valid=None)


    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow3(update_settings=
                   {
                       'github_slug':'jeeftor/EmojiTaco',
                       'frequency': 7
                   }
    )
    sys.exit(wf.run(main))
