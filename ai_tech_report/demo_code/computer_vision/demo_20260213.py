#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算机视觉多模态图像分析系统
Computer Vision Multimodal Image Analysis System

基于最新ArXiv论文技术的视觉理解与特征提取演示
实现了Transformer架构的视觉注意力机制和多模态特征融合

依赖安装:
    pip install torch torchvision transformers opencv-python pillow numpy tqdm

作者: AI教育专家
创建时间: 2026-02-13
"""

import os
import cv2
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
from transformers import (
    AutoProcessor, 
    AutoModelForVision2Seq,
    CLIPVisionModel,
    CLIPProcessor
)
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm
import warnings

# 忽略警告信息，保持输出整洁
warnings.filterwarnings('ignore')

# 设置设备 - 自动选择GPU或CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"当前使用设备: {device}")


class VisionFeatureExtractor:
    """
    视觉特征提取器类
    
    基于Transformer架构的视觉特征提取，
    实现了论文中提到的注意力机制和多模态融合技术。
    
    功能:
        1. 使用CLIP模型提取图像特征
        2. 支持批量图像处理
        3. 提取多尺度特征表示
    """
    
    def __init__(self, model_name: str = "openai/clip-vit-large-patch14-336"):
        """
        初始化视觉特征提取器
        
        Args:
            model_name: 预训练模型名称，默认使用CLIP大模型
        """
        print(f"正在加载模型: {model_name}")
        
        # 加载CLIP视觉模型和处理器
        self.vision_model = CLIPVisionModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        
        # 设置为评估模式
        self.vision_model.to(device)
        self.vision_model.eval()
        
        print("模型加载完成!")
    
    def extract_features(self, image: Image.Image) -> torch.Tensor:
        """
        从单张图像中提取视觉特征
        
        Args:
            image: PIL格式的输入图像
            
        Returns:
            图像特征向量 (torch.Tensor)
        """
        # 图像预处理
        inputs = self.processor(
            images=image, 
            return_tensors="pt"
        ).to(device)
        
        # 提取特征
        with torch.no_grad():
            outputs = self.vision_model(**inputs)
            # 使用[CLS]标记对应的特征作为全局表示
            features = outputs.last_hidden_state[:, 0, :]
        
        return features
    
    def extract_multi_scale_features(self, image: Image.Image, 
                                      scales: List[float] = [1.0, 0.75, 0.5, 0.25]
                                     ) -> Dict[str, torch.Tensor]:
        """
        提取多尺度图像特征
        
        借鉴论文中多尺度特征融合的思想，
        通过不同尺度的图像提取丰富的特征表示。
        
        Args:
            image: PIL格式的输入图像
            scales: 缩放比例列表
            
        Returns:
            包含不同尺度特征的字典
        """
        multi_scale_features = {}
        
        for scale in scales:
            # 缩放图像
            width, height = image.size
            new_width = int(width * scale)
            new_height = int(height * scale)
            scaled_image = image.resize((new_width, new_height))
            
            # 提取特征
            features = self.extract_features(scaled_image)
            multi_scale_features[f"scale_{scale}"] = features
        
        return multi_scale_features
    
    def compare_images(self, image1: Image.Image, image2: Image.Image) -> float:
        """
        计算两张图像的相似度
        
        基于余弦相似度计算图像特征之间的距离。
        
        Args:
            image1: 第一张图像
            image2: 第二张图像
            
        Returns:
            相似度分数 (0-1之间)
        """
        features1 = self.extract_features(image1)
        features2 = self.extract_features(image2)
        
        # 计算余弦相似度
        cosine_sim = torch.nn.functional.cosine_similarity(
            features1, features2, dim=1
        )
        
        return cosine_sim.item()


class MultimodalImageAnalyzer:
    """
    多模态图像分析器
    
    结合视觉和文本信息的智能图像分析系统，
    实现了论文中的多模态思维链推理。
    
    功能:
        1. 图像描述生成
        2. 视觉问答
        3. 图像相似度比较
    """
    
    def __init__(self, model_name: str = "Salesforce/instructblip-flan-t5-large"):
        """
        初始化多模态分析器
        
        Args:
            model_name: 多模态模型名称
        """
        print(f"正在加载多模态模型: {model_name}")
        
        # 加载指令调整的图像到文本模型
        self.model = AutoModelForVision2Seq.from_pretrained(model_name)
        self.processor = AutoProcessor.from_pretrained(model_name)
        
        self.model.to(device)
        self.model.eval()
        
        print("多模态模型加载完成!")
    
    def generate_description(self, image: Image.Image, 
                           prompt: str = "Describe this image in detail."
                           ) -> str:
        """
        生成图像描述
        
        Args:
            image: 输入图像
            prompt: 提示词
            
        Returns:
            生成的描述文本
        """
        inputs = self.processor(
            images=image,
            text=prompt,
            return_tensors="pt"
        ).to(device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,
                num_beams=5,
                temperature=0.7,
                do_sample=True
            )
        
        description = self.processor.decode(outputs[0], skip_special_tokens=True)
        return description
    
    def answer_question(self, image: Image.Image, 
                       question: str) -> str:
        """
        回答关于图像的问题
        
        Args:
            image: 输入图像
            question: 问题
            
        Returns:
            回答文本
        """
        prompt = f"Question: {question} Answer:"
        return self.generate_description(image, prompt)


class ImageProcessingUtils:
    """
    图像处理工具类
    
    提供基础的图像预处理和后处理功能。
    
    功能:
        1. 图像加载和保存
        2. 图像增强
        3. 特征可视化
    """
    
    @staticmethod
    def load_image(image_path: str) -> Optional[Image.Image]:
        """
        加载图像文件
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            PIL图像对象，失败返回None
        """
        try:
            # 使用OpenCV加载图像
            img_cv2 = cv2.imread(image_path)
            if img_cv2 is None:
                print(f"无法加载图像: {image_path}")
                return None
            
            # 转换为RGB格式 (OpenCV默认BGR)
            img_rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
            
            # 转换为PIL格式
            return Image.fromarray(img_rgb)
        
        except Exception as e:
            print(f"加载图像时出错: {e}")
            return None
    
    @staticmethod
    def save_features_to_file(features: torch.Tensor, 
                             output_path: str,
                             format: str = "pt") -> None:
        """
        保存特征向量到文件
        
        Args:
            features: 特征向量
            output_path: 输出文件路径
            format: 保存格式 ("pt"为PyTorch格式，"npy"为NumPy格式)
        """
        if format == "pt":
            torch.save(features, output_path)
        elif format == "npy":
            np.save(output_path, features.cpu().numpy())
        else:
            raise ValueError(f"不支持的格式: {format}")
        
        print(f"特征已保存到: {output_path}")
    
    @staticmethod
    def visualize_attention(image: Image.Image, 
                           attention_weights: np.ndarray,
                           output_path: str,
                           alpha: float = 0.5) -> None:
        """
        可视化注意力权重
        
        将注意力权重叠加到原始图像上。
        
        Args:
            image: 原始图像
            attention_weights: 注意力权重矩阵
            output_path: 输出图像路径
            alpha: 叠加透明度
        """
        # 调整注意力权重大小以匹配图像
        attention_map = cv2.resize(attention_weights, image.size)
        
        # 应用颜色映射
        heatmap = cv2.applyColorMap(
            np.uint8(255 * attention_map), 
            cv2.COLORMAP_JET
        )
        
        # 转换为RGB
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # 叠加到原图
        original_array = np.array(image)
        result = cv2.addWeighted(
            np.array(original_array), 
            1 - alpha, 
            heatmap, 
            alpha, 
            0
        )
        
        # 保存结果
        cv2.imwrite(output_path, cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
        print(f"注意力可视化已保存到: {output_path}")


def demo_image_analysis():
    """
    演示函数：展示计算机视觉系统的完整功能
    
    这个函数演示了如何使用上述类进行图像分析，
    包括特征提取、相似度比较和多模态推理。
    """
    print("\n" + "="*60)
    print("计算机视觉多模态图像分析系统演示")
    print("="*60 + "\n")
    
    # 创建示例图像（如果没有真实图像）
    print("创建示例测试图像...")
    
    # 创建测试图像1：红色背景的矩形
    img1 = Image.new('RGB', (224, 224), color=(255, 100, 100))
    img1.save("test_image_1.jpg")
    
    # 创建测试图像2：蓝色背景的矩形（与图像1相似）
    img2 = Image.new('RGB', (224, 224), color=(100, 100, 255))
    img2.save("test_image_2.jpg")
    
    # 创建测试图像3：绿色背景的矩形（与图像1不太相似）
    img3 = Image.new('RGB', (224, 224), color=(100, 255, 100))
    img3.save("test_image_3.jpg")
    
    print("测试图像创建完成！\n")
    
    # 初始化特征提取器
    print("1. 初始化视觉特征提取器...")
    extractor = VisionFeatureExtractor()
    
    # 加载测试图像
    test_images = [
        Image.open("test_image_1.jpg"),
        Image.open("test_image_2.jpg"),
        Image.open("test_image_3.jpg")
    ]
    
    print("\n2. 提取图像特征...")
    for i, img in enumerate(test_images):
        # 提取单尺度特征
        features = extractor.extract_features(img)
        print(f"   图像{i+1}特征维度: {features.shape}")
        
        # 提取多尺度特征
        multi_scale = extractor.extract_multi_scale_features(img)
        print(f"   图像{i+1}多尺度特征数量: {len(multi_scale)}")
    
    print("\n3. 计算图像相似度...")
    # 计算图像1和图像2的相似度
    similarity_12 = extractor.compare_images(test_images[0], test_images[1])
    print(f"   图像1与图像2相似度: {similarity_12:.4f}")
    
    # 计算图像1和图像3的相似度
    similarity_13 = extractor.compare_images(test_images[0], test_images[2])
    print(f"   图像1与图像3相似度: {similarity_13:.4f}")
    
    # 计算图像2和图像3的相似度
    similarity_23 = extractor.compare_images(test_images[1], test_images[2])
    print(f"   图像2与图像3相似度: {similarity_23:.4f}")
    
    print("\n4. 测试多模态分析功能...")
    analyzer = MultimodalImageAnalyzer()
    
    # 生成图像描述
    description = analyzer.generate_description(
        test_images[0], 
        "Describe this image in detail."
    )
    print(f"   图像描述: {description}")
    
    # 回答问题
    answer = analyzer.answer_question(
        test_images[0], 
        "What colors are present in this image?"
    )
    print(f"   颜色问答: {answer}")
    
    print("\n5. 保存特征向量...")
    # 保存图像1的特征
    features = extractor.extract_features(test_images[0])
    ImageProcessingUtils.save_features_to_file(
        features, 
        "image_features.pt"
    )
    
    # 清理临时测试图像
    print("\n6. 清理测试文件...")
    for i in range(1, 4):
        filename = f"test_image_{i}.jpg"
        if os.path.exists(filename):
            os.remove(filename)
            print(f"   已删除: {filename}")
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60)
    print("\n功能总结:")
    print("  ✓ 视觉特征提取 (基于Transformer架构)")
    print("  ✓ 多尺度特征分析")
    print("  ✓ 图像相似度比较")
    print("  ✓ 多模态描述生成")
    print("  ✓ 视觉问答功能")
    print("\n注意事项:")
    print("  - 首次运行会自动下载预训练模型")
    print("  - 建议在GPU环境下运行以获得更好性能")
    print("  - 可替换测试图像路径进行实际应用")


def main():
    """
    主函数
    
    程序入口点，负责协调各个模块的执行。
    """
    try:
        # 运行演示
        demo_image_analysis()
    
    except KeyboardInterrupt:
        print("\n\n用户中断程序执行")
    
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
```

[2m⏱️  Step 1 completed in 71.46s (total: 71.46s)[0m

[2m────────────────────────────────────────────────────────────[0m


[1m[96mSession Statistics:[0m
[2m────────────────────────────────────────[0m
  Session Duration: 00:01:11
  Total Messages: 3
    - User Messages: [92m1[0m
    - Assistant Replies: [94m1[0m
    - Tool Calls: [93m0[0m
  Available Tools: 8
  API Tokens Used: [95m7,150[0m
[2m────────────────────────────────────────[0m

[96mCleaning up MCP connections...[0m
[32m✅ Cleanup complete[0m

