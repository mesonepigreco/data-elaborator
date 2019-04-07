from distutils.core import setup

setup(
    # Application name:
    name="data-elaborator",

    # Version number (initial):
    version="0.2.0",

    # Application author details:
    author="Lorenzo Monacelli",
    #author_email="name@addr.ess",

    # Packages
    packages=["app_data_elaborator"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    #url="http://pypi.python.org/pypi/MyApplication_v010/",

    #
    # license="LICENSE.txt",
    description="A tool for scientific data analysis",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "wxPython", "numpy", "matplotlib"
    ],

    scripts = ["bin/data-elaborator"]
)
