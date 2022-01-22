project('gdm-settings',
        version: '0.1.1-alpha',
  meson_version: '>= 0.50.0')

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

application_name='Login Settings'
description = 'A settings app for GNOME\'s Login Manager (GDM)'
application_id='com.github.realmazharhussain.GdmSettings'
schema_path = '/com/github/realmazharhussain/GdmSettings/'

conf = configuration_data()
conf.set('project_name', meson.project_name())
conf.set('version', meson.project_version())
conf.set('application_name', application_name)
conf.set('description', description)
conf.set('application_id', application_id)
conf.set('schema_path', schema_path)

subdir('src')
subdir('data')
