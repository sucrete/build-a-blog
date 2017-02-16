
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    # def render(self):
    #     self._render_text = self.content.replace('\n', '<br>')
    #     renturn render_str('blogformpage.html', p=self)

class MainPage(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created desc limit 5")
        self.render("front.html", posts=posts)

class FormPage(Handler):
    def form_render(self, title="", body="", error=""):
        self.render("blogformpage.html", title=title, body=body, error=error)

    def get(self):
        self.form_render()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = BlogPost(title = title, body = body)
            a.put() #this will store the post in the database
            self.redirect('/blog/%s' % str(p.key().id()))

        else:
            error = "the Bros need both a title and a body before we post it, dudely"
            self.form_render(title, body, error)
class Permalink(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', FormPage),
    webapp2.Route('/blog/<id:\d+>', Permalink),
], debug=True)
