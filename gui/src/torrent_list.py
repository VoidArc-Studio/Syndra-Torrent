from gi.repository import Gtk, Gio
from torrent_pb2 import TorrentStatus

class TorrentList(Gtk.TreeView):
    def __init__(self, stub):
        self.stub = stub
        self.store = Gio.ListStore(item_type=TorrentStatus)
        super().__init__(model=self.store)
        self.filter_status = "all"
        self.set_grid_lines(Gtk.TreeViewGridLines.BOTH)

        # Columns
        columns = [
            ("Name", 0, 300, lambda: Gtk.CellRendererText(), "text"),
            ("Progress", 1, 100, self.render_progress, "value"),
            ("Download", 2, 100, lambda: Gtk.CellRendererText(), "text"),
            ("Upload", 3, 100, lambda: Gtk.CellRendererText(), "text"),
            ("ETA", 4, 100, self.render_eta, "text"),
            ("Status", 5, 100, lambda: Gtk.CellRendererText(), "text")
        ]
        for title, col_id, width, render_func, prop in columns:
            renderer = render_func()
            column = Gtk.TreeViewColumn(title, renderer)
            column.add_attribute(renderer, prop, col_id)
            column.set_resizable(True)
            column.set_fixed_width(width)
            self.append_column(column)

        # Context menu
        self.menu = Gtk.Menu()
        pause = Gtk.MenuItem(label="Pause")
        pause.connect("activate", self.on_pause)
        resume = Gtk.MenuItem(label="Resume")
        resume.connect("activate", self.on_resume)
        remove = Gtk.MenuItem(label="Remove")
        remove.connect("activate", self.on_remove)
        self.menu.append(pause)
        self.menu.append(resume)
        self.menu.append(remove)
        self.menu.show_all()
        self.connect("button-press-event", self.on_button_press)

    def render_progress(self):
        renderer = Gtk.CellRendererProgress()
        renderer.set_property("text", "%d%%")
        return renderer

    def render_eta(self):
        renderer = Gtk.CellRendererText()
        return renderer

    def refresh(self):
        response = self.stub.GetStatus(GetStatusRequest())
        self.store.remove_all()
        for torrent in response.torrents:
            if self.filter_status == "all" or self.filter_status in torrent.status.lower():
                self.store.append(torrent)

    def filter_torrents(self, status):
        self.filter_status = status
        self.refresh()

    def get_selected_torrent(self):
        selection = self.get_selection()
        model, treeiter = selection.get_selected()
        return model[treeiter][0] if treeiter else None

    def on_button_press(self, widget, event):
        if event.button == 3:  # Right click
            self.menu.popup(None, None, None, None, event.button, event.time)
            return True
        return False

    def on_pause(self, widget):
        torrent = self.get_selected_torrent()
        if torrent:
            self.stub.PauseTorrent(PauseTorrentRequest(torrent_id=torrent.torrent_id))
            self.refresh()

    def on_resume(self, widget):
        torrent = self.get_selected_torrent()
        if torrent:
            self.stub.ResumeTorrent(ResumeTorrentRequest(torrent_id=torrent.torrent_id))
            self.refresh()

    def on_remove(self, widget):
        torrent = self.get_selected_torrent()
        if torrent:
            self.stub.RemoveTorrent(RemoveTorrentRequest(torrent_id=torrent.torrent_id))
            self.refresh()
