py_app_dir = py_module_dir / 'app'

configure_file(
          input: 'info.py.in',
         output: '@BASENAME@',
        install: true,
    install_dir: py_app_dir,
  configuration: configuration_data({
            'prefix': get_option('prefix'),
           'version': meson.project_version(),
          'data_dir': get_option('prefix') / get_option('datadir') / meson.project_name(),
        'build_type': get_option('buildtype'),
  }),
)

source_files = files(
  '__init__.py',
  'about.py',
  'app.py',
  'enums.py',
  'env.py',
  'gr_utils.py',
  'log.py',
  'privilege_escalation.py',
  'settings.py',
  'theme_lists.py',
  'utils.py',
  'window.py',
)
install_data(source_files,
  install_dir: py_app_dir
)
install_subdir('pages',
  install_dir: py_app_dir
)
