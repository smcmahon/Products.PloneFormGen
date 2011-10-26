from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "PloneFormGen", "version.txt")).read().strip()

setup(name='Products.PloneFormGen',
      version=version,
      description="A through-the-web form generator for Plone",
      long_description=open(os.path.join("Products", "PloneFormGen", "README.txt")).read() \
                       + "\n\n" + \
                       # CHANGES.txt has lots of UTF8, which PyPI won't accept
                       open(os.path.join("Products", "PloneFormGen", "CHANGES.txt")).read().decode('UTF8').encode('ASCII', 'replace'),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Zope2",
        "Framework :: Plone",
        ],
      keywords='Plone PloneFormGen',
      author='Steve McMahon',
      author_email='steve@dcn.org',
      url='http://plone.org/products/ploneformgen',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.Archetypes',
          'Plone',
          'Products.TALESField>=1.1.3',
          'Products.TemplateFields>=1.2.4',
          'Products.PythonField>=1.1.3',
          'plone.app.jquerytools>=1.2dev',
          'collective.js.jqueryui',
          # -*- Extra requirements: -*-
      ],
      extras_require={
        'test': ['collective.funkload'],
        },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
