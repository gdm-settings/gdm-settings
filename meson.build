project('gdm-settings',
          version: '3.alpha.0',
    meson_version: '>= 0.59',
  default_options: [
    #'buildtype=release',

    'libadwaita:introspection=enabled',
    'libadwaita:vapi=false',
    'libadwaita:tests=false',
    'libadwaita:examples=false',
  ]
)

dependency('glib-2.0')
dependency('pygobject-3.0')
dependency('libadwaita-1')

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
