import tkinter as tk

animes = ["Shoukoku no Altair", "Netsuzou TRap - NTR", "18if", "Knight's & Magic",
"Nana Maru San Batsu", "Saiyuki Reload Blast", "Isekai Shokudou", "Keppeki Danshi! Aoyama-kun",
"Isekai wa Smartphone to Tomo ni.", "Katsugeki Touken Ranbu", "Enmusubi no Youko-chan",
"Shingeki no Bahamut - Virgin Soul", "Gamers!", "Koi to Uso", "Re-Creators", "Jikan no Shihaisha",
"Ballroom e Youkoso", "Nora to Oujo no Noraneko Heart", "Sin - Nanatsu no Taizai", "Monster Strike 2",
"Hajimete no Gal", "Boku no Hero Academia", "Sagrada Reset", "Youkoso Jitsuryoku Shijou Shugi no Kyoushitsu e", "Aho Girl"]

def save():
    animes = checkVar.keys()
    for anime in animes:
        value = checkVar.get(anime).get()
        if value == 1:
            data.append(anime)
    print(data)

class frame(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root

        self.vsb = tk.Scrollbar(self, orient="vertical")
        self.text = tk.Text(self, width=40, height=20,
                            yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.text.yview)
        self.vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        for idx, anime in enumerate(animes):
            checkVar[anime] = tk.IntVar()
            c = tk.Checkbutton(self, text=anime, variable=checkVar[anime])
            self.text.window_create("end", window=c)
            self.text.insert("end", "\n")
        self.btn = tk.Button(text='save', command=lambda: save())
        self.btn.pack(side="bottom", fill="both", expand=True)


checkVar = dict()
data = []
root = tk.Tk()
frame(root).pack(side="top", fill="both", expand=True)
root.mainloop()
