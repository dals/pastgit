import logging

from pastgit.lib.base import *
from pastgit.lib.pasterdao import *
from pylons.decorators import rest

from itertools import count
from formencode import variabledecode

log = logging.getLogger(__name__)

class DashboardController(BaseController):

    def __init__(self):
        self.paster = PasterDao()

    @rest.dispatch_on(POST='_postPaste')
    def index(self):
        c.fileId = 1
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

    def show(self, id):
        c.pasteId = id
        paste = self.paster.get(id)
        c.blobs = paste.show()
        return render("showPaste")

    @rest.dispatch_on(POST='_savePaste')
    def edit(self, id):
        c.pasteId = id
        paste = self.paster.get(id)
        c.blobs = paste.show()
        return render("editPaste")

    def _savePaste(self, id):
        post = variabledecode.variable_decode(request.POST)

        content = zip(post.get("fileName"), post.get("fileContent"))

        paste = self.paster.get(id)
        paste.modify(content)

        redirect_to(action="show")
