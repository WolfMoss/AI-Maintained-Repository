#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算机视觉示范代码 - 基于Transformer的图像描述生成
==================================================

依赖库 (请先安装):
    pip install torch torchvision transformers pillow gradio
    
相关AI论文技术:
    - UniT: Unified Multimodal Chain-of-Thought Test-time Scaling
    - Stroke of Surprise: Progressive Semantic Illusions in Vector Sketching

功能演示:
    1. 图像加载与预处理
    2. 基于预训练模型的图像描述生成
    3. 目标检测可视化
    4. 图像特征提取与相似度计算
"""

import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from transformers import AutoProcessor, AutoModelForVision2Seq
from transformers import DetrImageProcessor, DetrForObjectDetection
import warnings
warnings.filterwarnings('ignore')

# ==================== 配置参数 ====================
# 设备选择 (优先GPU)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🖥️  使用设备: {DEVICE}")

# 预训练模型名称 (Hugging Face格式)
IMAGE_CAPTION_MODEL = "microsoft/llava-1.5-7b-hf"  # 图像描述模型
# 备选: "Salesforce/blip2-opt-2.7b"  # 轻量级选择
OBJECT_DETECTION_MODEL = "facebook/detr-resnet-50"  # 目标检测模型


def load_image_caption_model():
    """
    加载图像描述生成模型
    
    使用LLaVA模型进行图像到文本的转换
    该模型结合了视觉编码器和语言模型,实现了视觉理解与生成
    
    相关论文技术:
    - UniT: 统一多模态思维链推理
    """
    print("📦 正在加载图像描述模型...")
    try:
        # 使用轻量级模型以确保本地可运行
        processor = AutoProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
        model = AutoModelForVision2Seq.from_pretrained(
            "Salesforce/blip-image-captioning-large",
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
        )
        model.to(DEVICE)
        model.eval()
        print("✅ 图像描述模型加载成功!")
        return processor, model
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        print("🔄 使用备用方案...")
        return None, None


def load_object_detection_model():
    """
    加载目标检测模型
    
    使用DETR (DEtection TRansformer) 模型进行目标检测
    DETR将目标检测视为集合预测问题,使用Transformer架构
    
    相关论文技术:
    - AttentionRetriever: 注意力层作为长文档检索器
    """
    print("📦 正在加载目标检测模型...")
    try:
        processor = DetrImageProcessor.from_pretrained(OBJECT_DETECTION_MODEL)
        model = DetrForObjectDetection.from_pretrained(OBJECT_DETECTION_MODEL)
        model.to(DEVICE)
        model.eval()
        print("✅ 目标检测模型加载成功!")
        return processor, model
    except Exception as e:
        print(f"❌ 目标检测模型加载失败: {e}")
        return None, None


def generate_image_caption(processor, model, image_path):
    """
    生成图像描述
    
    使用视觉语言模型分析图像内容并生成自然语言描述
    
    参数:
        processor: 图像处理器
        model: 视觉语言模型
        image_path: 图像文件路径
        
    返回:
        str: 生成的图像描述
    """
    if model is None:
        return "模型未加载"
    
    try:
        # 加载并预处理图像
        image = Image.open(image_path).convert('RGB')
        
        # 编码图像并生成描述
        inputs = processor(images=image, return_tensors="pt").to(DEVICE)
        
        with torch.no_grad():
            # 生成描述 (使用beam search获得更好结果)
            output = model.generate(
                **inputs,
                max_new_tokens=100,
                num_beams=5,
                do_sample=False
            )
        
        # 解码生成的文本
        caption = processor.batch_decode(output, skip_special_tokens=True)[0]
        return caption
        
    except Exception as e:
        return f"生成失败: {str(e)}"


def detect_objects(processor, model, image_path, confidence_threshold=0.7):
    """
    目标检测函数
    
    使用DETR模型检测图像中的物体边界框和类别
    
    参数:
        processor: DETR图像处理器
        model: DETR目标检测模型
        image_path: 图像路径
        confidence_threshold: 置信度阈值
        
    返回:
        dict: 包含检测结果的字典
    """
    if model is None:
        return {"success": False, "message": "模型未加载"}
    
    try:
        # 加载图像
        image = Image.open(image_path).convert('RGB')
        original_size = image.size
        
        # 预处理
        inputs = processor(images=image, return_tensors="pt").to(DEVICE)
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        # 后处理 - 解析检测结果
        target_sizes = torch.tensor([original_size[::-1]])
        results = processor.post_process_object_detection(
            outputs, 
            target_sizes=target_sizes,
            threshold=confidence_threshold
        )[0]
        
        # 提取检测信息
        detections = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            detection = {
                "label": model.config.id2label[label.item()],
                "confidence": round(score.item(), 3),
                "box": [round(b.item(), 2) for b in box]
            }
            detections.append(detection)
        
        return {
            "success": True,
            "detections": detections,
            "count": len(detections)
        }
        
    except Exception as e:
        return {"success": False, "message": str(e)}


def draw_detection_results(image_path, detections, output_path="output_detections.jpg"):
    """
    在图像上绘制检测结果
    
    将目标检测的边界框和标签绘制到图像上
    
    参数:
        image_path: 输入图像路径
        detections: 检测结果列表
        output_path: 输出图像路径
    """
    try:
        image = Image.open(image_path).convert('RGB')
        draw = ImageDraw.Draw(image)
        
        # 定义颜色方案 (COCO数据集80类)
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0)
        ]
        
        for i, det in enumerate(detections):
            box = det["box"]
            label = det["label"]
            conf = det["confidence"]
            
            # 绘制边界框
            color = colors[i % len(colors)]
            draw.rectangle(box, outline=color, width=3)
            
            # 绘制标签背景
            text = f"{label}: {conf:.2f}"
            draw.text((box[0], box[1] - 15), text, fill=color)
        
        # 保存结果
        image.save(output_path)
        print(f"💾 检测结果已保存至: {output_path}")
        
    except Exception as e:
        print(f"❌ 绘制失败: {e}")


def extract_image_features(processor, model, image_path):
    """
    提取图像特征向量
    
    使用预训练模型的视觉编码器提取图像的深度特征
    可用于图像相似度计算、聚类等任务
    
    参数:
        processor: 图像处理器
        model: 视觉模型
        image_path: 图像路径
        
    返回:
        np.ndarray: 特征向量
    """
    if model is None:
        return None
    
    try:
        image = Image.open(image_path).convert('RGB')
        inputs = processor(images=image, return_tensors="pt").to(DEVICE)
        
        with torch.no_grad():
            # 提取视觉特征
            if hasattr(model, 'vision_model'):
                # 对于BLIP-2类型模型
                vision_outputs = model.vision_model(pixel_values=inputs['pixel_values'])
                features = vision_outputs.last_hidden_state.mean(dim=1)
            else:
                features = model.get_image_features(**inputs)
        
        return features.cpu().numpy()
        
    except Exception as e:
        print(f"❌ 特征提取失败: {e}")
        return None


def calculate_similarity(feature1, feature2):
    """
    计算两个特征向量之间的余弦相似度
    
    参数:
        feature1: 第一个特征向量
        feature2: 第二个特征向量
        
    返回:
        float: 相似度分数 (0-1)
    """
    # 展平向量
    f1 = feature1.flatten()
    f2 = feature2.flatten()
    
    # 余弦相似度
    dot_product = np.dot(f1, f2)
    norm1 = np.linalg.norm(f1)
    norm2 = np.linalg.norm(f2)
    
    similarity = dot_product / (norm1 * norm2 + 1e-8)
    return float(similarity)


def create_demo_image():
    """
    创建一个示例图像用于测试
    
    生成包含简单几何形状的测试图像
    """
    # 创建空白图像
    img = Image.new('RGB', (800, 600), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # 绘制几何形状
    # 圆形 - 红色
    draw.ellipse([100, 100, 300, 300], fill=(255, 100, 100), outline=(0, 0, 0), width=2)
    
    # 矩形 - 绿色
    draw.rectangle([350, 100, 600, 300], fill=(100, 255, 100), outline=(0, 0, 0), width=2)
    
    # 三角形 - 蓝色
    draw.polygon([(450, 400), (350, 550), (550, 550)], fill=(100, 100, 255), outline=(0, 0, 0))
    
    # 文字
    try:
        draw.text((300, 50), "Computer Vision Demo", fill=(0, 0, 0))
    except:
        pass
    
    # 保存
    img.save("demo_image.jpg")
    print("📷 演示图像已创建: demo_image.jpg")
    return "demo_image.jpg"


def main():
    """
    主函数 - 演示计算机视觉的主要功能
    """
    print("=" * 60)
    print("🖼️  计算机视觉示范程序")
    print("=" * 60)
    
    # 1. 创建测试图像
    print("\n📌 步骤1: 创建测试图像")
    test_image = create_demo_image()
    
    # 2. 加载模型
    print("\n📌 步骤2: 加载AI模型")
    caption_processor, caption_model = load_image_caption_model()
    detection_processor, detection_model = load_object_detection_model()
    
    # 3. 图像描述生成
    print("\n📌 步骤3: 图像描述生成")
    caption = generate_image_caption(caption_processor, caption_model, test_image)
    print(f"📝 生成的描述: {caption}")
    
    # 4. 目标检测
    print("\n📌 步骤4: 目标检测")
    detections = detect_objects(detection_processor, detection_model, test_image)
    if detections.get("success"):
        print(f"🔍 检测到 {detections['count']} 个物体:")
        for det in detections["detections"]:
            print(f"   - {det['label']}: {det['confidence']}")
        
        # 绘制检测结果
        draw_detection_results(test_image, detections["detections"])
    
    # 5. 特征提取与相似度
    print("\n📌 步骤5: 图像特征提取")
    features = extract_image_features(caption_processor, caption_model, test_image)
    if features is not None:
        print(f"📊 特征维度: {features.shape}")
        
        # 自身相似度 (应为1.0)
        sim_self = calculate_similarity(features, features)
        print(f"🔗 自相似度: {sim_self:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
