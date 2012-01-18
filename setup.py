#!/usr/bin/env python2.4
import os
import os.path
import sys
from glob import glob
from distutils.core import setup

from emmalib import version 

icon_data = glob('icons/*.png')
glade_data = ['emmalib/emma.glade', 'emmalib/plugins/table_editor/table_editor.glade']
theme_data = ["theme/README.html"]
theme_gtk_data = glob("theme/gtk-2.0/*")
other_data = ['changelog']

setup(name="emma",
      version=version,
      description="emma is the extendable mysql managing assistant",
      author="Florian Schmidt",
      author_email="flo@fastflo.de",
      url="http://emma.sourceforge.net",
      scripts=['emma'],
	  package_dir={'emmalib': 'emmalib'},
      packages=[
            'emmalib', 
            'emmalib.plugins.table_editor',
            'emmalib.plugins.pretty_format'
      ],
      data_files=[
		("share/emma/icons", icon_data),
		("share/emma/glade", glade_data),
		("share/emma/theme", theme_data),
		("share/emma/theme/gtk-2.0", theme_gtk_data),
		("share/emma", other_data),
      ],
      license="GPL",
      long_description="""
Emma is a graphical toolkit for MySQL database developers and administrators
It provides dialogs to create or modify mysql databases, tables and 
associated indexes. it has a built-in syntax highlighting sql editor with 
table- and fieldname tab-completion and automatic sql statement formatting. 
the results of an executed query are displayed in a resultset where the record-
data can be edited by the user, if the sql statemant allows for it. the sql 
editor and resultset-view are grouped in tabs. results can be exported to csv 
files. multiple simultanios opend mysql connections are possible. 
Emma is the successor of yamysqlfront.
"""
      )

