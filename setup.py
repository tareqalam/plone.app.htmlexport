from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='plone.app.htmlexport',
      version=version,
      description="Export content objects as html",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Mohammad Tareq Alam',
      author_email='tareq.mist@gmail.com',
      url='tareqalam.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'BeautifulSoup'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
