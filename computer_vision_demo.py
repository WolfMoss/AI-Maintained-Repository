#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算机视觉演示代码 - 基于Transformer的图像理解与注意力可视化

依赖库 (请先安装):
    pip install torch torchvision transformers pillow matplotlib numpy

作者: AI教育专家
日期: 2026-02-16
"""

# 导入必要的库
import torch
import torchvision.transforms as transforms
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ==================== 配置部分 ====================

# 设备配置 - 使用GPU如果可用,否则使用CPU
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"当前使用设备: {DEVICE}")

# 模型配置 - 使用CLIP模型进行图像-文本理解
MODEL_NAME = "openai/clip-vit-base-patch32"


def load_clip_model():
    """
    加载CLIP模型
    CLIP (Contrastive Language-Image Pre-training) 是OpenAI开发的多模态模型,
    能够理解图像和文本之间的关系
    """
    from transformers import CLIPProcessor, CLIPModel
    
    print("正在加载CLIP模型...")
    model = CLIPModel.from_pretrained(MODEL_NAME)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model.to(DEVICE)
    model.eval()
    print("模型加载完成!")
    return model, processor


def load_image_attention_model():
    """
    加载用于注意力可视化的Vision Transformer模型
    ViT (Vision Transformer) 将Transformer架构应用于图像分类任务
    """
    from transformers import ViTForImageClassification, ViTImageProcessor
    
    print("正在加载ViT模型用于注意力分析...")
    model_name = "google/vit-base-patch16-224"
    model = ViTForImageClassification.from_pretrained(model_name)
    processor = ViTImageProcessor.from_pretrained(model_name)
    model.to(DEVICE)
    model.eval()
    print("ViT模型加载完成!")
    return model, processor


def preprocess_image(image_path, processor):
    """
    预处理图像
    将图像转换为模型所需的输入格式
    
    参数:
        image_path: 图像文件路径
        processor: 图像处理器
    
    返回:
        processed_image: 处理后的图像张量
    """
    # 打开图像文件
    image = Image.open(image_path).convert('RGB')
    
    # 使用processor处理图像
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    
    return image, inputs


def image_text_similarity(model, processor, image_path, texts):
    """
    计算图像与文本描述之间的相似度
    这是CLIP模型的核心功能之一 - 零样本图像分类
    
    参数:
        model: CLIP模型
        processor: CLIP处理器
        image_path: 图像路径
        texts: 文本描述列表
    
    返回:
        similarities: 相似度分数
    """
    # 预处理图像
    image = Image.open(image_path).convert('RGB')
    
    # 使用processor处理图像和文本
    inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    
    # 获取模型输出
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 计算相似度 (使用logits_per_image)
    logits_per_image = outputs.logits_per_image
    similarities = torch.softmax(logits_per_image, dim=1)
    
    return similarities.cpu().numpy()[0]


def visualize_attention(model, processor, image_path, save_path="attention_map.png"):
    """
    可视化ViT模型的注意力机制
    展示模型在处理图像时关注的不同区域
    
    参数:
        model: ViT模型
        processor: ViT处理器
        image_path: 图像路径
        save_path: 保存路径
    """
    from transformers import ViTForImageClassification
    
    # 打开并处理图像
    image = Image.open(image_path).convert('RGB')
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    
    # 获取注意力权重
    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)
        attentions = outputs.attentions
        
        # 获取最后一层的注意力权重
        last_layer_attention = attentions[-1]
        
        # 计算平均注意力 (对所有注意力头取平均)
        avg_attention = last_layer_attention.mean(dim=1)[0]
        
        # 获取CLS token对所有patch的注意力
        cls_attention = avg_attention[0, 1:].reshape(14, 14).cpu().numpy()
    
    # 创建可视化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # 显示原图
    axes[0].imshow(image)
    axes[0].set_title('原始图像', fontsize=14)
    axes[0].axis('off')
    
    # 显示注意力热力图
    im = axes[1].imshow(cls_attention, cmap='jet', interpolation='nearest')
    axes[1].set_title('注意力热力图 (ViT)', fontsize=14)
    axes[1].axis('off')
    
    # 添加颜色条
    plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"注意力可视化图已保存至: {save_path}")
    plt.close()


def classify_image(model, processor, image_path, top_k=5):
    """
    使用CLIP进行零样本图像分类
    不需要任何训练数据,直接通过文本描述进行分类
    
    参数:
        model: CLIP模型
        processor: CLIP处理器
        image_path: 图像路径
        top_k: 返回前k个最可能的类别
    
    返回:
        predictions: 预测结果列表
    """
    # 定义候选类别 (可以自定义任何文本描述)
    candidate_labels = [
        "a photo of a cat", "a photo of a dog", "a photo of a car",
        "a photo of a person", "a photo of a flower", "a photo of a bird",
        "a photo of a building", "a photo of food", "a photo of a computer",
        "a photo of nature"
    ]
    
    # 计算相似度
    similarities = image_text_similarity(model, processor, image_path, candidate_labels)
    
    # 排序并返回top_k结果
    top_indices = np.argsort(similarities)[::-1][:top_k]
    predictions = [(candidate_labels[i], similarities[i]) for i in top_indices]
    
    return predictions


def demonstrate_multimodal_reasoning(model, processor, image_path):
    """
    演示多模态推理能力
    类似于论文中提到的UniT多模态理解
    
    参数:
        model: CLIP模型
        processor: CLIP处理器
        image_path: 图像路径
    """
    # 定义一些需要推理的问题
    questions = [
        "Is there any animal in this image?",
        "Is this image taken indoors or outdoors?",
        "What is the main color in this image?",
        "Are there any people in this image?"
    ]
    
    # 为每个问题创建是/否的选项
    all_results = []
    
    for question in questions:
        # 创建二元选择
        options = [f"Yes, {question.lower()}", f"No, {question.lower()}"]
        
        # 计算相似度
        image = Image.open(image_path).convert('RGB')
        inputs = processor(text=options, images=image, return_tensors="pt", padding=True)
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits_per_image
            probs = torch.softmax(logits, dim=1)[0]
        
        # 解析问题并保存结果
        result = {
            "question": question,
            "answer": options[0] if probs[0] > probs[1] else options[1],
            "confidence": max(probs[0].item(), probs[1].item())
        }
        all_results.append(result)
    
    return all_results


def create_sample_image():
    """
    创建一个示例图像用于测试
    如果没有现成的图像,使用PIL创建简单图像
    """
    # 创建一个简单的彩色图像
    img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    # 创建渐变效果使其看起来更有意义
    x = np.linspace(0, 255, 224)
    y = np.linspace(0, 255, 224)
    xx, yy = np.meshgrid(x, y)
    
    # 创建圆形图案
    center_x, center_y = 112, 112
    radius = 80
    mask = (xx - center_x)**2 + (yy - center_y)**2 < radius**2
    
    # 填充颜色
    img_array[mask] = [255, 100, 100]  # 红色圆形
    img_array[~mask] = [100, 200, 255]  # 蓝色背景
    
    image = Image.fromarray(img_array)
    
    # 保存为临时文件
    temp_path = "sample_image.png"
    image.save(temp_path)
    print(f"已创建示例图像: {temp_path}")
    
    return temp_path


def main():
    """
    主函数 - 演示计算机视觉的各种功能
    """
    print("=" * 60)
    print("计算机视觉演示 - 基于Transformer的多模态理解")
    print("=" * 60)
    
    # 加载模型
    clip_model, clip_processor = load_clip_model()
    vit_model, vit_processor = load_image_attention_model()
    
    # 准备测试图像
    import os
    test_images = [f for f in os.listdir('.') if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if test_images:
        image_path = test_images[0]
        print(f"\n使用图像: {image_path}")
    else:
        print("\n未找到测试图像,创建示例图像...")
        image_path = create_sample_image()
    
    # 演示1: 零样本图像分类
    print("\n" + "=" * 40)
    print("演示1: 零样本图像分类 (CLIP)")
    print("=" * 40)
    predictions = classify_image(clip_model, clip_processor, image_path)
    print("图像分类结果:")
    for i, (label, prob) in enumerate(predictions, 1):
        print(f"  {i}. {label}: {prob:.4f}")
    
    # 演示2: 图像-文本相似度
    print("\n" + "=" * 40)
    print("演示2: 图像-文本相似度匹配")
    print("=" * 40)
    test_texts = [
        "a cute cat sitting",
        "a modern car on the road", 
        "a beautiful landscape",
        "a person typing on computer"
    ]
    similarities = image_text_similarity(clip_model, clip_processor, image_path, test_texts)
    print("图像与各文本描述的相似度:")
    for text, sim in zip(test_texts, similarities):
        print(f"  '{text}': {sim:.4f}")
    
    # 演示3: 注意力可视化
    print("\n" + "=" * 40)
    print("演示3: Vision Transformer注意力可视化")
    print("=" * 40)
    visualize_attention(vit_model, vit_processor, image_path)
    
    # 演示4: 多模态推理
    print("\n" + "=" * 40)
    print("演示4: 多模态推理 (类似UniT)")
    print("=" * 40)
    reasoning_results = demonstrate_multimodal_reasoning(clip_model, clip_processor, image_path)
    print("多模态推理结果:")
    for result in reasoning_results:
        print(f"  问题: {result['question']}")
        print(f"  回答: {result['answer']} (置信度: {result['confidence']:.2f})")
        print()
    
    print("\n演示完成!")
    print("=" * 60)


# 程序入口点
if __name__ == "__main__":
    # 检查并安装依赖
    try:
        main()
    except ImportError as e:
        print(f"缺少必要的库: {e}")
        print("\n请运行以下命令安装依赖:")
        print("pip install torch torchvision transformers pillow matplotlib numpy")
