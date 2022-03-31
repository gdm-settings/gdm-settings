project('gdm-settings',
        version: '0.4',
  meson_version: '>= 0.58',
  )

dependency('glib-2.0')
dependency('pygobject-3.0')
dependency('libadwaita-1')

version = meson.project_version()
project_name = meson.project_name()
application_name='Login Manager Settings'
description = 'A settings app for GNOME\'s Login Manager (GDM)'
application_id='io.github.realmazharhussain.GdmSettings'
schema_path = '/io/github/realmazharhussain/GdmSettings/'

python = import('python')
python3 = python.find_installation('python3')
py_modules_dir = python3.get_install_dir()
py_module_name = meson.project_name().underscorify()
py_proj_dir = py_modules_dir / py_module_name

prefix = get_option('prefix')
bindir = get_option('bindir')
localedir = prefix / get_option('localedir')
datadir = prefix / get_option('datadir')
pkgdatadir = datadir / meson.project_name()

conf = configuration_data()
conf.set('project_name',     project_name)
conf.set('application_name', application_name)
conf.set('version',          version)
conf.set('description',      description)
conf.set('application_id',   application_id)
conf.set('schema_path',      schema_path)
conf.set('prefix',           prefix)
conf.set('py_modules_dir',   py_modules_dir)
conf.set('py_module_name',   py_module_name)
conf.set('py_proj_dir',      py_proj_dir)
conf.set('bindir',           bindir)
conf.set('datadir',          datadir)
conf.set('localedir',        localedir)

i18n = import('i18n')

subdir('data')
subdir('src')
subdir('po')

subdir('build-aux')
