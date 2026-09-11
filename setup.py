"""Compatibility launcher only. Use npm ci for the supported implementation."""
from setuptools import setup
setup(name='dynamo-mcp',version='2.0.0a1',packages=['dynamo_mcp'],python_requires='>=3.11',install_requires=[],entry_points={'console_scripts':['dynamo-mcp=dynamo_mcp.main:main']})
