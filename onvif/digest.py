'''
From GitHubGist: sinchb/wsse.py
URL https://gist.github.com/sinchb/e026bb1c86517cb04de0#
'''
from base64 import b64encode
from hashlib import md5
try:
    from haslib import sha1
except:
    from sha import new as sha1

from suds.wsse import UsernameToken, Security, Token


class UsernameDigestToken(UsernameToken):

    def __init__(self, username=None, password=None):
        UsernameToken.__init__(self, username, password)
        self.setcreated()
        self.setnonce()

    def setnonce(self, text=None):
        if text is None:
            s = []
            s.append(self.username)
            s.append(self.password)
            s.append(Token.sysdate())
            m = md5()
            m.update(':'.join(s))
            self.raw_nonce = m.digest()
            self.nonce = b64encode(self.raw_nonce)
        else:
            self.nonce = text

    def xml(self):
        usernametoken = UsernameToken.xml(self)
        password = usernametoken.getChild('Password')
        nonce = usernametoken.getChild('Nonce')
        created = usernametoken.getChild('Created')
        password.set('Type', 'http://docs.oasis-open.org/wss/2004/01/'
                             'oasis-200401-wss-username-token-profile-1.0'
                             '#PasswordDigest')
        s = sha1()
        s.update(self.raw_nonce)
        s.update(created.getText())
        s.update(password.getText())
        password.setText(b64encode(s.digest()))
        nonce.set('EncodingType', 'http://docs.oasis-open.org/wss/2004'
            '/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary')
        return usernametoken
