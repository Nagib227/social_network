import os
import m3u8
import requests
import vk_api
from vk_api import VkApi
from vk_api.audio import VkAudio
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from .VARIABLES import bad_name_elements, LOGIN, PASSWORD



class M3U8Downloader:

    def __init__(self, login: str, password: str):
        self._vk_session = VkApi(
            login=login,
            password=password,
            api_version='5.81'
        )
        try:
            self._vk_session.auth()
        except vk_api.exceptions.Captcha as captcha:
            print(captcha.sid) # Получение sid
            print(captcha.get_url()) # Получить ссылку на изображение капчи
            raise vk_erorr

        self._vk_audio = VkAudio(self._vk_session)

    def download_audio(self, q: str):
        name, info = self._get_audio_info(q=q)
        
        if os.path.exists(f"static/music/wav/{name}.wav"):
            print(1)
            return info

        url = self._get_audio_url(q=q)
        segments = self._get_audio_segments(url=url)
        segments_data = self._parse_segments(segments=segments)
        segments = download_m3u8(segments_data=segments_data, index_url=url)
        self._convert_ts_to_mp3(segments=segments, name=name)
        return info

    def _convert_ts_to_mp3(self, segments: bytes, name: str):
        with open(f'static/music/segments/{name}.ts', 'wb') as f:
            f.write(segments)
        os.system(f'bin\\ffmpeg.exe -y -i "static/music/segments/{name}.ts" -vcodec copy -acodec copy -vbsf h264_mp4toannexb "static/music/wav/{name}.wav"')
        os.remove(f"static/music/segments/{name}.ts")

    def _get_audio_info(self, q: str):
        self._vk_audio.get_albums_iter()
        audio = next(self._vk_audio.search_iter(q=q))
        print(audio)
        title = audio['title']
        artist = audio['artist']
        url_img = audio['track_covers'][1]
        name = f"{title}_{artist}"
        for i in bad_name_elements:
            name = name.replace(i, "_")
        return [name, [title, artist, url_img, name]]

    def _get_audio_url(self, q: str):
        self._vk_audio.get_albums_iter()
        audio = next(self._vk_audio.search_iter(q=q))
        url = audio['url']
        return url

    @staticmethod
    def _get_audio_segments(url: str):
        m3u8_data = m3u8.load(
            uri=url
        )
        return m3u8_data.data.get("segments")

    @staticmethod
    def _parse_segments(segments: list):
        segments_data = {}

        for segment in segments:
            segment_uri = segment.get("uri")

            extended_segment = {
                "segment_method": None,
                "method_uri": None
            }
            if segment.get("key").get("method") == "AES-128":
                extended_segment["segment_method"] = True
                extended_segment["method_uri"] = segment.get("key").get("uri")
            segments_data[segment_uri] = extended_segment
        return segments_data

def download_key(key_uri: str) -> bin:
    return requests.get(url=key_uri).content


def download_m3u8(segments_data: dict, index_url: str) -> bin:
    downloaded_segments = []

    for uri in segments_data.keys():
        audio = requests.get(url=index_url.replace("index.m3u8", uri))

        downloaded_segments.append(audio.content)

        if segments_data.get(uri).get("segment_method") is not None:
            key_uri = segments_data.get(uri).get("method_uri")
            key = download_key(key_uri=key_uri)

            iv = downloaded_segments[-1][0:16]
            ciphered_data = downloaded_segments[-1][16:]

            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            data = unpad(cipher.decrypt(ciphered_data), AES.block_size)
            downloaded_segments[-1] = data

    return b''.join(downloaded_segments)
       

def find_music(q: str="Тутанхамон"):
    # md = M3U8Downloader(login=login, password=password)
    print("999999999999999999999999999")
    info = md.download_audio(q=q)
    return info

md = M3U8Downloader(login=LOGIN, password=PASSWORD)
if __name__ == "__main__":
    find_music(login="", password="")
