from setuptools import setup, find_packages

setup(
    name="autoruscraper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy=2.4.0",
        "pandas=2.3.3",
        "beautifulsoup4=4.14.3",
        # "psycopg2=2.9.11",
        "selenium=4.39.0",
        "SQLAlchemy=2.0.45",
        "tqdm=4.67.1",
        "loguru=0.7.3"
    ]
)