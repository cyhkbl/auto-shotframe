# auto-shotframe

[English](https://github.com/SeanYancy/auto-shotframe/blob/main/README.md) |
简体中文

`auto-shotframe` 是一款跨平台命令行工具，可以给 JPEG、HEIC、HEIF 和 TIFF
照片添加适合分享的摄影相框。成品包含模糊背景、相机品牌标志以及从 EXIF
读取的拍摄参数。

输入：

```text
photo.heic
```

工具会在原图旁边生成：

```text
photo_framed.jpg
```

原图不会被修改。如果目标文件已经存在，则依次生成
`photo_framed_2.jpg`、`photo_framed_3.jpg`。

## 功能

- 支持单张 JPEG、HEIC、HEIF、TIF、TIFF 照片，也支持处理一个目录；
- 完整保留照片内容，不裁切、不拉伸；
- 按照片比例生成模糊、压暗的延展背景；
- 可选圆角照片，投影也跟随圆角轮廓；
- 从 EXIF 读取相机、镜头、ISO、光圈、快门和焦距；
- 识别 Apple、Nikon、Canon、Sony、Fujifilm、Panasonic、Leica、Hasselblad
  和 OnePlus；
- 把 OnePlus `KB2000` 这类内部型号代码展开成市售名称（`OnePlus 8T`），
  只影响画面文字，不改动 EXIF；
- 内置厂商标志，也可以用自己的透明 PNG 覆盖；
- 使用 Jost Light/Regular 字重和适合摄影排版的字距；
- 默认生成长边不超过 2160 像素的社交媒体版本；
- 在照片缩放到最终工作尺寸后才绘制 Logo 和文字，减少平台二次缩放时的模糊；
- 导出时移除 GPS 和设备识别信息；
- 保留常用摄影 EXIF 和 ICC 色彩配置；
- 支持 Python 3.10 及以上版本，可在 macOS、Windows 和 Linux 使用。

## 安装

从 PyPI 安装：

```bash
python -m pip install auto-shotframe
```

从源码目录安装：

```bash
python -m pip install .
```

## 基本用法

处理一张 JPEG、HEIF 或 TIFF 照片：

```bash
auto-shotframe /path/to/photo.heic
```

处理目录里的全部支持格式：

```bash
auto-shotframe /path/to/photos/
```

目录处理不会递归进入子目录。文件名以 `_framed` 或 `_framed_N` 结尾的成品会
被自动跳过。

## 输出尺寸

默认模式针对小红书、微信朋友圈等社交平台优化。最终相框画布的长边不会超过
2160 像素，小图不会被放大。工具会先缩小照片，再在最终工作尺寸上生成背景、
Logo 和文字。

保留原始像素尺寸：

```bash
auto-shotframe photo.jpg -o
```

`-o` 是 `--original-size` 的快捷写法。它表示“不缩放像素尺寸”，并不代表无损：
添加相框后仍然需要重新编码 JPEG。

指定其他最终画布长边：

```bash
auto-shotframe photo.jpg --max-long-edge 1080
```

`-o` 与 `--max-long-edge` 不能同时使用。

## 参数

```text
--quality N          JPEG 质量 1–100；默认 92，原尺寸模式默认 95
-o, --original-size  保留原图像素尺寸，但仍会重新编码 JPEG
--max-long-edge N    最终相框画布的最大长边；默认 2160
--margin R           左右边距相对照片短边的比例；默认 0.105
--top-margin R       顶部边距比例；默认 0.130
--info-height R      底部信息区高度比例；默认 0.22
--corner-radius R    照片圆角半径比例；默认 0.040
--blur R             背景模糊半径比例；默认 0.03
--darken R           背景压暗程度 0–1；默认 0.20
--logo-dir PATH      自定义小写 PNG Logo 所在目录
--no-logo            不显示厂商标志
--version            显示当前版本
```

示例：

```bash
auto-shotframe photo.jpg --quality 90 --darken 0.30 --max-long-edge 1440
```

## 自定义 Logo

传入一个包含以下任意文件名的目录：

```text
apple.png
nikon.png
canon.png
sony.png
fujifilm.png
panasonic.png
leica.png
hasselblad.png
oneplus.png
```

推荐使用透明背景 PNG：

```bash
auto-shotframe photo.jpg --logo-dir ./my-logos
```

自定义 Logo 的优先级高于内置资源。如果识别出了厂商但 Logo 无法使用，工具会
改为显示厂商名称。

## 默认布局

全部尺寸都以照片短边为基准：

| 元素 | 默认值 |
| --- | ---: |
| 左右边距 | 10.5% |
| 顶部边距 | 13% |
| 底部信息区 | 22% |
| 照片圆角半径 | 4% |
| 背景模糊半径 | 3% |
| 背景压暗 | 20% |
| Logo 最大高度 | 5% |

照片从左、右、上三边按边距内缩，底部留给信息区。本版本默认使用较宽的圆角
相框，让模糊背景露得更多；想要更紧凑、更接近上游默认的直角相框就传更小的值：

```bash
auto-shotframe photo.jpg --margin 0.03 --top-margin 0.04 --corner-radius 0
```

第一行显示相机与镜头。Apple 照片只显示 iPhone 型号，不会把
`back triple camera` 之类的原始 EXIF 文本放进画面。第二行显示 ISO、光圈、
快门和焦距。缺少的字段会被直接省略，不会留下空占位。

部分厂商会在 EXIF 里写入内部型号代码而不是产品名。工具只把这些代码展开成
市售名称，导出照片的 EXIF 仍然保留原值：

| EXIF Make | EXIF Model | 画面显示 |
| --- | --- | --- |
| `OnePlus` | `KB2000` | `OnePlus 8T` |
| `OnePlus` | `KB2001` | `OnePlus 8T` |
| `OnePlus` | `KB2003` | `OnePlus 8T` |
| `OnePlus` | `KB2005` | `OnePlus 8T` |
| `OnePlus` | `KB2007` | `OnePlus 8T+ 5G` |

厂商识别不区分大小写，也会忽略首尾空白，因此 `OnePlus`、`ONEPLUS` 和
`oneplus` 都能识别。

## 元数据与隐私

成品会尽量保留常用摄影 EXIF 和源照片的 ICC 色彩配置，同时移除：

- GPS 定位信息；
- 相机和镜头序列号；
- 可能包含厂商设备标识的 MakerNote；
- Image Unique ID 和相机所有者名称；
- TIFF 转 JPEG 时的存储结构字段，以及 XMP、IPTC 和 Photoshop 资源容器。

源 JPEG、HEIF 或 TIFF 文件始终不会被修改。

## HEIF 说明

`.heic` 和 `.heif` 输入会读取容器中的主图，并始终输出同目录 JPEG。10-bit 或
12-bit HEIF 会生成 8-bit SDR JPEG。HDR gain map、辅助深度图、容器中的其他
图像以及 Live Photo 视频不会被复制到成品。

iPhone 原片通常包含机型、镜头、ISO、光圈、快门和焦距。截图、社交平台下载图
或其他二次导出文件可能已经删除部分或全部 EXIF；工具只显示实际存在的信息。

## TIFF 说明

`.tif` 和 `.tiff` 输入会读取第一张图像，并始终输出同目录 JPEG。相机导出的
TIFF 如果能被 Pillow 读取，工具会从 TIFF IFD/EXIF 字段提取拍摄参数。多页
TIFF 只处理第一页。

当前输出流程不是无损流程：16-bit TIFF 会转换为 8-bit RGB JPEG。
`-o/--original-size` 只是不缩放像素尺寸，并不会保留 TIFF 位深或压缩方式。
遇到不支持的 TIFF 压缩格式或损坏文件时，工具会报告该文件，并继续处理目录中
的其他照片。

## 开发

```bash
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest
.venv/bin/ruff check .
```

Windows 请把 `.venv/bin/python` 替换为 `.venv\Scripts\python`。

从仓库内的 SVG 重新生成运行时 PNG Logo：

```bash
.venv/bin/python scripts/render_logos.py
```

## 第三方资源与商标

字体和 Logo 来源记录在
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。所有产品名称、商标和
注册商标均归各自权利人所有。本项目仅根据照片元数据识别厂商，不代表与相关
厂商存在合作、赞助或背书关系。

## 许可证

项目代码采用 MIT License。随包分发的第三方资源仍遵循
`THIRD_PARTY_NOTICES.md` 中列出的授权和声明。
