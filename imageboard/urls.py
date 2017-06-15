from django.conf.urls import url

from imageboard import views

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^contacts/$', views.Contacts.as_view(), name='contacts'),

    url(r'^(?P<name_board>[a-z]{1,4})/$', views.ThreadList.as_view(), name='board'),
    url(r'^(?P<name_board>[a-z]{1,4})/res/(?P<pk>[0-9]{1,})/$', views.ThreadDetail.as_view(), name='thread'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),

    url(r'^(?P<name_board>[a-z]{1,4})/AddThread$', views.AddThread.as_view(), name='AddThread'),
    url(r'^(?P<name_board>[a-z]{1,4})/res/(?P<pk>[0-9]{1,})/AddComment$', views.AddCommentView.as_view(),
        name='AddComment'),

    url(r'^AjaxTooltipComment/$', views.AjaxTooltipComment.as_view(), name='AjaxTooltipComment'),
    url(r'^AjaxTooltipThread/$', views.AjaxTooltipThread.as_view(), name='AjaxTooltipThread'),
    url(r'^AjaxTooltip/$', views.AjaxTooltip.as_view(), name='AjaxTooltip'),

]
