# -*- coding: utf-8 -*-
# emma
#
# Copyright (C) 2006 Florian Schmidt (flo@fastflo.de)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

import sys
import traceback
from mysql_table import *

class mysql_db:
	def __init__(self, host, name = None):
		self.handle = host.handle
		self.host = host
		if name != None:
			self.name = name
			self.expanded = False
			self.status_headers = []
			self.tables = {}
		else:
			print "unpickling tables!", self.handle
			for name, table in self.tables.iteritems():
				table.handle = self.handle
		#self.id = id
		
	def __getstate__(self):
		d = dict(self.__dict__)
		for i in ["handle"]:
			del d[i]
		#print "db will pickle:", d
		return d
		
	def refresh(self):
		self.host.select_database(self)
		if not self.host.query("show table status"): return
		new_tables = []
		
		result = self.handle.store_result()
		self.status_headers = []
		for h in result.describe():
			self.status_headers.append(h[0])
		old = dict(zip(self.tables.keys(), range(len(self.tables))))
		for row in result.fetch_row(0):
			if not row[0] in old:
				#print "new table", row[0]
				self.tables[row[0]] = mysql_table(self, row, result.describe())
				new_tables.append(row[0])
			else:
				#print "known table", row[0]
				# todo update self.tables[row[0]] with row!
				del old[row[0]]
				
		for table in old:
			print "destroy table", table
			del self.tables[table]
		return new_tables

	def query(self, query, check_use=True, append_to_log=True):
		self.host.select_database(self)
		return self.host.query(query, check_use, append_to_log)
