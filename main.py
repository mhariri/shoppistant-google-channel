import json
import urllib
import urllib2
import datetime

import webapp2


PLUGIN_INFO = {
    "name": "Google product search"
}

# cache for 2 days
EXPIRATION_IN_SECONDS = 2 * 24 * 60 * 60

# increase appengine's deadline
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(45)

class GMT(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=10)

    def tzname(self, dt):
        return "GMT"

    def dst(self, dt):
        return datetime.timedelta(0)


def get_expiration_stamp(seconds):
    gmt = GMT()
    delta = datetime.timedelta(seconds=seconds)
    expiration = datetime.datetime.now()
    expiration = expiration.replace(tzinfo=gmt)
    expiration = expiration + delta
    return expiration.strftime("%a, %d %b %Y %H:%M:%S %Z")


class MainHandler(webapp2.RequestHandler):
    def get(self):
        barcode = self.request.params.get("q", None)
        if barcode:
            try:
                name = self.resolve_name(barcode)
                open_details = self.request.params.get("d", None)
                if open_details:
                    self.redirect(str("http://www.google.se/search?q=%s" % urllib.quote_plus(name.encode("utf8"))))
                else:
                    self.set_default_headers()
                    self.response.content_type = "image/png"
                    self.response.body_file = open("icon.png")
            except urllib2.HTTPError, e:
                self.response.write("Not found")
                self.response.status = 404
        else:
            self.response.content_type = "application/json"
            self.response.write(json.dumps(PLUGIN_INFO))

    def set_default_headers(self):
        # allow CORS
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers["Expires"] = get_expiration_stamp(EXPIRATION_IN_SECONDS)
        self.response.headers["Cache-Control"] = "public, max-age=%d" % EXPIRATION_IN_SECONDS

    def resolve_name(self, ean_code):
        request = urllib2.Request(
            "http://nameresolver-shoppistant.rhcloud.com/products/%s" % urllib.quote_plus(ean_code),
            None, {'Referrer': 'http://shoppistant.com'})
        response = urllib2.urlopen(request)

        results = json.load(response)
        return results["name"];


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
