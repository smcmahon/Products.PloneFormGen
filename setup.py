from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "PloneFormGen", "version.txt")).read().strip()

setup(name='Products.PloneFormGen',
      version=version,
      description="",
      long_description=open(os.path.join("Products", "PloneFormGen", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "PloneFormGen", "CHANGES.txt")).read() + "\n" +,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.TALESField',
          'Products.TemplateFields',
          'Products.PythonField',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
