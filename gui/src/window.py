import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GLib
import grpc
from torrent_list import TorrentList
from settings import SettingsDialog
from torrent_pb2 import *
from torrent_pb2_grpc import TorrentServiceStub

class SyndraTorrentWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Syndra Torrent")
        self.set_default_size(1000, 700)

        # gRPC client
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = TorrentServiceStub(self.channel)

        # Header bar
        header = Adw.HeaderBar()
        logo = Gtk.Image.new_from_file("assets/logo.png")
        logo.set_pixel_size(32)
        header.pack_start(logo)

        # Action buttons
        add_button = Gtk.Button(label="Add Torrent")
        add_button.connect("clicked", self.on_add_torrent)
        header.pack_end(add_button)

        settings_button = Gtk.Button(label="Settings")
        settings_button.connect("clicked", self.on_settings)
        header.pack_end(settings_button)

        # Sidebar
        self.sidebar = Gtk.ListBox()
        self.sidebar.set_selection_mode(Gtk.SelectionMode.SINGLE)
        filters = ["All", "Active", "Completed", "Paused", "Errors"]
        for f in filters:
            row = Gtk.ListBoxRow()
            row.set_child(Gtk.Label(label=f))
            self.sidebar.append(row)
        self.sidebar.connect("row-activated", self.on_sidebar_row_activated)

        # Torrent list
        self.torrent_list = TorrentList(self.stub)
        self.torrent_list.connect("row-activated", self.on_torrent_selected)

        # Progress bar
        self.progress = Gtk.ProgressBar()
        self.progress.set_show_text(True)

        # Detailed view (notebook)
        self.notebook = Gtk.Notebook()
        self.notebook.append_page(self.create_files_tab(), Gtk.Label(label="Files"))
        self.notebook.append_page(self.create_peers_tab(), Gtk.Label(label="Peers"))
        self.notebook.append_page(self.create_trackers_tab(), Gtk.Label(label="Trackers"))

        # Layout
        sidebar_scroll = Gtk.ScrolledWindow()
        sidebar_scroll.set_child(self.sidebar)
        sidebar_scroll.set_min_content_width(200)

        torrent_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        torrent_box.append(self.torrent_list)
        torrent_box.append(self.progress)
        torrent_box.append(self.notebook)

        paned = Gtk.Paned()
        paned.set_start_child(sidebar_scroll)
        paned.set_end_child(torrent_box)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.append(header)
        main_box.append(paned)
        self.set_content(main_box)

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("styles/theme.css")
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Periodic update
        GLib.timeout_add_seconds(1, self.update_torrent_list)

    def create_files_tab(self):
        self.files_store = Gio.ListStore(item_type=str)
        treeview = Gtk.TreeView(model=self.files_store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("File", renderer, text=0)
        column.set_resizable(True)
        treeview.append_column(column)
        scroll = Gtk.ScrolledWindow()
        scroll.set_child(treeview)
        scroll.set_vexpand(True)
        return scroll

    def create_peers_tab(self):
        self.peers_store = Gio.ListStore(item_type=str)
        treeview = Gtk.TreeView(model=self.peers_store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Peer", renderer, text=0)
        column.set_resizable(True)
        treeview.append_column(column)
        scroll = Gtk.ScrolledWindow()
        scroll.set_child(treeview)
        scroll.set_vexpand(True)
        return scroll

    def create_trackers_tab(self):
        self.trackers_store = Gio.ListStore(item_type=str)
        treeview = Gtk.TreeView(model=self.trackers_store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Tracker", renderer, text=0)
        column.set_resizable(True)
        treeview.append_column(column)
        scroll = Gtk.ScrolledWindow()
        scroll.set_child(treeview)
        scroll.set_vexpand(True)
        return scroll

    def on_add_torrent(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Add Torrent",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN
        )
        filter_torrent = Gtk.FileFilter()
        filter_torrent.set_name("Torrent files")
        filter_torrent.add_mime_type("application/x-bittorrent")
        dialog.add_filter(filter_torrent)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Add", Gtk.ResponseType.ACCEPT)
        dialog.connect("response", self.on_file_dialog_response)
        dialog.present()

    def on_file_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file:
                # Placeholder: assumes magnet link for simplicity
                magnet = "magnet:?xt=urn:btih:examplehash"  # Replace with actual file parsing
                response = self.stub.AddTorrent(AddTorrentRequest(magnet_link=magnet))
                if response.success:
                    self.torrent_list.refresh()
        dialog.destroy()

    def on_settings(self, button):
        dialog = SettingsDialog(self)
        dialog.present()

    def on_sidebar_row_activated(self, listbox, row):
        label = row.get_child().get_label()
        self.torrent_list.filter_torrents(label.lower())

    def on_torrent_selected(self, treeview, path, column):
        torrent = self.torrent_list.get_selected_torrent()
        if torrent:
            self.progress.set_fraction(torrent.progress)
            self.progress.set_text(f"{torrent.progress * 100:.1f}%")
            self.files_store.remove_all()
            for f in torrent.files:
                self.files_store.append(f)
            self.peers_store.remove_all()
            self.peers_store.append(f"{torrent.peers} peers")
            self.trackers_store.remove_all()
            self.trackers_store.append("tracker.example.com")  # Placeholder

    def update_torrent_list(self):
        self.torrent_list.refresh()
        return True
