from setuptools import setup, find_packages

setup(
    name="SteamAutoFriend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "steamautofriend=steamautofriend.main:main",
        ],
    },
    author="Original Author",
    author_email="example@example.com",
    description="Automated Steam friend request sender",
    keywords="steam, friend, automation",
    python_requires=">=3.7",
) 