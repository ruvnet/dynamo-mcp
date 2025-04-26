"""
Setup script for the dynamo-mcp package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dynamo-mcp",
    version="0.1.0",
    author="Dynamo MCP Team",
    author_email="info@example.com",
    description="A dynamic MCP registry for cookiecutter templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/dynamo-mcp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cookiecutter>=2.1.1",
        "fastapi>=0.95.0",
        "fastmcp>=0.1.0",
        "pydantic>=1.10.7",
        "uvicorn>=0.21.1",
        "sse-starlette>=1.6.1",
    ],
    entry_points={
        "console_scripts": [
            "dynamo-mcp=dynamo_mcp.main:main",
        ],
    },
)