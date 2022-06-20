project('gdm-settings',
        version: '0.6.1',
  meson_version: '>= 0.58',
)

dependency('glib-2.0')
dependency('pygobject-3.0')
dependency('libadwaita-1')

project_name = meson.project_name()
version      = meson.project_version()

build_type   = get_option('buildtype')
prefix       = get_option('prefix')
bin_dir      = get_option('bindir')
locale_dir   = prefix / get_option('localedir')
data_dir     = prefix / get_option('datadir')
pkg_data_dir = data_dir / project_name

python         = import('python')
python3        = python.find_installation('python3')
py_modules_dir = python3.get_install_dir()
py_module_name = project_name.underscorify()
py_proj_dir    = py_modules_dir / py_module_name

conf = configuration_data()
conf.set('build_type',     build_type)
conf.set('project_name',   project_name)
conf.set('version',        version)
conf.set('locale_dir',     locale_dir)
conf.set('py_modules_dir', py_modules_dir)
conf.set('py_module_name', py_module_name)

i18n = import('i18n')

subdir('po')
subdir('data')
subdir('src')

meson.add_install_script('build-aux/postinstall.py')
