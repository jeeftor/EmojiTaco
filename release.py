"""Make a github release."""
import json
import os
import sys
import urllib
import urllib.request

GITHUB_USER = "jeeftor"
GITHUB_REPO = "EmojiTaco"

""" Requires you have a github access token as specified below in your home director """


# Read github access token outof ~/.github_access_token
from os.path import expanduser

home = expanduser("~")
token_file = home + "/.github_access_token"
GITHUB_ACCESS_TOKEN = open(token_file).read()


def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


print(sys.argv)

version = sys.argv[1]
file_to_upload = sys.argv[2]

github_token = str(GITHUB_ACCESS_TOKEN).rstrip()


# curl -i -H 'Authorization: token 5b8e3a4d92993282d2a8f20b5fe4910edc9f82dd' https://api.github.com/user/repos

request_headers = {
    "Content-Type": "application/json",
    "Authorization": "token %s" % github_token,
}


print(request_headers)

# Release INFO
payload = {
    "tag_name": f"v{version}",
    "target_commitish": "master",
    "name": f"Release {version}",
    "body": "Auto Generated Release notes by the `release.py` script",
    "draft": True,
    "prerelease": False,
}


# Make a new release
data = json.dumps(payload)
clen = len(data)
request_headers["Content-Length"] = clen
url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases"
# url = 'https://api.github.com/repos/jeeftor/EmojiTaco/releases'
print(url)
req =  urllib.request.Request(url, data=data, headers=request_headers)
f = urllib.request.urlopen(req)
response = f.read()
f.close()
pp_json(response)
json = json.loads(response)

# Parse out the upload URL
url = json["upload_url"].split("{")[0]

# Do more parsing
upload_path = "build/" + file_to_upload
upload_data_len = length = os.path.getsize(upload_path)
upload_data = open(upload_path, "rb")
url = url + f"?name={file_to_upload}"

# Upload the new workflow file
request = urllib.request.Request(url, data=upload_data, headers=request_headers)
request.add_header("Cache-Control", "no-cache")
request.add_header("Content-Length", "%d" % upload_data_len)
res = urllib.request.urlopen(request).read().strip()


# Launch web browser to the Draf release
from subprocess import call

call(["open", json["html_url"]])
exit()
