
__title__ = "YoutubePlaylist"
__doc__ = "Checkout pre-recorded turtorials and demos about EnneadTab."

import webbrowser

def youtube_playlist():
    playlist = "https://youtube.com/playlist?list=PLz3VQzyVrU1iyoGV-kzWhCPsmh9cQWWoV"
    webbrowser.open_new(playlist)


if __name__ == "__main__":
    youtube_playlist()