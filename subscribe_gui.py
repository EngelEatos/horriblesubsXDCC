"""generate config file for subscribing animes with gui"""
import os
import tkinter as tk
from datetime import datetime
import config
import showparser
import json

CHECKVAR = dict()
ROOT = tk.Tk()
ANIME_LOADER = config.AnimeSettingsLoader()


def save():
    """save selected animes to file"""
    selected_animes = CHECKVAR.keys()
    result = []
    for anime in selected_animes:
        if CHECKVAR.get(anime).get() == 1:
            result.append(anime)
    ANIME_LOADER.set_watching(result)
    ANIME_LOADER.update_modified_date()
    ROOT.quit()


class Frame(tk.Frame):  # pylint: disable=too-many-ancestors
    """frame"""

    def __init__(self, root, airing, watching, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        self.airing = airing
        self.watching = watching
        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.text = tk.Text(self, width=40, height=20,
                            yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.text.yview)
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        for idx, anime in enumerate(self.airing):
            CHECKVAR[anime] = tk.IntVar()
            check_btn = tk.Checkbutton(
                self, text=anime, variable=CHECKVAR[anime])
            check_btn.config(bg="white")
            if anime in self.watching:
                check_btn.toggle()
            self.text.window_create("end", window=check_btn)
            self.text.insert("end", "\n")
        self.btn = tk.Button(text='save', command=lambda: save())
        self.btn.pack(side="bottom", fill="both", expand=True)
        self.text.config(state="disabled")


def check_expired(date):
    """check if config file is older than 10h"""
    if not date:
        return None
    delta = date - datetime.now()
    mod = divmod(delta.days * 86400 + delta.seconds, 60)
    return mod[0] >= 600


def create_gui():
    """create and show frame"""
    modified_date = ANIME_LOADER.get_modified_date()
    if check_expired(modified_date):
        ANIME_LOADER.update()
    airing = ANIME_LOADER.get_airing()
    watching = ANIME_LOADER.get_watching()
    Frame(ROOT, airing, watching).pack(side="top", fill="both", expand=True)
    ROOT.mainloop()


def main():
    """Main-Methode"""
    create_gui()


if __name__ == '__main__':
    main()
