# content of test_sysexit.py
import pytest
from workflow import Workflow3

from src.buildDataFiles import DataFilerBuilder

# def f():
#     raise SystemExit(1)

# def test_mytest():
#     with pytest.raises(SystemExit):
#         f()

# def test_data_builder():
#    DataFilerBuilder().buildData(Workflow3(), test_mode=True)



def test_stream(travis = None):
    def do_dl():
        r = web.get(url1, stream=True)

        total_size = int(r.headers.get('content-length', 0))
        dl = 0

        with open('emoji.htm', 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                dl += len(chunk)
                if chunk:
                    print (float(total_size) / (dl * 4096))
                    f.write(chunk)
        print ('done')

    url1 = 'http://unicode.org/emoji/charts-beta/full-emoji-list.html'
    if travis:
        with travis.folding_output():
            do_dl()
    else:
        do_dl()



def test_download(travis = None):
    url1 = 'http://unicode.org/emoji/charts-beta/full-emoji-list.html'
    url2 = 'http://unicode.org/emoji/charts/full-emoji-list.html'

    if travis:
        with travis.folding_output():
            r = web.get(url1, timeout=6000)
    else:
        r = web.get(url1, timeout=6000)

        print (r.status_code)
