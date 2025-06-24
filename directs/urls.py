from directs.views import Directs, SendDirect, UserSearch, NewConversation
from django.urls import path

urlpatterns = [
    path('', Directs, name="message"),
    path('direct/<username>', Directs, name="directs"),
    path('send/', SendDirect, name="send-directs"),
    path('search/', UserSearch, name="search-users"),
    path('new/<username>', NewConversation, name="conversation"),
]