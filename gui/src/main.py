import sys
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from window import SyndraTorrentWindow

def main():
    app = Adw.Application(application_id="org.syndra.torrent")
    app.connect("activate", on_activate)
    app.run(sys.argv)

def on_activate(app):
    win = SyndraTorrentWindow(app)
    win.present()

if __name__ == "__main__":
    main()
