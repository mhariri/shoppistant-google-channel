import json
import urllib
import urllib2
import datetime

import webapp2
from google.appengine.api import urlfetch


PLUGIN_INFO = {
    "name": "Google product search"
}

# cache for 2 days
EXPIRATION_IN_SECONDS = 2 * 24 * 60 * 60

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
        response = urlfetch.fetch(
            "http://nameresolver-shoppistant.rhcloud.com/products/%s" % urllib.quote_plus(ean_code),
            None, headers={'Referrer': 'http://shoppistant.com'}, deadline=45)

        if response.status_code != 200:
            raise urllib2.HTTPError(response.final_url, response.status_code,
                                    response.content, response.headers, None)

        results = json.loads(response.content)
        return results["name"]


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
