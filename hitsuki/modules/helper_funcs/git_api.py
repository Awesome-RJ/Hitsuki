#    Hitsuki (A telegram bot project)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import urllib.request as url

import rapidjson as json

VERSION = "1.0.2"
APIURL = "http://api.github.com/repos/"


def vercheck() -> str:
    return str(VERSION)


def getData(repoURL):
    try:
        with url.urlopen(APIURL + repoURL + "/releases") as data_raw:
            return json.loads(data_raw.read().decode())
    except Exception:
        return None


def getReleaseData(repoData, index):
    return repoData[index] if index < len(repoData) else None


def getAuthor(releaseData):
    return None if releaseData is None else releaseData['author']['login']


def getAuthorUrl(releaseData):
    return None if releaseData is None else releaseData['author']['html_url']


def getReleaseName(releaseData):
    return None if releaseData is None else releaseData['name']


def getReleaseDate(releaseData):
    return None if releaseData is None else releaseData['published_at']


def getAssetsSize(releaseData):
    return None if releaseData is None else len(releaseData['assets'])


def getAssets(releaseData):
    return None if releaseData is None else releaseData['assets']


def getBody(releaseData):
    return None if releaseData is None else releaseData['body']


def getReleaseFileName(asset):
    return asset['name']


def getReleaseFileURL(asset):
    return asset['browser_download_url']


def getDownloadCount(asset):
    return asset['download_count']


def getSize(asset):
    return asset['size']
