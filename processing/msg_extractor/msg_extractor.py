# coding: utf-8
import os

try:
    # Use https://github.com/mattgwwalker/msg-extractor to read .msg files
    import extract_msg
    HAVE_EXTRACT_MSG = True
except ImportError:
    HAVE_EXTRACT_MSG = False

from fame.common.utils import tempdir
from fame.core.module import ProcessingModule, ModuleInitializationError


class MSG(ProcessingModule):
    name = "msg"
    description = "Extract attachments and headers from .msg files"
    acts_on = "msg"
    generates = "email_headers"

    def initialize(self):
        if not HAVE_EXTRACT_MSG:
            raise ModuleInitializationError(self, "Missing dependency: extract_msg")

    def extract_header(self, mail):
        return mail.header.as_string()

    def extract_attachments(self, mail, outdir):
        attachments = mail.attachments
        paths = []

        for attachment in attachments:
            paths.append(attachment.save(customPath=outdir))

        return paths

    def register_header(self, header, outdir):
        fpath = os.path.join(outdir, '__header')

        with open(fpath, 'w') as f:
            f.write(header)

        self.register_files('email_headers', fpath)

    def add_attachments(self, paths):
        for path in paths:
            self.add_extracted_file(path)

    def each(self, target):
        mail = extract_msg.Message(target)

        if mail:
            outdir = tempdir()

            # extract header
            header_string = self.extract_header(mail)
            if header_string:
                self.register_header(header_string, outdir)
            else:
                self.log('error', 'could not extract email headers')

            # extract attachments
            attachments_path = self.extract_attachments(mail, outdir)
            if attachments_path:
                self.add_attachments(attachments_path)
            else:
                self.log('debug', 'no attachment found')
        else:
            self.log('error', 'extract_msg could not parse message')
