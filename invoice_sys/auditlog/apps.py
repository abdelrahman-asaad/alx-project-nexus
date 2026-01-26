from django.apps import AppConfig

class AuditlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditlog'

    def ready(self):
        # ✅ هنا بنستدعي ملف signals
        import auditlog.signals
