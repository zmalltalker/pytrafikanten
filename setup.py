from distutils.core import setup

import trafikanten
author, email = trafikanten.__author__[:-1].split(' <')

setup(name='trafikanten',
      version=trafikanten.__version__,
      description="Interface for realtime data from Norwegian public transportation",
      long_description=trafikanten.__doc__,
      author=author,
      author_email=email,
      url=trafikanten.__url__,
      packages=['trafikanten'],
      license=trafikanten.__license__,
      scripts=['scripts/tf_search', 'scripts/tf_realtime'],
      classifiers=[
          'License :: OSI Approved :: BSD License',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Operating System :: OS Independent',
          ],
    )
