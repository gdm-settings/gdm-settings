ui_dir = join_paths(pkgdatadir, 'ui')

configure_file(
  input:  'about-dialog.ui.in',
  output: 'about-dialog.ui',
  configuration: conf,
  install: true,
  install_dir: ui_dir
)

ui_files = [
  'main-window.ui',
  'app-menu.ui',
  'image-chooser.ui',
  'responses.ui',

  'appearance-page.ui',
  'fonts-page.ui',
  'night-light-page.ui',
  'sound-page.ui',
  'top-bar-page.ui',
  'touchpad-page.ui',
]

install_data(ui_files, install_dir: ui_dir)
