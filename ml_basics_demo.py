#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习基础示范代码
====================

依赖库 (请使用以下命令安装):
    pip install torch torchvision numpy matplotlib scikit-learn pandas

本代码演示机器学习基础知识:
    1. 数据加载与预处理
    2. 数据集划分与批处理
    3. 神经网络模型构建
    4. 训练循环与验证
    5. 模型评估与可视化

参考AI技术 (基于最新ArXiv论文):
    - 深度学习后处理方法 (ensemble-size-dependence)
    - 表面对齐假设 (Superficial Alignment)
    - 任务无关的点跟踪策略 (Dex4D)
    - 动态人体技能链接 (Perceptive Humanoid)

作者: AI教育专家
日期: 2026-02-19
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# ================== 配置区域 ==================
# 训练超参数配置
CONFIG = {
    "seed": 42,                    # 随机种子，保证结果可复现
    "test_size": 0.2,              # 测试集比例
    "batch_size": 32,             # 批次大小
    "learning_rate": 0.001,       # 学习率
    "num_epochs": 100,            # 训练轮数
    "hidden_dim": 64,             # 隐藏层维度
    "num_classes": 2,             # 分类类别数
    "num_features": 20,           # 特征数量
    "num_samples": 1000,          # 样本数量
    "device": "cuda" if torch.cuda.is_available() else "cpu"
}

# ================== 工具函数 ==================

def set_seed(seed: int):
    """
    设置随机种子，确保结果可复现
    
    Args:
        seed: 随机种子数值
    """
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    print(f"[INFO] 随机种子已设置为: {seed}")


def generate_synthetic_data(num_samples: int, num_features: int, num_classes: int):
    """
    生成合成分类数据集用于演示
    
    使用sklearn的make_classification生成模拟数据
    
    Args:
        num_samples: 样本数量
        num_features: 特征数量
        num_classes: 类别数量
        
    Returns:
        X: 特征矩阵 (numpy数组)
        y: 标签向量 (numpy数组)
    """
    print(f"[INFO] 正在生成合成数据集: {num_samples}样本, {num_features}特征, {num_classes}类别")
    
    # 生成模拟分类数据
    X, y = make_classification(
        n_samples=num_samples,
        n_features=num_features,
        n_informative=15,           #  信息特征数量
        n_redundant=5,              # 冗余特征数量
        n_classes=num_classes,
        random_state=CONFIG["seed"],
        flip_y=0.1                   # 标签噪声比例
    )
    
    print(f"[INFO] 数据生成完成!")
    print(f"  - 特征矩阵形状: {X.shape}")
    print(f"  - 标签分布: {np.bincount(y)}")
    
    return X, y


def preprocess_data(X: np.ndarray, y: np.ndarray, test_size: float):
    """
    数据预处理: 划分训练集/测试集, 标准化特征
    
    Args:
        X: 原始特征矩阵
        y: 标签向量
        test_size: 测试集比例
        
    Returns:
        X_train, X_test, y_train, y_test: 划分后的数据集
        scaler: 数据标准化器
    """
    print(f"[INFO] 正在进行数据预处理...")
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=CONFIG["seed"], stratify=y
    )
    
    print(f"  - 训练集大小: {X_train.shape[0]}")
    print(f"  - 测试集大小: {X_test.shape[0]}")
    
    # 特征标准化 (使特征均值为0, 标准差为1)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)  # 在训练集上拟合
    X_test = scaler.transform(X_test)        # 在测试集上转换
    
    print(f"[INFO] 数据预处理完成!")
    
    return X_train, X_test, y_train, y_test, scaler


# ================== PyTorch数据集类 ==================

class TabularDataset(Dataset):
    """
    表格数据PyTorch数据集类
    
    继承自torch.utils.data.Dataset, 用于批量加载和迭代数据
    """
    
    def __init__(self, X: np.ndarray, y: np.ndarray):
        """
        初始化数据集
        
        Args:
            X: 特征矩阵 (numpy数组)
            y: 标签向量 (numpy数组)
        """
        # 转换为PyTorch张量
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
        self.len = len(y)
    
    def __len__(self):
        """返回数据集样本数量"""
        return self.len
    
    def __getitem__(self, idx: int):
        """
        获取单个样本
        
        Args:
            idx: 样本索引
            
        Returns:
            特征张量, 标签张量
        """
        return self.X[idx], self.y[idx]


# ================== 神经网络模型 ==================

