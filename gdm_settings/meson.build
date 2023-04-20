py_module_dir = python.get_install_dir() / 'gdm_settings'

install_subdir('lib',
  install_dir: py_module_dir
)

subdir('app')

configure_file(
          input: 'gdm-settings.py.in',
         output: meson.project_name(),
        install: true,
    install_dir: get_option('bindir'),
  configuration: configuration_data({
            'prefix': get_option('prefix'),
          'data_dir': get_option('prefix') / get_option('datadir'),
        'locale_dir': get_option('prefix') / get_option('localedir'),
    'py_install_dir': python.get_install_dir(),
  }),
)
