from configparser import ConfigParser
import json
import os
import sys


import requests
import spotipy
import spotipy.util as util

'''
export SPOTIPY_CLIENT_ID='874522d147984dff932e264c028dbdcf'
export SPOTIPY_CLIENT_SECRET='20ee5ff2f2f046e898a511e38f6dc2ff'
export SPOTIPY_REDIRECT_URI='https://sandos.net/callback'
'''
# spotify:artist:2uFUBdaVGtyMqckSeCl0Qj
scope = 'user-read-currently-playing'
spotipy_token = None


def read_config():
    """ read configfile """
    global slack_token
    global slack_channel
    global slack_color
    global slack_footer_icon
    global spotipy_client_id
    global spotipy_client_secret
    global spotipy_redirect_uri
    global spotipy_username
    with open(os.path.join(sys.path[0], 'spotislack.cfg')) as conf:
        config = ConfigParser()
        config.read_file(conf)
    slack_token = config['slack']['slack_token']
    slack_channel = config['slack']['slack_channel']
    slack_color = config['slack']['slack_color']
    slack_footer_icon = config['slack']['slack_footer_icon']
    spotipy_client_id = config['spotify']['spotipy_client_id']
    spotipy_client_secret = config['spotify']['spotipy_client_secret']
    spotipy_redirect_uri = config['spotify']['spotipy_redirect_uri']
    spotipy_username = config['spotify']['spotipy_username']


def get_current_song_from_spotify(spotipy_token):
    if spotipy_token:
        global artist
        global songname
        global songurl
        global artwork
        global fallback
        sp = spotipy.Spotify(auth=spotipy_token)
        results = sp.current_user_playing_track()
        artist = results['item']['album']['artists'][0]['name']
        songname = results['item']['name']
        songurl = results['item']['uri']
        artwork = results['item']['album']['images'][0]['url']
        fallback = "np: {0} - {1}".format(artist, songname)
    else:
        print("Can't get token for", spotipy_username)


def send_message_to_slack(token, channel, color, footer_icon, artist, songname, songurl, artwork, fallback):
    """ Makes use of Send API:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(slack_token),
    }
    payload = {
        "channel": channel,
        "as_user": 'true',
        "attachments": [
            {
                "fallback": fallback,
                "color": color,
                "author_name": artist,
                "title": songname,
                "title_link": songurl,
                "thumb_url": artwork,
                "footer": "now playing",
                "footer_icon": footer_icon,
            }
        ]
    }
    url = 'https://slack.com/api/chat.postMessage'
    response = requests.post(url, headers=headers,
                             data=json.dumps(payload))
    response.raise_for_status()
    return response.json()


def main():
    """ the main function """

    try:
        read_config()
        spotipy_token = util.prompt_for_user_token(spotipy_username, scope, spotipy_client_id, spotipy_client_secret, spotipy_redirect_uri)
        get_current_song_from_spotify(spotipy_token)
        send_message_to_slack(slack_token, slack_channel, slack_color, slack_footer_icon, artist, songname, songurl, artwork, fallback)


    except:
        print("Connection Failed")


if __name__ == "__main__":
    main()
