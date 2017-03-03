from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^index.html$', views.Index.as_view(), name='index'),
    url(r'^contacts.html$', views.Contacts.as_view(), name='contacts')
]
