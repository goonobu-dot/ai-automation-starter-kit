from pathlib import Path

from setuptools import find_packages, setup


README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")


setup(
    name="ai-automation-starter-kit",
    version="0.1.0",
    description="Starter kit for reusable AI automation workflows.",
    long_description=README,
    long_description_content_type="text/markdown",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages("src"),
    entry_points={
        "console_scripts": [
            "ai-automation-kit=ai_automation_kit.cli:main",
        ],
    },
    python_requires=">=3.9",
)
