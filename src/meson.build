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

  'command_elevation.py',
  'functions.py',
  'gdm-settings.py',
  'theme_settings_manager.py',
]

install_data(source_files, install_dir: pkgdatadir)
