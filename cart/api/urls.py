from django.urls import path, include

urlpatterns = [
    path('v1/', include('cart.api.v1.urls'), name="API_VERSION"),
]
