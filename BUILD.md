## Dependencies

### AppImageTool

We need to install `appimagetool` for packaging the appimage.
It is (as of now) not available in the package managers of Arch or Ubuntu.

```bash
wget https://github.com/AppImage/appimagetool/releases/download/1.9.1/appimagetool-x86_64.AppImage

# Verify checksums
echo "ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0  appimagetool-x86_64.AppImage" | sha256sum --check

chmod +x appimagetool-x86_64.AppImage

mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
```

### Arch

```bash
sudo pacman -Sy pkgconf gdk-pixbuf2 glib2-devel meson blueprint-compiler

# Fix gdk-pixbuf2 loaders missing
sudo mkdir -p /usr/lib/gdk-pixbuf-2.0/2.10.0/loaders
sudo gdk-pixbuf-query-loaders --update-cache
```

### Ubuntu 25.10

```bash
# Required for the Meson build
sudo apt install meson libadwaita-1-dev sassc libgtk-4-dev python-gi-dev blueprint-compiler gettext

# Required for building the appimage
sudo apt install libnss-db gir1.2-rsvg-2.0 gir1.2-tracker-3.0 libturbojpeg0 gir1.2-cloudproviders-0.3.0 tinysparql
```

## Build

Run `./appimage/build.sh`

## Known Issues

If you get the error `libc.mo` or `glib20.mo` not found, then you're missing language packs.
This issue commonly occurs in minimal Linux installations or containers where language packs aren't installed by default.
Install a language pack, e.g., `apt install language-pack-en language-pack-en-base language-pack-gnome-en-base`
