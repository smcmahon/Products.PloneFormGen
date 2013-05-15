"""
gpg_encrypt
Provides a browser view with services from
ya_gpg.
"""

from Products.Five import BrowserView
from Products.PloneFormGen.content.ya_gpg import gpg


class GnuPGView(BrowserView):

    def encrypt(self, data, recipient_key_id):
        # Encrypt the message contained in the string 'data'

        return gpg.encrypt(data, recipient_key_id)
