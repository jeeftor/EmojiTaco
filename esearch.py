# encoding=utf8
import sys

reload(sys)
sys.setdefaultencoding('utf8')

from workflow import Workflow3
import os
import  urllib
name_match = []
keyword_match = []

def main(wf):

    if os.path.isfile('emoji.tab'):
        pass
    else:
        wf.add_item('Emoji not initialized.  Hit enter or type "init emoji".', 'The init script requires you to be connected to the internet', arg='init emoji', valid=True)
        wf.send_feedback()
        exit()


    try:
        query = [str(arg) for arg in wf.args[0:]]
    except:
        query = ''


    with open('emoji.tab', 'r') as f:
        for idx, line in enumerate(f,1):
            split_list = line.strip().split('\t')
            if len(split_list) != 6:
                raise  ValueError("Line {}: '{}' has {} spaces, expected 1"
                .format(idx, line.rstrip(), len(split_list) - 1))
            else:
                img, name, code, raw_code, code_string, keywords = split_list

            in_keywords = True
            in_name = True

            for term in query:

                if term.startswith('-'):
                    in_name &= term[1:] not in name.lower()
                    in_keywords &= term[1:] not in keywords.lower()
                else:
                    in_name &= term in name.lower()
                    in_keywords &= term in keywords.lower()

            if in_name:
                name_match.append([img, name, raw_code, keywords])
            elif in_keywords:
                keyword_match.append([img, name, raw_code, keywords])

    imgbase = 'file://' + urllib.quote(os.getcwd()) + '/img/'

    if len(name_match + keyword_match) == 0:
        wf.add_item("\\U0001F622\\U0000FE0F".decode('unicode_escape') + ' No Emoji found', 'Please try again', icon='icon.png')
    else:
        if len(name_match + keyword_match) > 9:
            wf.add_item( str(len(name_match + keyword_match)) + ' matches found', 'To remove results use - in front of a term',
                         icon='icon.png', valid=False)
    for array in name_match + keyword_match:
        img, title, raw_code, subtitle = array

        ql = imgbase + img

        item = wf.add_item(title, subtitle=subtitle.replace('  ',' '),
                    icon="img/" + img,
                    quicklookurl=ql,
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
