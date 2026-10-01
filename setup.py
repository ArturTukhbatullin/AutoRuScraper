from setuptools import setup, find_packages

setup(
    name="autoruscraper",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "numpy==2.2.6",
        "pandas==2.3.3",
        "beautifulsoup4==4.15.0",
        "psycopg2==2.9.13",
        "selenium==4.50.0",
        "sqlalchemy==2.0.54",
        "tqdm==4.67.1",
        "loguru==0.7.3",
        "certifi==2026.7.22",
        "urllib3==2.8.0",
        "websocket==0.2.1",
        "dotenv==0.9.9",
        "pydantic==2.13.5"
    ]
)