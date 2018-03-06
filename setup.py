from setuptools import setup, find_packages

version = '1.7.24'

setup(name='Products.PloneFormGen',
      version=version,
      description="A through-the-web form generator for Plone",
      long_description=(
          open("README.rst").read()
          + "\n\n" +
          # CHANGES.txt has lots of UTF8, which PyPI won't accept
          open("CHANGES.txt").read().decode('UTF8').encode('ASCII', 'replace')),
      classifiers=[
          "Development Status :: 6 - Mature",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
          "Framework :: Plone",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Operating System :: OS Independent',
          'Programming Language :: JavaScript',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
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
          'Products.Archetypes>=1.7.14',  # placeholder support
          'Products.CMFPlone>=4.1',
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
