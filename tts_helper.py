import subprocess
import os

def text_to_speech(text, output_path, character="topaz"):
    """
    调用 GPT-SoVITS 命令行工具生成语音
    """
    # 根据你的整合包实际路径修改
    gpt_path = r"F:/googledownload/GPT-SoVITS-v2pro-20250604-nvidia50/GPT_weights_v2Pro"   # 你有的 GPT 模型
    sovits_path = r"SoVITS_weights/topaz_voices-e10.pth"    # 你有的 SoVITS 模型
    # 如果你训练出了新的 D_23333.pth 和 G_23333.pth，就换成它们的路径
    
    cmd = [
        "python", "GPT-SoVITS/inference.py",  # 改成你的实际路径
        "--gpt_model", gpt_path,
        "--sovits_model", sovits_path,
        "--text", text,
        "--output", output_path
    ]
    # 如果整合包需要参考音频，加上 --ref_audio 参数
    # cmd += ["--ref_audio", "参考音频.wav"]
    
    subprocess.run(cmd, check=True)
    return output_path