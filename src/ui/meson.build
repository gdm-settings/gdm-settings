ui_dir = join_paths(pkgdatadir, 'ui')

configure_file(
  input:  'about-dialog.ui.in',
  output: 'about-dialog.ui',
  configuration: conf,
  install: true,
  install_dir: ui_dir
)

ui_files = [
  'app-menu.ui',
  'image-chooser.ui',
  'main-window.ui',
  'theme.ui',
  'settings.ui',
  'responses.ui',
]

install_data(ui_files, install_dir: ui_dir)
