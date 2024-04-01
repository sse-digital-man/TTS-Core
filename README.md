# TTS-Core
## 项目介绍
本项目是数字人项目的TTS部分， 为LLM部分提供调用接口，同时将生成的音频信息提供给人物模型供其生成对应的唇形和相应的动作
### 架构介绍
本项目提供WebUi通过tts_controller管理和控制TTS-Core的启动/关闭以及控制API/本地模型的切换。

#### src
tts_controller通过管理TTS类型（API/LOCAL）从而修改相应的TTS具体实现，并通过generate_speech来生成对应的声音至`./out`目录下 \
API或本地模型的具体实现都需要通过继承ConfigurableModel/GenerativeModel实现对应的接口（_initialize和synthesize）

#### api
此处可以根据需要封装实现各种WebAPI，目前提供四种API：讯飞、微软Azure、OpenAI、字节跳动

#### localtts
此处可以根据需要封装实现各种本地模型，目前提供1种模型以及[预训练模型](#资源获取)：[Bert-Vits2](https://github.com/fishaudio/Bert-VITS2)

#### config
在`tts_config.json`中配置API和本地模型的相关信息

#### doc(TODO)
开发文档

## 使用说明
1. 使用`pip install -r requirements.txt`安装项目所需依赖
2. 在`config/tts_config.json`文件中配置相关信息
3. 运行`demo/my_gradio.py`运行示例
> 注意：
> 1. python3版本 < 3.12
> 2. 本项目既可以运行在win也可以运行在linux

## 资源获取
1. 预训练模型：[PretrainedModel](https://drive.google.com/drive/folders/1cWW7Vc_sJ2VjsDC2GR3AHEaUteCMxsY2?usp=drive_link)
2. ApiKey(开发人员使用)：[ApiKey](https://drive.google.com/drive/folders/1fo88_FfoLlVd1FJoQfzyOTV72zhAp9bh?usp=sharing)