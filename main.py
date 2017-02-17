import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))


class PostBlog(db.Model):
    subject = db.StringProperty(required = True)
    posted = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

#class PostBlog(db.Model):
#    subject = db.StringProperty
#    posted = db.TextProperty
#    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


class Index(Handler):
    """ Handles requests coming in to '/' (the root of our site)
        e.g. localhost:12080/
        will print all posts
    """

    def get(self):
        list_of_posts = db.GqlQuery("SELECT * FROM PostBlog order by created desc limit 5")
        x = jinja_env.get_template("post.html")
        content = x.render(
                        posts = list_of_posts,
                        error = self.request.get("error"))
        self.response.write(content)



class Post(Handler):
    """ Handles requests coming in to '/blog'
        e.g. localhost:12080/blog
    """
    def post(self):
        new_post = self.request.get("new-post")
        new_posted = self.request.get("posted")

        # if the user typed nothing at all, redirect and yell at them
        if (not new_post) or (new_post.strip() == ""):
            error = "Please specify a subject for post you want to add."
            self.redirect("/?error=" + cgi.escape(error))

        if (not new_posted) or (new_posted.strip() == ""):
            error = "Please enter a post you want to add."
            self.redirect("/?error=" + cgi.escape(error))

        # 'escape' the user's input so that if they typed HTML, it doesn't mess up our site
        new_post_escaped = cgi.escape(new_post, quote=True)
        new_posted_escaped = cgi.escape(new_posted, quote=True)

        # construct a post object for the new post
        p = PostBlog(subject = new_post_escaped , posted = new_posted_escaped)
        p.put()


        self.redirect("/blog/%s" % p.key().id())
        # get list of posts and display
        list_of_posts = db.GqlQuery("SELECT * FROM PostBlog order by created desc limit 5")
        t = jinja_env.get_template("post.html")

        content = t.render(
                        posts = list_of_posts,
                        error = self.request.get("error"))
        self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):
    """ Handles requests coming in to '/blog/id number'
        e.g. localhost:12080/blog/#####
    """
    def get(self,id):
    #    pass

        post = PostBlog.get_by_id(int(id))
        subject = post.subject
        posted = post.posted


        t = jinja_env.get_template("permalink.html")
        content=t.render(posted=posted,subject=subject,id=id)

        self.response.write(content)

def get_posts(limit, offset):
    # TODO: query the database for posts, and return them

    list_of_posts = db.GqlQuery("SELECT * FROM PostBlog order by created desc limit {0} offset{1}".format (limit,offset))
    t = jinja_env.get_template("post.html")

    content = t.render(
                    posts = list_of_posts,
                    error = self.request.get("error"))
    self.response.write(content)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', Post),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
