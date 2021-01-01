from setuptools import setup

setup(name='pyvcontrol',
      version='0.1a',
      description='Communication with Viessmann heating via Optolink interface',
      url='http://github.com/',
      author='Jochen Schmaehling',
      author_email='j_ochen_573@freenet.de',
      packages=['pyvcontrol'],
      zip_safe=False,
      install_requires=['pyserial'],
      classifiers=[
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',

            'License :: OSI Approved :: GPL-3',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
      ],
      )