from django.conf.urls import url
from webmaster.server import ad

urlpatterns = [
    url(r'^haidong/', ad.site.urls),
]