class MLPClassifier(nn.Module):
    """
    多层感知机 (Multi-Layer Perceptron) 分类器
    
    这是一个基础的前馈神经网络, 包含:
    - 输入层
    - 隐藏层 (带ReLU激活和Dropout正则化)
    - 输出层 (带Softmax激活)
    
    参考: 深度学习后处理方法研究中使用的神经网络结构
    """
    
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        """
        初始化网络结构
        
        Args:
            input_dim: 输入特征维度
            hidden_dim: 隐藏层维度
            output_dim: 输出类别数
        """
        super(MLPClassifier, self).__init__()
        
        # 定义网络层: 输入层 -> 隐藏层 -> 输出层
        self.network = nn.Sequential(
            # 第一层线性变换
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),                    # ReLU激活函数
            nn.Dropout(0.3),              # Dropout正则化, 防止过拟合
            
            # 第二层线性变换
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            # 输出层
            nn.Linear(hidden_dim, output_dim)
        )
        
        # 权重初始化
        self._initialize_weights()
    
    def _initialize_weights(self):
        """
        使用Xavier初始化权重
        这有助于训练深层网络, 保持梯度稳定
        """
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播
        
        Args:
            x: 输入特征张量
            
        Returns:
            输出 logits (未归一化的类别分数)
        """
        return self.network(x)


# ================== 训练与评估函数 ==================

def train_epoch(model: nn.Module, dataloader: DataLoader, 
                criterion: nn.Module, optimizer: optim.Optimizer, device: str):
    """
    训练一个epoch (遍历整个训练集一次)
    
    Args:
        model: 神经网络模型
        dataloader: 训练数据加载器
        criterion: 损失函数
        optimizer: 优化器
        device: 计算设备 (cuda/cpu)
        
    Returns:
        average_loss: 平均训练损失
        accuracy: 训练准确率
    """
    model.train()  # 设置为训练模式 (启用Dropout等)
    total_loss = 0.0
    correct = 0
    total = 0
    
    for batch_X, batch_y in dataloader:
        # 移动数据到指定设备
        batch_X = batch_X.to(device)
        batch_y = batch_y.to(device)
        
        # 前向传播: 计算输出
        outputs = model(batch_X)
        
        # 计算损失
        loss = criterion(outputs, batch_y)
        
        # 反向传播: 清零梯度 -> 计算梯度 -> 更新参数
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # 累计损失
        total_loss += loss.item()
        
        # 计算准确率
        _, predicted = torch.max(outputs.data, 1)
        total += batch_y.size(0)
        correct += (predicted == batch_y).sum().item()
    
    average_loss = total_loss / len(dataloader)
    accuracy = correct / total
    
    return average_loss, accuracy


def evaluate(model: nn.Module, dataloader: DataLoader, 
             criterion: nn.Module, device: str):
    """
    在测试集上评估模型
    
    Args:
        model: 神经网络模型
        dataloader: 测试数据加载器
        criterion: 损失函数
        device: 计算设备
        
    Returns:
        average_loss: 平均测试损失
        accuracy: 测试准确率
        all_preds: 所有预测结果
        all_labels: 所有真实标签
    """
    model.eval()  # 设置为评估模式 (禁用Dropout)
    total_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():  # 禁用梯度计算, 节省内存
        for batch_X, batch_y in dataloader:
            batch_X = batch_X.to(device)
            batch_y = batch_y.to(device)
            
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
            
            # 收集预测结果用于后续分析
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(batch_y.cpu().numpy())
    
    average_loss = total_loss / len(dataloader)
    accuracy = correct / total
    
    return average_loss, accuracy, np.array(all_preds), np.array(all_labels)


def plot_training_history(train_losses: list, train_accs: list, 
                          test_losses: list, test_accs: list, save_path: str):
    """
    绘制训练历史曲线
    
    Args:
        train_losses: 训练损失列表
        train_accs: 训练准确率列表
        test_losses: 测试损失列表
        test_accs: 测试准确率列表
        save_path: 保存路径
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 绘制损失曲线
    axes[0].plot(train_losses, label='训练损失', color='blue', linewidth=2)
    axes[0].plot(test_losses, label='测试损失', color='red', linewidth=2)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss', fontsize=12)
    axes[0].set_title('训练与测试损失曲线', fontsize=14)
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # 绘制准确率曲线
    axes[1].plot(train_accs, label='训练准确率', color='blue', linewidth=2)
    axes[1].plot(test_accs, label='测试准确率', color='red', linewidth=2)
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Accuracy', fontsize=12)
    axes[1].set_title('训练与测试准确率曲线', fontsize=14)
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[INFO] 训练曲线已保存至: {save_path}")


# ================== 主函数 ==================

