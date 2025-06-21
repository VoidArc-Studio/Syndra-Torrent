from gi.repository import Gtk, Adw
import json

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Settings", transient_for=parent, modal=True)
        self.set_default_size(400, 300)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(12)
        box.set_margin_bottom(12)
        box.set_margin_start(12)
        box.set_margin_end(12)

        # Download directory
        dir_label = Gtk.Label(label="Download Directory")
        self.dir_entry = Gtk.Entry()
        dir_button = Gtk.Button(label="Browse")
        dir_button.connect("clicked", self.on_browse)
        dir_box = Gtk.Box(spacing=6)
        dir_box.append(self.dir_entry)
        dir_box.append(dir_button)
        box.append(dir_label)
        box.append(dir_box)

        # Theme
        theme_label = Gtk.Label(label="Theme")
        self.theme_combo = Gtk.ComboBoxText()
        self.theme_combo.append_text("Light")
        self.theme_combo.append_text("Dark")
        box.append(theme_label)
        box.append(self.theme_combo)

        # Speed limits
        down_label = Gtk.Label(label="Max Download Speed (KB/s)")
        self.down_entry = Gtk.Entry()
        up_label = Gtk.Label(label="Max Upload Speed (KB/s)")
        self.up_entry = Gtk.Entry()
        box.append(down_label)
        box.append(self.down_entry)
        box.append(up_label)
        box.append(self.up_entry)

        # Buttons
        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.on_save)
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self.on_cancel)
        button_box = Gtk.Box(spacing=6)
        button_box.append(cancel_button)
        button_box.append(save_button)
        box.append(button_box)

        self.set_content(box)

        # Load config
        self.load_config()

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.dir_entry.set_text(config.get("download_dir", "~/Downloads"))
                self.theme_combo.set_active(0 if config.get("theme", "light") == "light" else 1)
                self.down_entry.set_text(str(config.get("max_download_speed", 0)))
                self.up_entry.set_text(str(config.get("max_upload_speed", 0)))
        except:
            pass

    def on_browse(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select Download Directory",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Select", Gtk.ResponseType.ACCEPT)
        dialog.connect("response", self.on_dir_dialog_response)
        dialog.present()

    def on_dir_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            folder = dialog.get_file()
            if folder:
                self.dir_entry.set_text(folder.get_path())
        dialog.destroy()

    def on_save(self, button):
        config = {
            "download_dir": self.dir_entry.get_text(),
            "theme": "light" if self.theme_combo.get_active() == 0 else "dark",
            "max_download_speed": int(self.down_entry.get_text() or "0"),
            "max_upload_speed": int(self.up_entry.get_text() or "0")
        }
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        # Apply theme
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(f"styles/{config['theme']}.css")
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.destroy()

    def on_cancel(self, button):
        self.destroy()
