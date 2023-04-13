project('gdm-settings',
          version: '4.alpha',
    meson_version: '>= 0.59',
  default_options: [
    'gtk:media-gstreamer=disabled',
    'gtk:print-cups=disabled',
    'gtk:introspection=enabled',
    'gtk:demos=false',
    'gtk:build-testsuite=false',
    'gtk:build-examples=false',
    'gtk:build-tests=false',

    'libadwaita:introspection=enabled',
    'libadwaita:vapi=false',
    'libadwaita:tests=false',
    'libadwaita:examples=false',
  ]
)

dependency('glib-2.0')
dependency('pygobject-3.0')
dependency('gtk4', version: '>=4.10')
dependency('libadwaita-1', version: '>=1.2')

i18n = import('i18n')
gnome = import('gnome')
python = import('python').find_installation('python3')

subdir('po')
subdir('data')
subdir('src')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
