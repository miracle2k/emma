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

import pango
import gtk
import traceback

class mysql_query_tab:
	def __init__(self, xml, nb):
		self.xml = xml
		self.nb = nb
		
		renameload = {
			"textview": "query_text", 
			"treeview": "query_view", 
			"save_result": "save_result",
			"save_result_sql": "save_result_sql",
			"add_record": "add_record_tool",
			"delete_record": "delete_record_tool",
			"apply_record": "apply_record_tool",
			"local_search": "local_search_button",
			"remove_order": "remove_order",
			"label": "query_label",
			"page": "first_query",
			"query_bottom_label": "query_bottom_label",
			"query_db_label": "query_db_label",
		}
		
		for attribute, xmlname in renameload.iteritems():
			self.__dict__[attribute] = xml.get_widget(xmlname)
			
		self.current_host = None
		self.current_db = None
		self.model = None
		self.last_source = None
		self.result_info = None
		self.append_iter = None
		self.save_result_sql.set_sensitive(False)
		self.last_path = None
		if hasattr(self, "query"):
			self.textview.get_buffer().set_text(self.query)
		self.last_auto_name = None

	def __getstate__(self):
		b = self.textview.get_buffer()
		d = {
			"name": self.nb.get_tab_label_text(self.page),
			"query": b.get_text(b.get_start_iter(), b.get_end_iter())
		}
		print "query will pickle:", d
		return d

	def auto_rename(self, new_auto_name):
		label = self.get_label()
		if label is None:
			return
		if self.last_auto_name is None:
			print "no last_auto_name"
			label.set_text(new_auto_name)
			self.last_auto_name = new_auto_name
			return
		current_name = label.get_text()
		if self.last_auto_name in current_name:
			print "setting new %r from old %r" % (new_auto_name, current_name)
			label.set_text(current_name.replace(self.last_auto_name, new_auto_name))
			self.last_auto_name = new_auto_name
		else:
			print "last auto name %r not in %r!" % (self.last_auto_name, current_name)
		return

	def get_label(self):
		tab_widget = self.nb.get_tab_label(self.page)
		if not tab_widget:
			print "no tab widget"
			return
		labels = filter(lambda w: type(w) == gtk.Label, tab_widget.get_children())
		if not labels:
			print "no label found!"
			return
		return labels[0]

	def user_rename(self, new_name):
		tab_widget = self.nb.get_tab_label(self.page)
		label = self.get_label()
		label.set_text(new_name)

	def destroy(self):
		# try to free some memory
		if self.model: self.model.clear()
		self.textview.get_buffer().set_text("")
		del self.treeview
		del self.model
		del self.textview
		self.treeview = None
		self.model = None
		self.textview = None
		self.update_db_label()
		
	def set(self, text):
		self.last_source = text
		self.textview.get_buffer().set_text(text)
	
	def update_db_label(self):
		h = self.current_host
		d = self.current_db
		if not h:
			self.query_db_label.set_label("no host/database selected")
			return
		title = "selected host"
		if d:
			dname = "/" + d.name
			title = "selected database"
		else:
			dname = ""
		if h.name == h.host:
			hname = h.name
		else:
			hname = "%s(%s)" % (h.name, h.host)
		
		self.query_db_label.set_label("%s: %s@%s%s" % (
			title,
			h.user, hname,
			dname
		))
		self.auto_rename("%s%s" % (h.name, dname))
		
	def set_current_host(self, host):
		if self.current_host == host and host is not None and self.current_db == host.current_db:
			return
		self.current_host = host
		if host:
			self.current_db = host.current_db
		else:
			self.current_db = None
		self.update_db_label()

	def set_current_db(self, db):
		self.current_host = db.host
		self.current_db = db
		self.update_db_label()

	def update_bottom_label(self):
		self.query_bottom_label.set_label("encoding: %s" % self.encoding)
		
	def set_query_encoding(self, encoding):
		self.encoding = encoding
		self.update_bottom_label()
		
	def set_query_font(self, font_name):
		self.textview.get_pango_context()
		fd = pango.FontDescription(font_name)
		self.textview.modify_font(fd)

	def set_result_font(self, font_name):
		self.treeview.get_pango_context()
		fd = pango.FontDescription(font_name)
		self.treeview.modify_font(fd)

	def set_wrap_mode(self, wrap):
		self.textview.set_wrap_mode(wrap)
