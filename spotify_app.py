"""
Step 1: Log into youtube.
Step 2: Grab our liked videos.
Step 3: Create a new spotify playlist
Step 4: Search for the song.
Step 5: Add this song to spotify playlist
"""

from config import SpotifyAppConfig
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import json
import os
import pickle as p
import requests


class CreatePlaylist:

    def __init__(self):
        self.youtube_client = self.get_youtube_client()
        self.songs_done = p.load(open('songs.pkl', 'rb'))

    def get_youtube_client(self):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        api_service_name = 'youtube'
        api_version = 'v3'
        client_secret_file = 'client_secret_2.json'

        # Get credentials and API client
        scopes = ['https://www.googleapis.com/auth/youtube.readonly']
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secret_file, scopes)
        credentials = flow.run_console()
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client

    def get_saved_videos(self):
        request = self.youtube_client.playlistItems().list(playlistId='PL3OTLdWDBsfFsGvaWGVqDbK5ekwx3qlc4',
                                                           part='snippet , contentDetails')
        response = request.execute()

        for item in response['items']:
            artist = item['snipprt']['title'].split('-')[0]
            song_name = item['snipprt']['title'].split('-')[1]
            song_uri = self.get_song_uri(song_name, artist)

            if song_uri not in self.songs_done:
                self.add_song_to_spotify(song_uri)
                self.songs_done[song_uri] = 1
            else:
                print(f'{song_name} {artist} song already added as : {song_uri}')

    def create_playlist(self):
        request_body = json.dumps({'name': 'youtube liked videos',
                                   'description': 'All youtube liked videos',
                                   'public': True})
        url = f'https://api.spotify.com/v1/users/{SpotifyAppConfig.Spotify.user_id}/playlists'
        response = requests.post(url,
                                 data=request_body,
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': f'Bearer {SpotifyAppConfig.Spotify.oauth_token}'},
                                 )
        response_json = response.json()
        return response_json['id']

    def get_song_uri(self, song_name, artist):
        url = f'https://api.spotify.com/v1/search?query={song_name} {artist}&type=track&limit=1'
        resp = requests.get(url,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': f'Bearer {SpotifyAppConfig.Spotify.oauth_token}'}
                            )
        resp = resp.json()
        print(resp)
        return resp['tracks']['items'][0]['uri']

    def add_song_to_spotify(self, uri):
        playlist_id = SpotifyAppConfig.Spotify.playlist_id
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        song_uri = uri
        request_body = json.dumps([song_uri])
        response = requests.post(url,
                      data=request_body,
                      headers={'Content-Type': 'application/json',
                               'Authorization': f'Bearer {SpotifyAppConfig.Spotify.oauth_token}'}
                      )
        response = response.json()
        print(response)