def main():
    """
    主函数: 完整演示机器学习流程
    
    流程:
    1. 配置与初始化
    2. 数据生成与预处理
    3. 创建数据加载器
    4. 构建神经网络模型
    5. 训练循环
    6. 模型评估与可视化
    """
    print("=" * 60)
    print("       机器学习基础示范代码 - 分类任务")
    print("=" * 60)
    
    # 步骤1: 设置随机种子, 保证结果可复现
    set_seed(CONFIG["seed"])
    
    # 确定计算设备
    device = CONFIG["device"]
    print(f"[INFO] 使用计算设备: {device}")
    
    # 步骤2: 生成合成数据
    X, y = generate_synthetic_data(
        num_samples=CONFIG["num_samples"],
        num_features=CONFIG["num_features"],
        num_classes=CONFIG["num_classes"]
    )
    
    # 步骤3: 数据预处理
    X_train, X_test, y_train, y_test, scaler = preprocess_data(
        X, y, CONFIG["test_size"]
    )
    
    # 步骤4: 创建PyTorch数据集和数据加载器
    train_dataset = TabularDataset(X_train, y_train)
    test_dataset = TabularDataset(X_test, y_test)
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=CONFIG["batch_size"], 
        shuffle=True,
        num_workers=0
    )
    test_loader = DataLoader(
        test_dataset, 
        batch_size=CONFIG["batch_size"], 
        shuffle=False,
        num_workers=0
    )
    
    print(f"[INFO] 数据加载器创建完成")
    print(f"  - 训练批次数: {len(train_loader)}")
    print(f"  - 测试批次数: {len(test_loader)}")
    
    # 步骤5: 构建神经网络模型
    model = MLPClassifier(
        input_dim=CONFIG["num_features"],
        hidden_dim=CONFIG["hidden_dim"],
        output_dim=CONFIG["num_classes"]
    )
    model = model.to(device)
    
    print(f"[INFO] 模型结构:")
    print(model)
    
    # 定义损失函数 (交叉熵损失, 适用于分类任务)
    criterion = nn.CrossEntropyLoss()
    
    # 定义优化器 (Adam优化器, 常用且效果好)
    optimizer = optim.Adam(
        model.parameters(), 
        lr=CONFIG["learning_rate"],
        weight_decay=1e-4  # L2正则化, 防止过拟合
    )
    
    # 学习率调度器 (随着训练进行逐渐降低学习率)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.5)
    
    # 步骤6: 训练循环
    print("\n" + "=" * 60)
    print("开始训练...")
    print("=" * 60)
    
    train_losses, train_accs = [], []
    test_losses, test_accs = [], []
    best_test_acc = 0.0
    
    for epoch in range(CONFIG["num_epochs"]):
        # 训练一个epoch
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, device
        )
        
        # 在测试集上评估
        test_loss, test_acc, _, _ = evaluate(
            model, test_loader, criterion, device
        )
        
        # 更新学习率
        scheduler.step()
        
        # 记录历史
        train_losses.append(train_loss)
        train_accs.append(train_acc)
        test_losses.append(test_loss)
        test_accs.append(test_acc)
        
        # 保存最佳模型
        if test_acc > best_test_acc:
            best_test_acc = test_acc
            torch.save(model.state_dict(), 'best_model.pth')
        
        # 每10个epoch打印一次进度
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1:3d}/{CONFIG['num_epochs']}] | "
                  f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | "
                  f"Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.4f}")
    
    print("\n" + "=" * 60)
    print(f"训练完成! 最佳测试准确率: {best_test_acc:.4f}")
    print("=" * 60)
    
    # 步骤7: 加载最佳模型并进行最终评估
    model.load_state_dict(torch.load('best_model.pth'))
    _, final_acc, predictions, labels = evaluate(
        model, test_loader, criterion, device
    )
    
    # 打印详细评估报告
    print("\n[模型评估报告]")
    print("-" * 40)
    print(f"最终测试准确率: {final_acc:.4f}")
    print("\n分类报告:")
    print(classification_report(labels, predictions, target_names=['类别0', '类别1']))
    
    print("混淆矩阵:")
    cm = confusion_matrix(labels, predictions)
    print(cm)
    
    # 步骤8: 可视化训练历史
    plot_training_history(
        train_losses, train_accs, 
        test_losses, test_accs,
        'training_history.png'
    )
    
    # 绘制混淆矩阵
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('混淆矩阵', fontsize=14)
    plt.colorbar()
    tick_marks = np.arange(CONFIG["num_classes"])
    plt.xticks(tick_marks, ['类别0', '类别1'])
    plt.yticks(tick_marks, ['类别0', '类别1'])
    
    # 在混淆矩阵上显示数值
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    
    plt.ylabel('真实标签', fontsize=12)
    plt.xlabel('预测标签', fontsize=12)
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=150)
    plt.close()
    print("[INFO] 混淆矩阵已保存至: confusion_matrix.png")
    
    print("\n" + "=" * 60)
    print("机器学习流程演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
