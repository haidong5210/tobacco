from django.conf.urls import url
from webmaster.server import sites

urlpatterns = [
    url(r'^haidong/', sites.site.urls),
]
