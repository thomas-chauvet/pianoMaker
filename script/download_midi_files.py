import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from bs4 import BeautifulSoup
import requests
import os
import re


def flatten(x):
    return [item for sublist in x for item in sublist]


def get_artists_links(url="http://www.piano-midi.de/midi_files.htm"):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    artists_links_list = [
        x.find("a", href=True) for x in soup.findAll('tr', {'class': "midi"})
    ]
    return [
        "http://www.piano-midi.de/" + x["href"] for x in artists_links_list
        if x is not None
    ]


def get_songs_list_for_artist(artist_url):
    songs_links_list = [
        x.find("a", href=True)
        for x in BeautifulSoup(requests.get(artist_url).text, "html.parser")
        .findAll('td', {'class': "midi"})
    ]
    songs_links_list = [x for x in songs_links_list if x is not None]
    return [
        "http://www.piano-midi.de/" + x["href"] for x in songs_links_list
        if x["href"].endswith(".mid")
    ]


def make_artist_directory(url, base_dir="../data/raw/"):
    path = base_dir + re.search('http://www.piano-midi.de/midis/(.*)/',
                                url).group(1)
    if not os.path.exists(path):
        os.makedirs(path)


def download_midi_file(url, base_dir="../data/raw/"):
    logging.info("Download " + url + ".")
    file_name = base_dir + url.replace("http://www.piano-midi.de/midis/", "")
    make_artist_directory(url)
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        response = requests.get(url)
        # write to file
        file.write(response.content)


if __name__ == '__main__':
    url = "http://www.piano-midi.de/midi_files.htm"
    logging.info("Get artists list from " + url + ".")
    artists_links_list = get_artists_links()
    logging.info("Get songs list from all artists.")
    songs_links_list = flatten(
        [get_songs_list_for_artist(x) for x in artists_links_list])
    logging.info("Download song...")
    _ = [download_midi_file(x) for x in songs_links_list]