import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nonebot_plugin_maidle",
    version="0.0.4",
    author="huanxin996",
    author_email="mc.xiaolang@foxmail.com",
    description="基于nonebot的maimai猜歌插件，支持多平台",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/huanxin996/nonebot_plugin_maidle",
    packages=setuptools.find_packages(),
    install_requires=[
        'nonebot2>=2.3.0,<3.0.0',
        'nonebot_plugin_alconna>=0.54.0',
        'nonebot_plugin_apscheduler>=0.3.0,<0.6.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    include_package_data=True,
)