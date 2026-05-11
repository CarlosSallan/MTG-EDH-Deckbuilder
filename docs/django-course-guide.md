# Django Course Guide — Web Project (UdL)

Step-by-step guide to build a web app with Django.

---

## Key conventions

| Part | File | Role |
|------|------|------|
| View | views.py | Handles a request and returns a response |
| Model | models.py | Defines a database table as a Python class |
| Template | *.html | HTML sent to the browser, with Django template language |
| URL config | urls.py | Maps URL paths to views |
| Admin | admin.py | Register models for the built-in admin panel |

Flow: **URL → View → (Model) → Template → Response**

---

## Step 1 — Project structure

```
DjangoProject/
├── DjangoProject/       # Project config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── blog/                # App
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
├── templates/
├── manage.py
└── pyproject.toml
```

Run server: `python manage.py runserver` (PyCharm) or `uv run python manage.py runserver` (external terminal).

---

## Step 2 — View + URL + Template

### views.py
```python
from django.shortcuts import render

def home(request):
    return render(request, 'blog/home.html')
```

### blog/urls.py (create this file)
```python
from django.urls import path
from . import views

app_name = 'blog'  # namespace → {% url 'blog:home' %} in templates

urlpatterns = [
    path('', views.home, name='home'),
]
```

### DjangoProject/urls.py
```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]
```

### templates/blog/home.html
```html
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>My Blog</title></head>
<body>
  <h1>Welcome</h1>
</body>
</html>
```

---

## Step 3 — Base template

### templates/base.html
```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{% block title %}My Blog{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'blog/style.css' %}">
</head>
<body>
  <nav>
    <a href="{% url 'blog:home' %}">Home</a>
  </nav>
  <div class="container">
    {% block content %}{% endblock %}
  </div>
  <footer><p>Django Blog - 2026</p></footer>
</body>
</html>
```

### Child template pattern
```html
{% extends "base.html" %}
{% block title %}Page Title{% endblock %}
{% block content %}
  <h1>Page content here</h1>
{% endblock %}
```

Static files go in `blog/static/blog/style.css`. Django finds them via `{% static 'blog/style.css' %}`.

---

## Step 4 — Model + migrations + admin

### models.py
```python
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})
```

After any model change:
```bash
python manage.py makemigrations
python manage.py migrate
```

### admin.py
```python
from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('title', 'body')
```

Create superuser: `python manage.py createsuperuser`

---

## Step 5 — List and Detail views (class-based)

```python
from django.views.generic import ListView, DetailView
from .models import Post

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
```

### blog/urls.py
```python
urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.PostListView.as_view(), name='post_list'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
]
```

`<int:pk>` captures the post ID from the URL and passes it to the view.

### Template — list
```html
{% for post in posts %}
  <article>
    <h2><a href="{{ post.get_absolute_url }}">{{ post.title }}</a></h2>
    <p>{{ post.created_at|date:"F j, Y" }}</p>
    <p>{{ post.body|truncatewords:30 }}</p>
  </article>
{% empty %}
  <p>No posts yet.</p>
{% endfor %}
```

---

## Step 6 — Login / Logout

### DjangoProject/urls.py
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('blog.urls')),
]
```

### settings.py (add at bottom)
```python
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

Django provides these views automatically: `/accounts/login/`, `/accounts/logout/`, `/accounts/password_change/`, `/accounts/password_reset/`.

You must provide `templates/registration/login.html`. Django passes a `form` variable with `form.username` and `form.password`.

**Logout must use a POST form** (not a link) because it changes server state:
```html
<form method="post" action="{% url 'logout' %}" class="inline-form">
  {% csrf_token %}
  <button type="submit">Logout</button>
</form>
```

**{% csrf_token %}** is required on every POST form — Django rejects forms without it (403 error).

In templates, `user.is_authenticated` and `user.username` are available in all templates automatically.

---

## Step 7 — Signup

```python
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')
```

Add to main urls.py **before** `accounts/`:
```python
path('accounts/signup/', SignUpView.as_view(), name='signup'),
path('accounts/', include('django.contrib.auth.urls')),
```

Order matters: Django checks URLs top to bottom, first match wins.

---

## Step 8 — Create view (login required)

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'body']
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
```

`LoginRequiredMixin` must be listed **first** in the parent classes.
`form.instance` is the object about to be saved — set fields on it before calling `super()`.
`super().form_valid(form)` saves the object and redirects to `get_absolute_url()`.

**URL order rule**: specific paths before parameterised ones:
```python
path('posts/new/', views.PostCreateView.as_view(), name='post_create'),  # BEFORE
path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
```
