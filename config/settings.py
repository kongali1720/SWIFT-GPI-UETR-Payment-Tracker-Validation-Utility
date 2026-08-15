import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv(
        "APP_NAME",
        "SWIFT GPI UETR Payment Tracker"
    )

    APP_VERSION = os.getenv(
        "APP_VERSION",
        "1.0.0"
    )

    APP_ENV = os.getenv(
        "APP_ENV",
        "development"
    )

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )

    API_HOST = os.getenv(
        "API_HOST",
        "127.0.0.1"
    )

    API_PORT = int(
        os.getenv(
            "API_PORT",
            "8080"
        )
    )


settings = Settings()
