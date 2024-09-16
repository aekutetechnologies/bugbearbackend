from django.apps import AppConfig
import os


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobs"

    def ready(self):
        # Avoid running the command when running tests or migrations
        if os.environ.get("RUN_MAIN", None) != "true":
            return

        from django.core.management import call_command

        call_command("load_jobs_to_redis")
