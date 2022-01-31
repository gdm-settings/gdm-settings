configure_file(
  input:  'info.py.in',
  output: 'info.py',
  configuration: conf,
  install: true,
  install_dir: pkgdatadir
)

configure_file(
  input:  'about-dialog.ui.in',
  output: 'about-dialog.ui',
  configuration: conf,
  install: true,
  install_dir: pkgdatadir
)

source_files = [
  '__init__.py',

  'app-menu.ui',
  'image-chooser.ui',
  'main-window.ui',
  'theme.ui',
  'responses.ui',

  'command_elevation.py',
  'functions.py',
  'gdm-settings.py',
  'settings_manager.py',
  'settings.ui',
]

install_data(source_files, install_dir: pkgdatadir)
