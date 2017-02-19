
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    # def render(self):
    #     self._render_text = self.content.replace('\n', '<br>')
    #     return render_str('blogformpage.html', p=self)



class MainPage(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created desc limit 5")
        self.render("front.html", posts=posts)

class FormPage(Handler):
    def get(self):
        self.render("blogformpage.html")

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            q = BlogPost(title = title, post = post)
            q.put() #this will store the post in the database
            q_id = q.key().id()
            self.redirect('/blog/%s' % q_id)#does the q object contain an id?

        else:
            error = "the Bros need a title AND a body before we can post it, dudely"
            self.render("blogformpage.html", title=title, body=body, error=error)

class Permalink(Handler):
    def get(self, id):
        key = db.Key.from_path('BlogPost', int(id))#this need a blog key? (i.e. ",parent=blog_key()"). try it without first
        #the .from_path method pulls from the url
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)
        #post.title and post.post in 'permalink.html' should be filled by the post object which was got with the 'db.get(key)' method directly above

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', FormPage),
    webapp2.Route('/blog/<id:\d+>', Permalink),
], debug=True)
