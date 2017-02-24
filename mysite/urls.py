"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from posts import views as posts_view
from accounts import views as accounts_view

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    
    url(r'^comments/', include("comments.urls", namespace='comments')),
    url(r'^login/$', accounts_view.login_view, name='login'),
    url(r'^register/$', accounts_view.register_view, name='register'),
    url(r'^logout/$', accounts_view.logout_view, name='logout'),
    url(r'^', include("posts.urls"), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
