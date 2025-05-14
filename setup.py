from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="health_insurance_au",
    version="0.1.0",
    author="Mehdi Modarressi",
    author_email="your.email@example.com",
    description="Australian Health Insurance Simulation System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/health_insurance_sql_server",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyodbc",
        "python-dotenv",
        "pandas",
        "pytest",
        "pytest-cov",
    ],
    entry_points={
        "console_scripts": [
            "hi-init-db=health_insurance_au.cli.initialize_db:main",
            "hi-add-data=health_insurance_au.cli.add_initial_data:main",
            "hi-enable-cdc=health_insurance_au.cli.enable_cdc:main",
            "hi-monitor-cdc=health_insurance_au.cli.monitor_cdc:main",
            "hi-simulation=health_insurance_au.cli.simulation:main",
        ],
    },
)