import os
import json
import tkinter as tk
import config

CONFIG_FILE = config.CONFIG_FILE
checkVar = dict()
animes = ["Shoukoku no Altair", "Netsuzou TRap - NTR", "18if", "Knight's & Magic",
"Nana Maru San Batsu", "Saiyuki Reload Blast", "Isekai Shokudou", "Keppeki Danshi! Aoyama-kun",
"Isekai wa Smartphone to Tomo ni.", "Katsugeki Touken Ranbu", "Enmusubi no Youko-chan",
"Shingeki no Bahamut - Virgin Soul", "Gamers!", "Koi to Uso", "Re-Creators", "Jikan no Shihaisha",
"Ballroom e Youkoso", "Nora to Oujo no Noraneko Heart", "Sin - Nanatsu no Taizai", "Monster Strike 2",
"Hajimete no Gal", "Boku no Hero Academia", "Sagrada Reset", "Youkoso Jitsuryoku Shijou Shugi no Kyoushitsu e", "Aho Girl"]

def load():
    with open(CONFIG_FILE, 'r') as config:
        return json.load(config)

def save():
    animes = checkVar.keys()
    data = []
    for anime in animes:
        if checkVar.get(anime).get() == 1:
            result.append(anime)
    if os.path.isfile(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)

class frame(tk.Frame):
    def __init__(self, root, data, animes, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        self.data = data
        self.animes = animes
        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.text = tk.Text(self, width=40, height=20, yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.text.yview)
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        for idx, anime in enumerate(animes):
            checkVar[anime] = tk.IntVar()
            c = tk.Checkbutton(self, text=anime, variable=checkVar[anime])
            c.config(bg="white")
            if anime in self.data:
                c.toggle()
            self.text.window_create("end", window=c)
            self.text.insert("end", "\n")
        self.btn = tk.Button(text='save', command=lambda: save())
        self.btn.pack(side="bottom", fill="both", expand=True)
        self.text.config(state="disabled")

def create_gui(animes):
    data = load()
    root = tk.Tk()
    frame(root, data, animes).pack(side="top", fill="both", expand=True)
    root.mainloop()

def main():
    create_gui(animes)

if __name__ == '__main__':
    main()
