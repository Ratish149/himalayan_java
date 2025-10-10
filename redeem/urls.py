from django.urls import path

from . import views

urlpatterns = [
    # Redeem points (create redemption order)
    path("redeem-offers/", views.RedeemPointsView.as_view(), name="redeem_points"),
    path(
        "redeem-offers/<int:pk>",
        views.RedeemPointsRetrieveUpdateDestroyView.as_view(),
        name="redeem_points",
    ),
    path("user-redeem/", views.UserRedeemView.as_view(), name="user_redeem"),
    path(
        "next-offer/",
        views.UserRedeemNextOfferView.as_view(),
        name="user_redeem_next_offer",
    ),
]
