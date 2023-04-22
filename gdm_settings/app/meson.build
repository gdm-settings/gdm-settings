py_app_dir = py_module_dir / 'app'

source_files = files(
  '__init__.py',
  'about.py',
  'app.py',
  'gr_utils.py',
  'log.py',
  'cmd.py',
  'settings.py',
  'theme_lists.py',
  'window.py',
)
install_data(source_files,
  install_dir: py_app_dir
)
install_subdir('pages',
  install_dir: py_app_dir
)
