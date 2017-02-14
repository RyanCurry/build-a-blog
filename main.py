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
import cgi
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape=True)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect("/blog") # don't get an error when you forget to go to /blog

    def write(self, *a, **kw):
        self.response.out.write(*a,**kw)


    def render_str(self, template , **kw):
        t = jinja_env.get_template(template)
        return t.render(kw)

    def render(self, template,**kw):
        self.write(self.render_str(template,**kw))


class blog_posts(db.Model):
    title=db.StringProperty(required = True)
    blog_body=db.TextProperty(required = True)
    created=db.DateTimeProperty(auto_now_add = True)


def get_posts(limit1, offset1):
    offset2=(offset1-1)*5 # no offset for page 1
    blogs=db.GqlQuery("SELECT * FROM blog_posts ORDER BY created DESC LIMIT {limit1} OFFSET {offset2}".format(limit1=limit1,offset2=offset2))
    return blogs


class MainPage(MainHandler):
    def render_front(self,title="",blog_body="",error="",created=""):
        page=self.request.get("page")
        if page:
            page=int(page)
        else:
            page=1

        blogs = get_posts(5,page)
        count=blogs.count()
        PrevPage=""
        Nextpage=""
        if count>(page * 5):
            Nextpage="Next"
        if page > 1:
            PrevPage="Previous"

        self.render("BlogPosts.html",title=title,blog_body=blog_body, blogs=blogs,date_created=created, PageNum=page, Prev=PrevPage,Nextp=Nextpage)


    def get(self):
        self.render_front()

class NewPost(MainHandler):
    def get(self):
        self.render("form.html")

    def post(self):
        title = self.request.get("title")
        blog_body = self.request.get("blog_body")
        if title and blog_body:
            a=blog_posts(title=title,blog_body=blog_body)
            a.put()

            self.redirect("/blog")
        else:
            error="Need a Title and body"
            self.render("form.html",title=title,blog_body=blog_body,error=error)


class ViewPostHandler(MainHandler):
    def get(self, id):
        blog_post_to_get=blog_posts.get_by_id(int(id))

        self.render("singlepost.html",post=blog_post_to_get)

app = webapp2.WSGIApplication([
    ("/",MainHandler ),
    ('/blog', MainPage),
    ("/newpost", NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
