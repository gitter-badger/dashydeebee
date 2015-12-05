from setuptools import setup

setup(
    name='dashydeebee',
    version='0.0.1',
    long_description=__doc__,
    packages=['dashydeebee'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask', 'python-dateutil']
)
