from django.contrib import admin
from django.urls import path, include
from Documents.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('documents/', include("Documents.urls")),
    path('register/', include("register.urls")),
    path('user/', include("UserCards.urls")),
    path('', include("Documents.urls"))
]
