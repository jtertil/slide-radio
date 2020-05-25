import requests, time

import mpv

MB_URL = 'http://musicbrainz.org/ws/2'
LAST_URL = 'http://ws.audioscrobbler.com/2.0'
FANART_URL = 'http://webservice.fanart.tv/v3'
LAST_API_KEY = ''
FANART_API_KEY = ''

RADIO_URL = 'http://stream.antenarock.sk/antena-hi.mp3'
# RADIO_URL = 'http://us4.internet-radio.com:8258/'
# RADIO_URL = 'http://us5.internet-radio.com:8267/'

player = mpv.MPV()


def mb_query(artist):
    r = requests.get(f'{MB_URL}/artist/?query=artist:{artist}&fmt=json')
    if r.status_code == 200:
        j = r.json()
        mb_artists = j.get('artists')
    if mb_artists:
        try:
            mb_artist = mb_artists[0]
        except IndexError:
            mb_artist = {}
            print(f'Err mb_artist: {artist}')
    else:
        mb_artist = {}
        print(f'Err mb_artist: {artist}')
    mb_id = mb_artist.get('id')
    return mb_id


def lastfm_query(mb_id):
    r = requests.get(f'{LAST_URL}/?method=artist.getinfo&mbid={mb_id}&api_key={LAST_API_KEY}&format=json')
    if r.status_code == 200:
        j = r.json()
        artist = j.get('artist')
    else:
        artist = {}
        print(f'Err lastfm artist: {mb_id}')
    if artist:
        bio = artist.get('bio')
    else:
        bio = {}
        print(f'Err bio: {mb_id}')
    summary = bio.get('summary')
    content = bio.get('content')
    return {'summary': summary, 'content': content}


def fanart_query(mb_id):
    r = requests.get(f'{FANART_URL}/music/{mb_id}?api_key={FANART_API_KEY}')
    if r.status_code == 200:
        j = r.json()
        fanart = j.get('artistbackground')
    else:
        fanart = {}
        print(f'Err fanart: {mb_id}')
    return fanart


def get_info(metadata):
    icy_name = metadata.get('icy-name')
    icy_title = metadata.get('icy-title')
    station = icy_name
    if icy_title:
        try:
            artist, title = icy_title.split(' - ')
        except Exception as e:
            print(f'Err title split: ({icy_title}).')
            artist = None
            title = None
        return {'station': station,'artist': artist,'title': title}
    else:
        return {'station': station}


def player_connect():
    print('checking internet connection.')
    while True:
        r = requests.get('http://stream.antenarock.sk/')
        if r.status_code != 200:
            print('.', end='')
            sleep(5)
        else:
            break
    player.play(RADIO_URL)


def run():
    info = {}
    while True:
        if not player.metadata:
            player_connect()
            time.sleep(3)

        actual_info = get_info(player.metadata)
        if info != actual_info:
            info = actual_info

            if info.get('artist') and info.get('title'):
                if info.get('artist') == info.get('station'):
                    display = f"You are listening to {info['station']}."
                    print('\n')
                    print('*' * len(display))
                    print(display)
                    print('*' * len(display))
                else:
                    display = f"{info['station']} playing now: {info['artist']} - {info['title']}."
                    mb_id = mb_query(info['artist'])
                    print('\n')
                    print('=' * len(display))
                    print(display)
                    print('=' * len(display))
                    if mb_id:
                        display = f"musicbrainz id: {mb_id}"
                        print('\n')
                        print(display)
                        print('-' * len(display))
                        lastfm =  lastfm_query(mb_id)
                        fanart = fanart_query(mb_id)
                    if lastfm['summary']:
                        display = f'This is last.fm summary:'
                        print('\n')
                        print(display)
                        print('-' * len(display))
                        print(lastfm['summary'])
                    if fanart:
                        display = f'Fanart count: {len(fanart)}:'
                        print('\n')
                        print(display)
                        print('-' * len(display))
                        for i in fanart[:5]:
                            print(f"{i['url']}")
            else:
                display = f"You are listening to unknown station."
                print('\n')
                print('*' * len(display))
                print(display)
                print('*' * len(display))
        time.sleep(1)
