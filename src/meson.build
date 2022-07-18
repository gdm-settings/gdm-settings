configure_file(
          input: 'gdm-settings.in',
         output: '@BASENAME@',
  configuration: conf,
        install: true,
    install_dir: get_option('bindir'),
)

configure_file(
          input: 'info.py.in',
         output: '@BASENAME@',
  configuration: conf,
        install: true,
    install_dir: py_proj_dir,
)

source_files = files(
  'app.py',
  'dialogs.py',
  'enums.py',
  'env.py',
  'settings.py',
  'theme_lists.py',
  'utils.py',
)
install_data(source_files, install_dir: py_proj_dir)

subdir('blueprints')
