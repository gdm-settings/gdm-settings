configure_file(
          input: 'gdm-settings.py.in',
         output: meson.project_name(),
        install: true,
    install_dir: get_option('bindir'),
  configuration: configuration_data({
            'prefix': get_option('prefix'),
        'locale_dir': get_option('prefix') / get_option('localedir'),
    'py_install_dir': python.get_install_dir(),
  }),
)

configure_file(
          input: 'info.py.in',
         output: '@BASENAME@',
        install: true,
    install_dir: python.get_install_dir() / 'gdm_settings',
  configuration: configuration_data({
            'prefix': get_option('prefix'),
           'version': meson.project_version(),
          'data_dir': get_option('prefix') / get_option('datadir') / meson.project_name(),
        'build_type': get_option('buildtype'),
  }),
)

source_files = files(
  '__init__.py',
  'app.py',
  'bind_utils.py',
  'common_widgets.py',
  'dialogs.py',
  'enums.py',
  'env.py',
  'gr_utils.py',
  'settings.py',
  'theme_lists.py',
  'utils.py',
)
install_data(source_files,
  install_dir: python.get_install_dir() / 'gdm_settings'
)

subdir('blueprints')
