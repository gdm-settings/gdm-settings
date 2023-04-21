py_module_dir = python.get_install_dir() / 'gdm_settings'

configure_file(
  input: 'config.py.in',
  output: 'config.py',
  install: true,
  install_dir: py_module_dir,
  configuration: configuration_data({
    'prefix': get_option('prefix'),
    'version': meson.project_version(),
    'datadir': get_option('prefix') / get_option('datadir'),
    'localedir': get_option('prefix') / get_option('localedir'),
    'buildtype': get_option('buildtype'),
  }),
)

install_data(files(
    '__init__.py',
    'enums.py',
    'widgets.py',
    'utils.py',
  ),

  install_dir: py_module_dir
)

subdir('app')
