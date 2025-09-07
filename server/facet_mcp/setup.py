#!/usr/bin/env python3
"""
Setup script for FACET MCP Server

This allows the MCP server to be installed and run independently
of the main FACET package.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="facet-mcp-server",
    version="0.1.0",
    description="FACET MCP Server - Agent-First AI Tooling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Emil Rokossovskiy",
    author_email="ecsiar@gmail.com",
    url="https://github.com/rokoss21/FACET",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=[
        "websockets>=12.0",
        "jsonschema>=4.0",
        "uvloop>=0.17.0; sys_platform != 'win32'",
        # FACET core dependencies
        "numba>=0.56.0",
        "numpy>=1.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio",
            "black",
            "isort",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    entry_points={
        "console_scripts": [
            "facet-mcp=facet_mcp.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
