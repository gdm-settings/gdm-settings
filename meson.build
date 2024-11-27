project('gdm-settings',
          version: '5.beta0+',
    meson_version: '>= 0.59',
  default_options: [
    'buildtype=release',

    'gtk:media-gstreamer=disabled',
    'gtk:print-cups=disabled',
    'gtk:introspection=enabled',
    'gtk:build-demos=false',
    'gtk:build-testsuite=false',
    'gtk:build-examples=false',
    'gtk:build-tests=false',

    'libadwaita:introspection=enabled',
    'libadwaita:vapi=false',
    'libadwaita:tests=false',
    'libadwaita:examples=false',
  ]
)

app_id = 'io.github.realmazharhussain.GdmSettings'

dependency('glib-2.0')
dependency('pygobject-3.0')
dependency('gtk4', version: '>=4.10')
dependency('libadwaita-1', version: '>=1.4')

i18n = import('i18n')
gnome = import('gnome')
python = import('python').find_installation('python3')

subdir('po')
subdir('data')
subdir('resources')
subdir('gdms')

configure_file(
  input: 'gdm-settings.py.in',
  output: meson.project_name(),
  install: true,
  install_dir: get_option('bindir'),
  configuration: configuration_data({
    'prefix': get_option('prefix'),
    'py_install_dir': python.get_install_dir(),
  }),
)

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
