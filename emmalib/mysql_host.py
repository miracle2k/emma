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
import _mysql
import _mysql_exceptions
import time
import re
import traceback
from mysql_db import *

class mysql_host:
	def __init__(self, *args):
		if len(args) == 2:
			# unpickle
			self.sql_log, self.msg_log = args
			print "unpickle host!"
			if self.connected:
				db_name = self.current_db.name
				self.current_db = None
				print "try to reconnect after unpickling!"
				self.connect()
				print "resulting handle:", self.handle
			if self.connected:
				print "unpickling databases!", self.handle
				for name, db in self.databases.iteritems():
					db.__init__(self)
				self._use_db(db_name, True)
		else:
			self.sql_log, self.msg_log, self.name, self.host, self.port, self.user, self.password, self.database, self.connect_timeout = args
			self.connected = False
			self.databases = {} # name -> db_object
			self.current_db = None
			self.expanded = False
			self.handle = None
			
		self.processlist = None
		self.update_ui = None
		self.last_error = ""
		
	def __getstate__(self):
		d = dict(self.__dict__)
		for i in ["sql_log", "msg_log", "handle", "processlist", "update_ui", "update_ui_args"]:
			del d[i]
		#print "host will pickle:", d
		return d
		
	def get_connection_string(self):
		if self.port != "":
			output = "%s:%s" % (self.host, self.port)
		else:
			output = "%s" % self.host
		output += ",%s,%s,%s" % (self.user, self.password, self.database)
		return output
		
	def set_update_ui(self, update_ui, *args):
		self.update_ui = update_ui
		self.update_ui_args = args
	
	def connect(self):
		c = {
			"host": self.host, 
			"user": self.user, 
			"passwd": self.password, 
			"connect_timeout": int(self.connect_timeout)
			}
		if self.port:
			c["port"] = int(self.port)
		if self.database:
			c["db"] = self.database

		try:
			self.handle = _mysql.connect(**c)
		except _mysql_exceptions.OperationalError:
			self.connected = False
			self.msg_log("%s: %s" % (sys.exc_type, sys.exc_value[1]))
			return
		self.connected = True
		self.refresh()
		if self.database: self._use_db(self.database)
		
	def ping(self):
		try:
			self.handle.ping()
			return True
		except:
			self.connected = False
			self.msg_log(sys.exc_value[1])
			return False
		
	def close(self):
		self.databases = {}
		self.processlist = None
		if self.handle:
			self.handle.close()
			self.handle = None
		self.current_db = None
		self.connected = False
		if self.update_ui: self.update_ui(self, *self.update_ui_args)
		
	def query(self, query, check_use=True, append_to_log=True, encoding=None):
		if not self.handle:
			self.msg_log("not connected! can't execute %s, %s, %s" % (query, str(self.handle), str(self)))
			return
		if append_to_log:
			self.sql_log(query)
		try:
			self.query_time = 0
			start = time.time()
			if encoding:
				query = query.encode(encoding, "ignore")
			self.handle.query(query)
			self.query_time = time.time() - start
		except:
			#print "error code:", sys.exc_value[0]
			try:
				self.last_error = sys.exc_value[1]
			except:
				self.last_error = str(sys.exc_value)
			s = sys.exc_value[1]
			#print "error:", [s]
			s = s.replace("You have an error in your SQL syntax.  Check the manual that corresponds to your MySQL server version for the right syntax to use near ", "MySQL syntax error at ")
			self.msg_log(s)
			if sys.exc_value[0] == 2013:
				# lost connection
				self.close()
			return False
			
		if not check_use: return True
		match = re.match("(?is)^([ \r\n\t]*|#[^\n]*)*(use[ \r\n\t]*).*", query)
		if match:
			dbname = query[match.end(2):].strip("`; \t\r\n")
			print "use db: '%s'" % dbname
			self._use_db(dbname, False)
			# reexecute to reset field_count and so on...
			self.handle.query(query)
		return True
		
	def _use_db(self, name, do_query=True):
		if self.current_db and name == self.current_db.name: return
		if do_query: self.query("use `%s`" % name, False)
		try:
			self.current_db = self.databases[name]
		except KeyError:
			print "Warning: used an unknown database %r! please refresh host!\n%s" % (name, "".join(traceback.format_stack()))
		
	def select_database(self, db):
		self._use_db(db.name)
		
	def refresh(self):
		self.query("show databases")
		result = self.handle.store_result()
		old = dict(self.databases)
		db_id = len(old)
		for row in result.fetch_row(0):
			if not row[0] in old:
				self.databases[row[0]] = mysql_db(self, row[0])
			else:
				del old[row[0]]
		for db in old.keys():
			print "remove database", db
			del self.databases[db]
		
	def refresh_processlist(self):
		if not self.query("show processlist"): return
		result = self.handle.store_result()
		self.processlist = (result.describe(), result.fetch_row(0))
		
	def insert_id(self):
		return self.handle.insert_id()
		
	def escape(self, s):
		if s is None:
			return s
		return self.handle.escape_string(s)
	
