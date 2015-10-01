from setuptools import setup, find_packages

version = '1.8.0'

setup(name='Products.PloneFormGen',
      version=version,
      description="A through-the-web form generator for Plone",
      long_description=(
          open("README.rst").read() +
          "\n\n" +
          open("CHANGES.txt").read()),
      classifiers=[
          "Development Status :: 6 - Mature",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
          "Framework :: Plone",
          "Framework :: Plone :: 5.0",
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Operating System :: OS Independent',
          'Programming Language :: JavaScript',
          'Programming Language :: Python',
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
          'Products.CMFPlone>=5.0b2.dev0',
          'Products.TALESField>=1.1.3',
          'Products.TemplateFields>=1.2.4',
          'Products.PythonField>=1.1.3',
      ],
      extras_require={
          'test': [
              'Products.PloneTestCase',
              # needed in Plone 5.0
              'plone.app.testing',
              'plone.testing',
          ],
          'loadtest': ['collective.funkload'],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
