configure_file(
  input:  'info.py.in',
  output: 'info.py',
  configuration: conf,
  install: true,
  install_dir: py_proj_dir,
)

source_files = [
  '__init__.py',
  'utils.py',
  'env.py',
  'settings_manager.py',
  'gdm_settings_gui.py',
]
install_data(source_files, install_dir: py_proj_dir)

configure_file(
  input: 'gdm-settings.in',
  output: '@BASENAME@',
  configuration: conf,
  install_dir: get_option('bindir'),
)

subdir('blueprints')
