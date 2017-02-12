#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

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

class MainPage(Handler):
    def front_render(self, title="", body="", error=""):
        self.render("front.html", title=title, body=body, error=error)
        all_posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created desc")

    def get(self):
        self.front_render()

    def post(self):





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
            self.redirect("/")

        else:
            error = "the Bros need both a title and a body before we post it, dudely"
            self.form_render(title, body, error)

app = webapp2.WSGIApplication([
    ('/blog', MainPage)
    ('/newpost', FormPage)
], debug=True)
