from django.urls import path

from .views import FeedView, FollowView, LoginView, MeView, ProfileView, RegisterView, UnfollowView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("follow/<int:user_id>/", FollowView.as_view(), name="follow"),
    path("unfollow/<int:user_id>/", UnfollowView.as_view(), name="unfollow"),
    path("feed/", FeedView.as_view(), name="feed"),
]

