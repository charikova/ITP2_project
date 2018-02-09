from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include("UserCards.urls")),
    path('', include("Documents.urls")),
    path('requests/', include("BookRequests.urls")),
]
