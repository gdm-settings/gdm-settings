py_module_dir = python.get_install_dir() / 'gdm_settings'

config = configuration_data({
  'prefix': get_option('prefix'),
  'data_dir': get_option('prefix') / get_option('datadir'),
  'locale_dir': get_option('prefix') / get_option('localedir'),
  'py_install_dir': python.get_install_dir(),
})

configure_file(
  input: 'config.py.in',
  output: 'config.py',
  install: true,
  install_dir: py_module_dir,
  configuration: config,
)

install_data(
  files('__init__.py'),
  install_dir: py_module_dir
)

install_subdir('lib',
  install_dir: py_module_dir
)

subdir('app')

configure_file(
  input: 'gdm-settings.py.in',
  output: meson.project_name(),
  install: true,
  install_dir: get_option('bindir'),
  configuration: config,
)
