from setuptools import setup, find_packages


version = '1.7.27'

with open("README.rst") as myfile:
    readme = myfile.read()
with open("CHANGES.txt") as myfile:
    changes = myfile.read()
# CHANGES.txt has lots of UTF8, which PyPI won't accept.
# So we used to call this on it:
# .decode('UTF8').encode('ASCII', 'replace')
# This worked until 1.7.25.
# But now 'read' returns str instead of unicode, so it has no 'decode' method.
# I tested an upload to test.pypi.org without this decode/encode, and it worked fine.
# Apparently PyPI accepts it meanwhile.

long_description=(readme + "\n\n" + changes)

setup(name='Products.PloneFormGen',
      version=version,
      description="A through-the-web form generator for Plone",
      long_description=long_description,
      classifiers=[
          "Development Status :: 6 - Mature",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Operating System :: OS Independent',
          'Programming Language :: JavaScript',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
      ],
      keywords='Plone PloneFormGen',
      author='Steve McMahon',
      author_email='steve@dcn.org',
      url='https://github.com/smcmahon/Products.PloneFormGen',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.Archetypes>=1.7.14',  # placeholder support
          'Products.CMFPlone>=4.1',
          'Products.GenericSetup>=1.8.2',
          'Products.TALESField>=1.1.3',
          'Products.TemplateFields>=1.2.4',
          'Products.PythonField>=1.1.3',
          'plone.app.jquerytools>=1.2dev',
          'collective.js.jqueryui',
      ],
      extras_require={
          'test': [
              'Products.PloneTestCase',
              'plone.protect>=2.0.2',
          ],
          'loadtest': ['collective.funkload'],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
