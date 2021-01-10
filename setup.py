import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ntu_learn_downloader",
    version="0.2.2",
    author="Raynold Ng",
    author_email="raynold.ng24@gmail.com",
    description="API wrapper to NTU Learn",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leafgecko/ntulearn_downloader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["beautifulsoup4==4.7.1", "requests==2.22.0", "lxml==4.5.1"],
)

