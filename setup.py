from distutils.core import setup

setup(
    name='lightspeed_api',
    version='0.0.1',
    packages=['lightspeed_api',],
    install_requires=['requests'],
    long_description="Lightweight interface for the Lightspeed Retail API.",
)