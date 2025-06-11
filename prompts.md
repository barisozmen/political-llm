# 1
Terminal commands:
- django-admin startproject core
- python3 manage.py startapp app
- python3 manage.py runserver

### Afterwards
- some dir hierarchy changes

# 2
Improve this django project with the followings:

Integrate a user system 
A google social login system for users
A django mail backend
A magiclink email login system for user


Use only SQLite database for everything.

### Afterwards
- do necessary pip installs
- clean extra columns in the user database
  - Uses this prompt for this:
```
  Before making the migrations, change some user fields both from the database and the user profile form and any other place that it can be relavant:

Here are the changes:
- remove these fields: phone number, birth date, location
- add these fields: twitter handle, discord handle, ETH address, Bitcoin address
```

Another fix prompt I used:
```
Getting this error on the browser:
```
NoReverseMatch at /
Reverse for 'socialaccount_provider_login' not found. 'socialaccount_provider_login' is not a valid view function or pattern name.
Request Method:	GET
Request URL:	http://127.0.0.1:8000/
Django Version:	5.1.2
Exception Type:	NoReverseMatch
Exception Value:	
Reverse for 'socialaccount_provider_login' not found. 'socialaccount_provider_login' is not a valid view function or pattern name.
Exception Location:	/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/django/urls/resolvers.py, line 831, in _reverse_with_prefix
Raised during:	app.views.HomeView
Python Executable:	/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
Python Version:	3.11.5
Python Path:	
['/Users/barisozmen/development/github/barisozmen/django-stripe-google-signin-template',
 '/Library/Frameworks/Python.framework/Versions/3.11/lib/python311.zip',
 '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11',
 '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/lib-dynload',
 '/Users/barisozmen/Library/Python/3.11/lib/python/site-packages',
 '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages',
 '__editable__.tinygrad-0.8.0.finder.__path_hook__',
 '/Users/barisozmen/development/github/huggingface/lerobot',
 '/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/rerun_sdk']
Server time:	Thu, 29 May 2025 09:26:27 +0000
Error during template rendering
In template /Users/barisozmen/development/github/barisozmen/django-stripe-google-signin-template/templates/app/home.html, error at line 90

Reverse for 'socialaccount_provider_login' not found. 'socialaccount_provider_login' is not a valid view function or pattern name.
80	                        </div>
81	                    </div>
82	
83	                    <!-- Google OAuth -->
84	                    <div class="col-md-4">
85	                        <div class="card h-100 text-center">
86	                            <div class="card-body">
87	                                <i class="fab fa-google fa-3x text-danger mb-3"></i>
88	                                <h5 class="card-title">Google Sign-In</h5>
89	                                <p class="card-text">Quick and secure login using your Google account.</p>
90	                                <a href="{% url 'socialaccount_provider_login' 'google' %}" class="btn btn-google">
91	                                    <i class="fab fa-google me-2"></i>Sign in with Google
92	                                </a>
93	                            </div>
94	                        </div>
95	                    </div>
96	
97	                    <!-- Magic Link -->
98	                    <div class="col-md-4">
99	                        <div class="card h-100 text-center">
100	                            <div class="card-body">
```
```

And many more other error messages!



#3
In the login page at /accounts/login/, it asks for email and password. It shouldn't ask for it! Instead, it should give only two options to the user:

1) Continue with Google
2) Email address

In the second option, it should send a signin email to the user with a link for sign in. No password required!

Make necessary changes both in the frontend and the backedn



# 4
When the user try signin with email (magiclink), it should check if the mail is registered, if not, it should send a sign-up link to the user. There shouldn't be a separate register form or logic. It should give proper messages to the user for that

Update frontend and backend accordingly for this.


# 5
$ python3 manage.py setup_oauth


# 6
Somehow, I don't get authentication link when I provided my email address. Find out why? I'm setting this for privateemail. Tell me what environment variables I should set for it

### Afterwards
The reason was my email password was misspelled.

# 7
After I send a magiclink for signup to myself, I'm getting this error on the browser after clicking to the received link with the token.

"This signup link has expired or is invalid. Please request a new one."

It seems like there are problems in the token logic. Find out what is wrong and correct them


