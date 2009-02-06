import logging

from pastgit.lib.base import *
from pastgit.lib.pasterdao import *
from pylons.decorators import rest

from itertools import count
from formencode import variabledecode
from pastgit.lib.relativetime import *

log = logging.getLogger(__name__)

class DashboardController(BaseController):

    languages = dict(txt = "Plain Text",
                     java = "Java",
                     js = "JavaScript",
                     css = "CSS",
                     xml = "XML")

    def __init__(self):
        self.paster = PasterDao()

    @rest.dispatch_on(POST='_postPaste')
    def index(self):
        c.fileId = 1
        self._prepareLanguages()
        return render("newpaste")

    def pasteBox(self, id = None):
        if id == None:
            c.fileId = 1
        else:
            c.fileId = id
        return render("pasteBox")

    def _postPaste(self):
        post = variabledecode.variable_decode(request.POST)
        log.info("post: " + str(post))

        if not post.get("fileContent"):
            return "empty"

        initial = zip(count(), post.get("fileName"), post.get("fileContent"))
        log.info(initial)

        paste = self.paster.create(initial)
        c.pasteId = paste.id

        return render("pasted")

    def show(self, id, rev=None):
        c.pasteId = id

        paste = self.paster.get(id)
        c.blobs = paste.show(rev)

        history = paste.history()
        
        c.currentRev = history[0].id
        if rev:
            c.currentRev = rev

        c.history = [(x.id[0:5], x.id, relative_time(x.committed_date), c.currentRev == x.id and "current" or "other") for x in history]

        c.editable =  c.currentRev == history[0].id

        return render("showPaste")

    @rest.dispatch_on(POST='_savePaste')
    def edit(self, id):
        c.pasteId = id
        self._prepareLanguages()

        paste = self.paster.get(id)
        c.blobs = paste.show()
        return render("editPaste")

    def _savePaste(self, id):
        post = variabledecode.variable_decode(request.POST)

        content = zip(count(), post.get("fileName"), post.get("fileContent"))

        paste = self.paster.get(id)
        paste.modify(content)

        redirect_to(controller="/dashboard", id=id, action="show", rev=None)

    def _prepareLanguages(self):
        c.languages = [(x[0], x[1], x[0] == "txt" and "selected" or "") for x in self.languages.iteritems()]
