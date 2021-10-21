from json.decoder import JSONDecodeError
import time
import json
import requests
import secrets
import os
import utils
import urllib.parse
from requests_oauthlib import OAuth2Session


# base_url = "https://myanimelist.net/v1/oauth2/"
# auth_url = base_url + "authorize"
# token_url = base_url + "token"


class MALAPI:
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    refresh_url = 'https://myanimelist.net/v1/oauth2/token'
    oauthClient = None
    token = None
    code_challenge = None
    code_verifier = None
    authorization_url = None
    authorization_code = None

    # 1. Generate a new Code Verifier / Code Challenge.

    def get_new_code_verifier(self) -> str:
        code_verifier = secrets.token_urlsafe(100)
        return code_verifier[:128]

    # 2. Print the URL needed to authorize your application.

    def print_new_authorization_url(self):

        url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={self.CLIENT_ID}&code_challenge={self.code_challenge}'
        print(f'Authorize your application by clicking here: {url}\n')

    def get_new_authorization_url(self) -> str:

        url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={self.CLIENT_ID}&code_challenge={self.code_challenge}'
        return url

    # 3. Once you've authorized your application, you will be redirected to the webpage you've
    #    specified in the API panel. The URL will contain a parameter named "code" (the Authorization
    #    Code). You need to feed that code to the application.

    def generate_new_token(self, authorization_code: str) -> dict:

        url = 'https://myanimelist.net/v1/oauth2/token'
        data = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'code': authorization_code,
            'code_verifier': self.code_verifier,
            'grant_type': 'authorization_code'
        }
        expires_at = time.time()
        response = requests.post(url, data)
        response.raise_for_status()  # Check whether the requests contains errors

        self.token = response.json()
        response.close()
        print('Token generated successfully!')
        self.token['expires_at'] = expires_at + self.token['expires_in']
        extra = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'grant_type': 'refresh_token',
        }
        self.oauthClient = OAuth2Session(
            self.CLIENT_ID, token=self.token, auto_refresh_url=self.refresh_url, auto_refresh_kwargs=extra, token_updater=self.saver_token)
        self.save_token()

        return self.token

    # 4. Test the API by requesting your profile information

    def print_user_info(self):
        url = 'https://api.myanimelist.net/v2/users/@me'
        response = requests.get(url, headers={
            'Authorization': f'Bearer {self.token["access_token"]}'
        })

        response.raise_for_status()
        user = response.json()
        response.close()

        print(f"\n>>>     Greetings {user['name']}!     <<<\n")

    def refresh_token(self):
        url = 'https://myanimelist.net/v1/oauth2/token'
        data = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': self.token['refresh_token']
        }
        response = requests.post(url, data)
        response.raise_for_status()

        self.token = response.json()
        response.close()
        print('Token generated successfully!')

        self.save_token()

        return self.token

    def get_user_animelist(self):
        url = 'https://api.myanimelist.net/v2/users/@me/animelist'
        response = self.oauthClient.get(
            url,
            # headers={'Authorization': f'Bearer {self.token["access_token"]}'},
            params={'sort': 'anime_title',
                    'limit': '1000',
                    'fields': 'id,title,synopsis,mean,main_picture,my_list_status'}
        )
        response.raise_for_status()
        res = response.json()
        response.close()

        return res['data']

    def get_top_anime(self):
        url = 'https://api.myanimelist.net/v2/anime/ranking'
        response = self.oauthClient.get(
            url,
            # headers={'Authorization': f'Bearer {self.token["access_token"]}'},
            params={'ranking_type': 'all',
                    'limit': '20',
                    'fields': 'id,title,synopsis,mean,main_picture,my_list_status'}
        )
        # 'fields': 'id,title,synopsis,mean,main_picture,my_list_status'
        response.raise_for_status()
        res = response.json()
        response.close()
        return res['data']

    def find_anime(self, search_str: str):
        url = 'https://api.myanimelist.net/v2/anime'
        response = self.oauthClient.get(
            url,
            # headers={'Authorization': f'Bearer {self.token["access_token"]}'},
            params={'q': urllib.parse.quote(search_str),
                    'limit': '10',
                    'fields': 'id,title,synopsis,mean,main_picture,my_list_status'}
        )
        # 'fields': 'id,title,synopsis,mean,main_picture,my_list_status'
        response.raise_for_status()
        res = response.json()
        response.close()

        return res['data']

    def add_anime_to_list(self, anime_id, score=None):
        url = f'https://api.myanimelist.net/v2/anime/{anime_id}/my_list_status'
        data = {
            'status': 'completed',
        }
        if score != None:
            data['score'] = str(score)
        response = self.oauthClient.patch(
            url,
            data,
            # headers={'Authorization': f'Bearer {self.token["access_token"]}'}
        )
        response.raise_for_status()
        response.close()

    def delete_anime_from_list(self, anime_id):
        url = f'https://api.myanimelist.net/v2/anime/{anime_id}/my_list_status'
        response = self.oauthClient.delete(
            url,
            # headers={'Authorization': f'Bearer {self.token["access_token"]}'}
        )
        response.raise_for_status()
        response.close()

    def saver_token(self, token):
        self.token = token
        self.save_token()

    def save_token(self, path='token'):
        # utils.save_json('token.json', self.token)
        utils.save_encrypted('token', self.token)

    def load_token(self, path='token'):
        self.token = None
        if os.path.exists(path):
            try:
                self.token = utils.decrypt_from_file(path)
            except Exception:
                return False
            extra = {
                'client_id': self.CLIENT_ID,
                'client_secret': self.CLIENT_SECRET,
                # 'grant_type': 'refresh_token',
            }
            self.oauthClient = OAuth2Session(
                client_id=self.CLIENT_ID,
                token=self.token,
                auto_refresh_url=self.refresh_url,
                auto_refresh_kwargs=extra,
                token_updater=self.saver_token)
            return True
        return False

    def get_id_and_secret(self):
        self.CLIENT_ID = os.environ.get('TRRP_MALAPI_CLIENT_ID')
        self.CLIENT_SECRET = os.environ.get('TRRP_MALAPI_CLIENT_SECRET')
        if self.CLIENT_ID == None or self.CLIENT_SECRET == None:
            raise RuntimeError(
                'CLIENT ID or SECRET is not found in system environment')

    def __init__(self):
        self.get_id_and_secret()
        self.code_verifier = self.code_challenge = self.get_new_code_verifier()
        self.authorization_url = self.get_new_authorization_url()

    def make_token(self, authorization_code):
        self.authorization_code = authorization_code
        self.token = self.generate_new_token(
            self.authorization_code)


if __name__ == '__main__':
    malapi = MALAPI()
    malapi.load_token()
    # print(malapi.authorization_url)
    # authorization_code = input('Copy-paste the Authorization Code: ').strip()
    # malapi.make_token(authorization_code)
    print(malapi.get_user_animelist())
