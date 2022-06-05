**注意事项**
- [QQ音乐爬虫原理视频](https://www.bilibili.com/video/BV1pk4y1m7TG)
- `execjs`依赖于`NodeJS`，请务必提前安装（本项目的开发环境为`NodeJS v14.6.0`）。
- `cd`到当前文件夹，执行`python demo.py`即可
- `demo.py`为没有入库版，只爬取一个分类，没开多进程，方便大家理解
- 请务必`demo.py` 的`filename`和`with open`项目路径问题
- `get_singer_mid(index)` 方法决定分类爬取