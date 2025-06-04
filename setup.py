from setuptools import setup, find_packages

setup(
    name="pythongrid",
    version="0.1.3.0",
    packages=find_packages(),
    install_requires=[
        "httpx",
        "orjson",
        "arrow",
        "pydantic",
        "tqdm",
    ],
    author="Allan Cao",
    author_email="allan@allancao.ca",
    description="Simple Python based client for the GRID esports API with a collection of data pipeline functions to support processing of game data.",
    python_requires=">=3.10",  # Union typing is extensively used.
)
