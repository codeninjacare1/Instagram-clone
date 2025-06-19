# from django.apps import AppConfig


# class PostConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'post'


from django.apps import AppConfig

class PostConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'post'

    def ready(self):
        import post.custom_filters  # <-- Add this line