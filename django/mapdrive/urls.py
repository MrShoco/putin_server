from django.conf.urls import url
from .views import index, upload, upload_delete, send, process_result


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'upload/', upload, name='jfu_upload' ),
    url(r'^delete/(?P<pk>\d+)$', upload_delete, name='jfu_delete' ),
    url(r'^send$', send, name='send'),
    url(r'^process_result/(?P<id>\d+)/$', process_result, name='process_result')
]