# 8
Remove the full name property from the users. We shouldn't ask or now first or last name of the user. Remove that logic from the frontend and backend as well

# 9
I see there is a change password section on the user profile page. There shouldn't be such a thing because we don't use any password logic. Remove it both from frontend and backend as that's necessary.

We have only two ways to login:
1) google social signin
2) paswordless magic link


# 10
remove all the backend and frontend logic pertaining to the email verification. Email is always verified, because either if the user login through google social or magiclink, we have been automatically validated the email. We don't need any separate email verficiation logic


# 11
Make this django project production ready by making it served through daphne on production.

On production, I'll serve it with pm2, linux process manager 2. It will use Daphne as well to server


# 12
for all usages of the name "django-stripe-google-signin-template", add a variable to hold

# 13
I want to keep my nginx conf inside of the project folder and then link to sites-enabled of nginx. how can i do that?

# 14
I started hosting this app on @https://djangotemplate.bozmen.xyz/ . When I enter into /accounts/login/, I'm getting CSRF verification error as below on the browser

```
Forbidden (403)
CSRF verification failed. Request aborted.

Help
Reason given for failure:

    Origin checking failed - https://djangotemplate.bozmen.xyz does not match any trusted origins.
    
In general, this can occur when there is a genuine Cross Site Request Forgery, or when Django’s CSRF mechanism has not been used correctly. For POST forms, you need to ensure:

Your browser is accepting cookies.
The view function passes a request to the template’s render method.
In the template, there is a {% csrf_token %} template tag inside each POST form that targets an internal URL.
If you are not using CsrfViewMiddleware, then you must use csrf_protect on any views that use the csrf_token template tag, as well as those that accept the POST data.
The form has a valid CSRF token. After logging in in another browser tab or hitting the back button after a login, you may need to reload the page with the form, because the token is rotated after a login.
You’re seeing the help section of this page because you have DEBUG = True in your Django settings file. Change that to False, and only the initial error message will be displayed.

You can customize this page using the CSRF_FAILURE_VIEW setting.
```

# 15
https://github.com/barisozmen/django-stripe-google-signin-template/commit/45283258f20c5730c1b87ebbd88e60cdc059e605

# 16
The current code runs daphne with @run_daphne.py . Check if it is correct and if the correct settings for a daphne application already done in this django project


# 17
remove magiclink button from the homepage. We will still use magiclink, but we don't need another website page for that. Just remove the magiclink button as it's unneccessary. 


# 18
Change the logic for signin with google. When user clicks 'continue with google', it should be directly send to relevant google link. There is no need an intermediary page at accounts/google/login/. Remove it, and directly send people to google instead


# 19
how can I enable google social auth from the google cloud console? There will be also a callback from google, do we have that page?


# 20
>> I did many things to make google auth work.


# 21
For this django project, integrate Logfire so that I can do structured loggins. See @https://github.com/pydantic/logfire 

Also, add some light loggins in important places


# 22

# 23


# Stripe
For this django project, set up Stripe subscription. Make a stripe subscription and billing page showing the current subscription tier of the user and dashboard of subscription options.

Subscription options:
- 10$ per month -> 1000 credits per month
- 20$ per month -> 3000 credits per month (best value)
- 30$ per month -> 5000 credits per month

Implement all necessary stripe logic. When users subscribes, their tier should be noted in the user database. And also user database should keep track of their spent credits for each their monthly subscription cycles.

Think deeply about how this can be designed and what else can be needed. First do a design session for planning, then start implementing


# Stripe
In the current user subscription dashboard, there is no link for subscribe. Add buttons for stripe subscriptions and also show all the stripe tiers of subscriptions. 

Remember the tiers again:
- 10$ per month -> 1000 credits per month
- 20$ per month -> 3000 credits per month (best value)
- 30$ per month -> 5000 credits per month

### Afterwards
Many other prompts to fix small issues. Finally it's at the commit: e4515726b0b4c5ec3b65975b789609b5c1bc3683


# 
Add a footer to the home page and other relevant frontend pages. In this footer, there should be links to terms, privacy, and about pages. Also create those terms, privacy, and about pages

#
Learn about SEO tags and strategies from @Web and apply them to the frontend webpages in this project

#

#

#

#
