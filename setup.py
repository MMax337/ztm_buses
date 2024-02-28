import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ztm_buses",  
    version="0.0.1",
    author="Maksym Matviienko", 
    author_email="xxxmax337@example.com",
    description="Warsaw ZTM API Fetcher and Data Analyzer",
    long_description=long_description,
    install_requires=["requests","urllib3", "folium","plotly_express", "pandas"],
    setup_requires=["requests","urllib3","folium", "plotly_express", "pandas"],
    long_description_content_type="text/markdown",
    url="https://github.com/MMax337/ztm_buses/tree/main",
    packages=setuptools.find_packages(exclude=["contrib", "docs", "tests*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
