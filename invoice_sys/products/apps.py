from django.apps import AppConfig

class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        """
        دي بتتفتح أوتوماتيك لما الـ app يشتغل.
        بنستورد signals هنا عشان تتسجل.
        """
        import products.signals
