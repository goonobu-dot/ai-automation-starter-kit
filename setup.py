from setuptools import find_packages, setup


setup(
    name="ai-automation-starter-kit",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages("src"),
    entry_points={
        "console_scripts": [
            "ai-automation-kit=ai_automation_kit.cli:main",
        ],
    },
    python_requires=">=3.9",
)
