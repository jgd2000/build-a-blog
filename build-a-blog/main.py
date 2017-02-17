import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))


class Post(db.Model):
    subject = db.StringProperty(required = True)
#    posted = db.TextProperty(required = True)
    posted = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


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
        list_of_posts = db.GqlQuery("SELECT * FROM Post order by created desc limit 5")
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


        self.response.write("i'm in post module1")
        self.response.write(new_post)
        self.response.write("that was new_post")
        self.response.write(new_posted)
        self.response.write("that was new_posted")

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
        p = Post(subject = new_post_escaped , posted = new_posted_escaped)
        p.put()

        # get list of posts and display
#        list_of_posts = db.GqlQuery("SELECT * FROM Post order by created desc limit 5")
#        t = jinja_env.get_template("post.html")

    #    content = t.render(
    #                    posts = list_of_posts,
    #                    error = self.request.get("error"))
    #    self.response.write(content)




app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', Post)
], debug=True)
