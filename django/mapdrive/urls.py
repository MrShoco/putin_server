from django.conf.urls import url
from .views import index, upload, upload_delete, send


urlpatterns = [
    url(r'^$', index, name='index'),
    url( r'upload/', upload, name='jfu_upload' ),
    url( r'^delete/(?P<pk>\d+)$', upload_delete, name='jfu_delete' ),
    url(r'^send$', send, name='send'),
]
