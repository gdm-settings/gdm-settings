configure_file(
  input:  'info.py.in',
  output: 'info.py',
  configuration: conf,
  install: true,
  install_dir: pkgdatadir
)

source_files = [
  '__init__.py',
  'settings_manager.py',
  'gdm-settings.py',
]
install_data(source_files, install_dir: pkgdatadir)

subdir('blueprints')
