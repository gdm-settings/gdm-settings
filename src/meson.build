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
  '__init__.py',
  'app.py',
  'dialogs.py',
  'env.py',
  'settings_manager.py',
  'utils.py',
)
install_data(source_files, install_dir: py_proj_dir)

subdir('blueprints')
