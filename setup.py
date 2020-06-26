from setuptools import setup

version = '0.4.2'

setup(
    name='bitly_api',
    version=version,
    description="An API for bit.ly",
    long_description=open("./README.md", "r").read(),
    classifiers=[
      "Development Status :: 5 - Production/Stable",
      "Environment :: Console",
      "Intended Audience :: End Users/Desktop",
      "Natural Language :: English",
      "Operating System :: OS Independent",
      "Programming Language :: Python",
      "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
      "Topic :: Utilities",
      "License :: OSI Approved :: Apache Software License",
      ],
    keywords='bitly bit.ly',
    author='Allen Dolph',
    author_email='allen@kleinerperkins.com',
    install_requires=[
        'requests>=2.21.0',
        'requests-oauthlib>=1.2.0',
    ],
    url='https://github.com/KleinerPerkins/bitly-api-python',
    license='Apache Software License',
    packages=['bitly_api'],
    include_package_data=True,
    zip_safe=True,
)
