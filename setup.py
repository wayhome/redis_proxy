from setuptools import setup, find_packages
import os
classifiers = [
    'Programming Language :: Python',
    'Environment :: Console',
    'Topic :: System :: Networking',
    'Framework :: Twisted',
    'License :: OSI Approved :: BSD License',
]

version = '0.0.1'
README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(name='redis_proxy',
      version=version,
      description='a redis proxy that will seperate read and write',
      long_description=README,
      classifiers=classifiers,
      keywords='redis proxy',
      author='Young King',
      author_email='yanckin@gmail.com',
      url='https://github.com/youngking/redis_proxy',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['Nose'],
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'twisted'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      redis-proxy = redis_proxy.main:run
      """,
      )
