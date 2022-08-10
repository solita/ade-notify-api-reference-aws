import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="ade-notify-api-reference-aws",
    version="0.9.0",

    description="ade-notify-api-reference-aws",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Henri Hemminki",

    package_dir={"": "stacks"},
    packages=setuptools.find_packages(where="ade-notify-api-reference-aws"),

    install_requires=[
        "aws-cdk-lib>=2.37.0",
        "constructs>=10.0.0"
    ],

    python_requires=">=3.8",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
