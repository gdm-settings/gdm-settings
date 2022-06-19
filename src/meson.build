configure_file(
  input: 'gdm-settings.in',
  output: '@BASENAME@',
  configuration: conf,
  install_dir: get_option('bindir'),
)

configure_file(
  input:  'info.py.in',
  output: 'info.py',
  configuration: conf,
  install: true,
  install_dir: py_proj_dir,
)

install_data([
  '__init__.py',
  'colors.py',
  'dialogs.py',
  'env.py',
  'gui.py',
  'settings_manager.py',
  'utils.py',
  ],
  install_dir: py_proj_dir,
)

subdir('blueprints')
