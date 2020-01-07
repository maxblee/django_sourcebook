"""django_sourcebook URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import sourcebook.views

urlpatterns = [
    path("", sourcebook.views.site_index, name="site_index"),
    path("admin/", admin.site.urls),
    path("sourcebook/", include("sourcebook.urls.sourcebook")),
    path("foia/", include("sourcebook.urls.foia")),
    path("projects/", include("sourcebook.urls.projects")),
]

# debug toolbar settings
from django.conf import settings
from django.conf.urls import include, url

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [url(r"^__debug__/", include(debug_toolbar.urls))]
