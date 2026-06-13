"""
Setup configuration for AI Knowledge Support System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-knowledge-support-system",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered document Q&A system using Pinecone and Hugging Face",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ambalalsonawane26/ai-knowledge-support-system",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-qa=app.main:main",
        ],
    },
    include_package_data=True,
)
