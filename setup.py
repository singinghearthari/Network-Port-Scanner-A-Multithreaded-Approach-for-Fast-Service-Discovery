from setuptools import setup, find_packages

setup(
    name="port_scanner",
    version="1.0.0",
    description="A multithreaded network port scanner with GUI and CLI",
    author="You",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "port_scanner=main:main",
        ]
    },
    python_requires=">=3.6",
)
