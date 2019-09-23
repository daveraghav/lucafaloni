import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='lucafaloni',  
     version='0.1',
     scripts=['app'] ,
     author="Raghav Dave",
     author_email="dave.raghav@gmail.com",
     description="A dashboard",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/daveraghav/lucafaloni",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3"
     ],
 )