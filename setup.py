# -*- coding: utf-8 -*-
import ast
import re
from pathlib import Path

from setuptools import find_packages, setup

# Fixed, repository-relative build inputs; no user-supplied paths are accepted.
PACKAGE_ROOT = Path(__file__).resolve().parent
_version_re = re.compile(r"__version__\\s+=\\s+(.*)")
version_source = (PACKAGE_ROOT / "propms" / "__init__.py").read_text(encoding="utf-8")
version = str(ast.literal_eval(_version_re.search(version_source).group(1)))
install_requires = (PACKAGE_ROOT / "requirements.txt").read_text(encoding="utf-8").strip().split("\n")

setup(
    name="propms",
    version=version,
    description="Property Management Solution",
    author="Aakvatech",
    author_email="info@aakvatech.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
