"""gui"""
from datetime import datetime

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from animeinfo import AnimeInfo
from animesettingsloader import AnimeSettingsLoader


ANIME_LOADER = AnimeSettingsLoader()


class AnimeInfoWindow(Gtk.Dialog):
    """gtk3 window"""

    def __init__(self, parent, name, url):
        Gtk.Dialog.__init__(self, name, parent, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        self.set_default_size(500, 50)
        self.set_modal(1)
        self.set_border_width(10)

        anime_info = AnimeInfo(name, url)
        image_file, desc = anime_info.get_anime_info()

        hbox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.set_homogeneous(True)

        vbox_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_left.set_homogeneous(False)

        vbox_right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_right.set_homogeneous(False)

        hbox.pack_start(vbox_left, True, True, 0)
        hbox.pack_start(vbox_right, True, True, 0)

        image_area = Gtk.Box()
        image = Gtk.Image()
        image.set_from_file(image_file)
        image_area.add(image)
        vbox_left.pack_start(image_area, True, True, 0)

        desc_label = Gtk.Label(desc)
        desc_label.set_line_wrap(True)
        desc_label.set_justify(Gtk.Justification.FILL)
        vbox_right.pack_start(desc_label, True, True, 0)

        box = self.get_content_area()

        box.add(hbox)
        self.show_all()


class SubWindow(Gtk.Window):
    """gtk3 window"""

    def __init__(self, airing, watching):
        Gtk.Window.__init__(self, title="Subsribe GUI")
        self.set_default_size(420, 500)
        self.set_resizable(False)
        self.liststore = Gtk.ListStore(str, bool)
        self.airing = airing
        for anime in self.airing.keys():
            self.liststore.append(
                [anime, True if anime in watching else False])
        treeview = Gtk.TreeView(model=self.liststore)
        treeview.connect('row-activated', self.on_row_activated)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Anime", renderer_text, text=0)
        column_text.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column_text.set_max_width(350)
        treeview.append_column(column_text)

        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_cell_toggled)

        column_toggle = Gtk.TreeViewColumn(
            "watching", renderer_toggle, active=1)
        column_toggle.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column_toggle.set_max_width(70)
        treeview.append_column(column_toggle)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(treeview)

        save_btn = Gtk.Button.new_with_label("Save")
        save_btn.connect("clicked", self.on_save_clicked)
        save_btn.set_size_request(80, 25)

        self.mainbox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.mainbox)

        self.mainbox.pack_start(scrolled_window, True, True, 0)
        self.mainbox.pack_start(save_btn, False, False, 0)

    def on_row_activated(self, widget, path, column):
        """on row activated"""
        treeiter = self.liststore.get_iter(path)
        anime = self.liststore.get_value(treeiter, 0)
        url = self.airing[anime]
        if url != "not yet":
            dialog = AnimeInfoWindow(self, anime, url)
            dialog.run()
            dialog.destroy()

    def on_cell_toggled(self, widget, path):
        """on checkbox toggle"""
        treeiter = self.liststore.get_iter(path)
        self.liststore.set_value(
            treeiter, 1, not self.liststore.get_value(treeiter, 1))

    def on_save_clicked(self, button):
        """on btn save click"""
        result = []
        for i in range(0, len(self.liststore)):
            treeiter = self.liststore.get_iter(i)
            if self.liststore.get_value(treeiter, 1):
                result.append(self.liststore.get_value(treeiter, 0))
        ANIME_LOADER.set_watching(result)
        ANIME_LOADER.update_modified_date()
        ANIME_LOADER.save()
        Gtk.main_quit()


def check_expired(date):
    """check if config file is older than 10h"""
    if not date:
        return None
    delta = datetime.now() - date
    mod = divmod(delta.days * 86400 + delta.seconds, 60)
    return int(mod[0]) >= 600


def main():
    """main"""
    modified_date = ANIME_LOADER.get_modified_date()
    if check_expired(modified_date):
        ANIME_LOADER.update()
    airing = ANIME_LOADER.get_airing()
    watching = ANIME_LOADER.get_watching()
    win = SubWindow(airing, watching)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
