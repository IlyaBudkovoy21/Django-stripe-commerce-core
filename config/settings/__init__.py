import os


DJANGO_ENV = os.getenv("DJANGO_ENV", "development").lower()

if DJANGO_ENV in {"production", "prod"}:
    from .prod import *  # noqa: F403
else:
    from .dev import *  # noqa: F403
