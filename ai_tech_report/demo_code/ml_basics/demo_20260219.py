#!/usr/bin/env python3
"""
AI技术基础示例代码

本示例展示了一个简单的机器学习分类任务，
使用scikit-learn构建一个分类器。

作者: AI-Generated
日期: 2026-02-13
"""

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.datasets import make_classification
import warnings
warnings.filterwarnings('ignore')

def main():
    """主函数：演示机器学习分类流程"""
    print("=" * 50)
    print("AI机器学习分类示例")
    print("=" * 50)
    
    # 1. 生成模拟数据集
    print("步骤1: 生成模拟数据集...")
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        n_classes=2,
        random_state=42
    )
    print("数据集形状: X=" + str(X.shape) + ", y=" + str(y.shape))
    
    # 2. 划分训练集和测试集
    print("步骤2: 划分训练集和测试集...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    print("训练集: " + str(X_train.shape[0]) + " 样本")
    print("测试集: " + str(X_test.shape[0]) + " 样本")
    
    # 3. 创建和训练模型
    print("步骤3: 创建和训练随机森林模型...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    print("模型训练完成!")
    
    # 4. 模型预测
    print("步骤4: 进行预测...")
    y_pred = model.predict(X_test)
    
    # 5. 评估模型
    print("步骤5: 模型评估...")
    accuracy = accuracy_score(y_test, y_pred)
    accuracy_percent = accuracy * 100
    acc_str = "%.4f" % accuracy
    acc_percent_str = "%.2f" % accuracy_percent
    print("准确率: " + acc_str + " (" + acc_percent_str + "%)")
    
    print("分类报告:")
    print(classification_report(y_test, y_pred, target_names=['类别0', '类别1']))
    
    # 6. 特征重要性分析
    print("步骤6: 特征重要性分析...")
    feature_importance = model.feature_importances_
    top_5_indices = np.argsort(feature_importance)[-5:][::-1]
    
    print("Top 5 重要特征:")
    for idx_enum, idx in enumerate(top_5_indices, 1):
        imp_str = "%.4f" % feature_importance[idx]
        print("  " + str(idx_enum) + ". 特征 " + str(idx) + ": " + imp_str)
    
    print("=" * 50)
    print("示例运行完成!")
    print("=" * 50)

if __name__ == "__main__":
    main()
