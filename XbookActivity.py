# Copyright (C) 2007, Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
from gettext import gettext as _

import gtk
import evince
import hippo
import os

from sugar.activity import activity

from xbooktoolbar import XbookToolbar

class XbookActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self._document = None

        logging.debug('Starting xbook...')
        self.set_title(_('Read Activity'))
        
        evince.job_queue_init()
        self._view = evince.View()

        toolbox = activity.ActivityToolbox(self)

        self._toolbar = XbookToolbar(self._view)
#        self._toolbar.connect('open-document', self._open_document_cb)
        toolbox.add_toolbar(_('View'), self._toolbar)
        self._toolbar.show()

        self.set_toolbox(toolbox)
        toolbox.show()

        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled.props.shadow_type = gtk.SHADOW_NONE

        scrolled.add(self._view)
        self._view.show()
                
        self.set_canvas(scrolled)
        scrolled.show()

        if handle.uri:
            self._load_document(handle.uri)

    def _load_document(self, filename):
        if self._document:
            del self._document
        self._document = evince.factory_get_document(filename)
        self._view.set_document(self._document)
        self._toolbar.set_document(self._document)
        title = _("Read Activity")
        info = self._document.get_info()
        if info and info.title:
            title += ": " + info.title
        self.set_title(title)

    def _open_document_cb(self, widget):
        chooser = FileChooserDialog(_("Open a document to read"),
                                    parent=self,
                                    buttons=(gtk.STOCK_CANCEL,
                                             gtk.RESPONSE_REJECT,
                                             gtk.STOCK_OK,
                                             gtk.RESPONSE_ACCEPT))
        chooser.set_current_folder(os.path.expanduser("~"))
        chooser.set_show_hidden(False)

        file_filter = gtk.FileFilter()
        file_filter.set_name(_("All supported formats"))
        file_filter.add_mime_type("application/pdf")
        file_filter.add_mime_type("application/x-pdf")
        chooser.add_filter(file_filter)

        file_filter = gtk.FileFilter()
        file_filter.set_name(_("All files"))
        file_filter.add_pattern("*")
        chooser.add_filter(file_filter)
        
        resp = chooser.run()
        fname = chooser.get_filename()
        chooser.hide()
        chooser.destroy()
        if resp == gtk.RESPONSE_ACCEPT and fname:
            self._load_document('file://%s' % fname)
