from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^index.html$', views.Index.as_view(), name='index'),
    url(r'^contacts.html$', views.Contacts.as_view(), name='contacts'),
    url(r'^(?P<name_board>[a-z]{1,4})/$', views.ThreadList.as_view(), name='board'),
    url(r'^(?P<name_board>[a-z]{1,4})/AddThread$', views.AddThread.as_view(), name='AddThread'),
    url(r'^(?P<name_board>[a-z]{1,4})/res/(?P<pk>[0-9]{1,}).html$', views.ThreadDetail.as_view(), name='thread'),
    url(r'^(?P<name_board>[a-z]{1,4})/res/(?P<pk>[0-9]{1,})/AddComment$', views.AddCommentView.as_view(), name='AddComment'),
    url(r'^AjaxTooltipComment.json$', views.AjaxTooltipComment.as_view(), name='AjaxTooltipComment'),
    url(r'^AjaxTooltipThread.json$', views.AjaxTooltipThread.as_view(), name='AjaxTooltipThread'),
    url(r'^AjaxTooltip.json$', views.AjaxTooltip.as_view(), name='AjaxTooltip'),
    url(r'^$', views.Index.as_view()),

]
