# horriblesubsXDCC

## Installation

```python -m pip install -r requirements.txt```

## Usage

1. set animes you watch in ```settings/animes.json``` or ```python sub_gui.py```
2. edit irc config ```settings/irc.sjon``` (user, res, etc.)
3. start downloading ```python horriblesubs.py```

### example irc.json
```
{
    "irc": {
        "anime_folder": "D:\\anime",
        "channel": "#horriblesubs",
        "default_bot": "CR-RALEIGH|NEW",
        "default_res": "720p",
        "host": "irc.rizon.net",
        "multiprocessing": 0,
        "port": 6667,
        "user": "bot123",
        "bot_ranking": ["CR-RALEIGH|NEW", "Ginpachi-Sensei", "CR-HOLLAND|NEW", "CR-BATCH|720p", "CR-ARCHIVE|720p", "ARUTHA-BATCH|720p"]
    }
}
```

### example animes.json
```
{
    "animes": {
        "airing": {
            "Ace Attorney S2": "http://horriblesubs.info/shows/ace-attorney-s2",
            "Akanesasu Shoujo": "http://horriblesubs.info/shows/akanesasu-shoujo",
            "Anima Yell!": "http://horriblesubs.info/shows/anima-yell",
            "Bakumatsu": "http://horriblesubs.info/shows/bakumatsu",
            "Banana Fish": "http://horriblesubs.info/shows/banana-fish",
            "Beelzebub-jou no Okinimesu mama.": "http://horriblesubs.info/shows/beelzebub-jou-no-okinimesu-mama",
            "Black Clover": "http://horriblesubs.info/shows/black-clover",
        },
        "modified_date": "2018-11-29T21:39:26.826895",
        "watching": [
            "Sword Art Online - Alicization"
        ]
    }
}
```