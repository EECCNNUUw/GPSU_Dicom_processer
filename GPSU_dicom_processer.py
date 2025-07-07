import os
import json
import pydicom
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage import filters, segmentation, measure

class DicomAdapter(ABC):
    """DICOM适配器抽象基类，为不同厂商的DICOM文件提供统一接口"""
    
    @abstractmethod
    def is_compatible(self, dicom_data: pydicom.FileDataset) -> bool:
        """检查该适配器是否适用于给定的DICOM数据"""
        pass
    
    @abstractmethod
    def get_protocol_info(self, dicom_data: pydicom.FileDataset) -> Dict[str, Any]:
        """提取DICOM中的协议信息"""
        pass
    
    @abstractmethod
    def get_pixel_data(self, dicom_data: pydicom.FileDataset) -> np.ndarray:
        """获取并处理像素数据"""
        pass


class SiemensDicomAdapter(DicomAdapter):
    """西门子DICOM文件适配器"""
    
    def is_compatible(self, dicom_data: pydicom.FileDataset) -> bool:
        return "SIEMENS" in str(dicom_data.Manufacturer).upper()
    
    def get_protocol_info(self, dicom_data: pydicom.FileDataset) -> Dict[str, Any]:
        protocol = {}
        # 提取西门子的协议参数
        protocol["Manufacturer"] = "Siemens"
        protocol["SeriesDescription"] = dicom_data.get("SeriesDescription", "")
        protocol["SequenceName"] = dicom_data.get("SequenceName", "")
        
        # 提取常用参数
        protocol["SliceThickness"] = {"value": dicom_data.get("SliceThickness", ""), "valid_range": "0.1-10 mm"}
        protocol["EchoTime"] = {"value": dicom_data.get("EchoTime", ""), "valid_range": "0-500 ms"}
        protocol["RepetitionTime"] = {"value": dicom_data.get("RepetitionTime", ""), "valid_range": "0-5000 ms"}
        
        return protocol
    
    def get_pixel_data(self, dicom_data: pydicom.FileDataset) -> np.ndarray:
        # 西门子特定的像素数据处理
        pixel_data = dicom_data.pixel_array
        if hasattr(dicom_data, 'RescaleSlope') and hasattr(dicom_data, 'RescaleIntercept'):
            pixel_data = pixel_data * dicom_data.RescaleSlope + dicom_data.RescaleIntercept
        return pixel_data


class GE_DicomAdapter(DicomAdapter):
    """GE DICOM文件适配器"""
    
    def is_compatible(self, dicom_data: pydicom.FileDataset) -> bool:
        return "GE MEDICAL SYSTEMS" in str(dicom_data.Manufacturer).upper()
    
    def get_protocol_info(self, dicom_data: pydicom.FileDataset) -> Dict[str, Any]:
        protocol = {}
        # 提取GE的协议参数
        protocol["Manufacturer"] = "GE"
        protocol["SeriesDescription"] = dicom_data.get("SeriesDescription", "")
        protocol["ProtocolName"] = dicom_data.get("ProtocolName", "")
        
        # 提取常用参数
        protocol["SliceThickness"] = {"value": dicom_data.get("SliceThickness", ""), "valid_range": "0.1-10 mm"}
        protocol["EchoTime"] = {"value": dicom_data.get("EchoTime", ""), "valid_range": "0-500 ms"}
        protocol["RepetitionTime"] = {"value": dicom_data.get("RepetitionTime", ""), "valid_range": "0-5000 ms"}
        
        return protocol
    
    def get_pixel_data(self, dicom_data: pydicom.FileDataset) -> np.ndarray:
        # GE特定的像素数据处理
        pixel_data = dicom_data.pixel_array
        if hasattr(dicom_data, 'RescaleSlope') and hasattr(dicom_data, 'RescaleIntercept'):
            pixel_data = pixel_data * dicom_data.RescaleSlope + dicom_data.RescaleIntercept
        return pixel_data


class PhilipsDicomAdapter(DicomAdapter):
    """飞利浦DICOM文件适配器"""
    
    def is_compatible(self, dicom_data: pydicom.FileDataset) -> bool:
        return "PHILIPS" in str(dicom_data.Manufacturer).upper()
    
    def get_protocol_info(self, dicom_data: pydicom.FileDataset) -> Dict[str, Any]:
        protocol = {}
        # 提取飞利浦的协议参数
        protocol["Manufacturer"] = "Philips"
        protocol["SeriesDescription"] = dicom_data.get("SeriesDescription", "")
        protocol["ProtocolName"] = dicom_data.get("ProtocolName", "")
        
        # 提取常用参数
        protocol["SliceThickness"] = {"value": dicom_data.get("SliceThickness", ""), "valid_range": "0.1-10 mm"}
        protocol["EchoTime"] = {"value": dicom_data.get("EchoTime", ""), "valid_range": "0-500 ms"}
        protocol["RepetitionTime"] = {"value": dicom_data.get("RepetitionTime", ""), "valid_range": "0-5000 ms"}
        
        return protocol
    
    def get_pixel_data(self, dicom_data: pydicom.FileDataset) -> np.ndarray:
        # 飞利浦特定的像素数据处理
        pixel_data = dicom_data.pixel_array
        if hasattr(dicom_data, 'RescaleSlope') and hasattr(dicom_data, 'RescaleIntercept'):
            pixel_data = pixel_data * dicom_data.RescaleSlope + dicom_data.RescaleIntercept
        return pixel_data


class UnitedImagingDicomAdapter(DicomAdapter):
    """联影DICOM文件适配器"""
    
    def is_compatible(self, dicom_data: pydicom.FileDataset) -> bool:
        return "UNITED IMAGING" in str(dicom_data.Manufacturer).upper()
    
    def get_protocol_info(self, dicom_data: pydicom.FileDataset) -> Dict[str, Any]:
        protocol = {}
        # 提取特定的协议参数
        protocol["Manufacturer"] = "United Imaging"
        protocol["SeriesDescription"] = dicom_data.get("SeriesDescription", "")
        protocol["ProtocolName"] = dicom_data.get("ProtocolName", "")
        
        # 提取常用参数
        protocol["SliceThickness"] = {"value": dicom_data.get("SliceThickness", ""), "valid_range": "0.1-10 mm"}
        protocol["EchoTime"] = {"value": dicom_data.get("EchoTime", ""), "valid_range": "0-500 ms"}
        protocol["RepetitionTime"] = {"value": dicom_data.get("RepetitionTime", ""), "valid_range": "0-5000 ms"}
        
        return protocol
    
    def get_pixel_data(self, dicom_data: pydicom.FileDataset) -> np.ndarray:
        # 联影特定的像素数据处理
        pixel_data = dicom_data.pixel_array
        if hasattr(dicom_data, 'RescaleSlope') and hasattr(dicom_data, 'RescaleIntercept'):
            pixel_data = pixel_data * dicom_data.RescaleSlope + dicom_data.RescaleIntercept
        return pixel_data


class DicomProcessor:
    """DICOM文件处理器，负责协调各种处理功能"""
    
    def __init__(self):
        # 注册所有已知的DICOM适配器
        self.adapters = [
            SiemensDicomAdapter(),
            GE_DicomAdapter(),
            PhilipsDicomAdapter(),
            UnitedImagingDicomAdapter()
        ]
        self.dicom_data = None
        self.adapter = None
        self.pixel_data = None
        self.protocol_info = None
    
    def load_dicom(self, file_path: str) -> bool:
        """加载DICOM文件"""
        try:
            self.dicom_data = pydicom.dcmread(file_path)
            self.adapter = self._find_compatible_adapter()
            if self.adapter:
                self.pixel_data = self.adapter.get_pixel_data(self.dicom_data)
                self.protocol_info = self.adapter.get_protocol_info(self.dicom_data)
                return True
            else:
                print("Error: No compatible DICOM adapter found for this file.")
                return False
        except Exception as e:
            print(f"Error loading DICOM file: {e}")
            return False
    
    def _find_compatible_adapter(self) -> Optional[DicomAdapter]:
        """查找兼容的DICOM适配器"""
        for adapter in self.adapters:
            if adapter.is_compatible(self.dicom_data):
                return adapter
        return None
    
    def get_protocol_info(self, output_format: str = "json") -> str:
        """获取协议信息，支持JSON或XML格式输出"""
        if not self.protocol_info:
            return "Error: Protocol information not available. Load a DICOM file first."
        
        if output_format.lower() == "json":
            return json.dumps(self.protocol_info, indent=4)
        elif output_format.lower() == "xml":
            # 简单的XML转换，实际应用中可能需要更复杂的转换
            xml = '<?xml version="1.0" encoding="UTF-8"?>\n<Protocol>\n'
            for key, value in self.protocol_info.items():
                if isinstance(value, dict):
                    xml += f'  <{key}>\n'
                    for sub_key, sub_value in value.items():
                        xml += f'    <{sub_key}>{sub_value}</{sub_key}>\n'
                    xml += f'  </{key}>\n'
                else:
                    xml += f'  <{key}>{value}</{key}>\n'
            xml += '</Protocol>'
            return xml
        else:
            return "Error: Unsupported output format. Use 'json' or 'xml'."
    
    def adjust_window(self, window_width: int, window_level: int) -> np.ndarray:
        """调整窗宽窗位"""
        if self.pixel_data is None:
            print("Error: No pixel data available. Load a DICOM file first.")
            return None
        
        min_value = window_level - window_width // 2
        max_value = window_level + window_width // 2
        
        # 窗口调整
        windowed_data = np.copy(self.pixel_data)
        windowed_data[windowed_data < min_value] = min_value
        windowed_data[windowed_data > max_value] = max_value
        
        # 归一化到0-255
        windowed_data = ((windowed_data - min_value) / window_width * 255).astype(np.uint8)
        
        return windowed_data
    
    def merge_channels(self, dicom_processors: List["DicomProcessor"], weights: List[float] = None) -> np.ndarray:
        """合并多个DICOM图像通道"""
        if self.pixel_data is None:
            print("Error: No pixel data available. Load a DICOM file first.")
            return None
        
        # 确保所有图像尺寸相同
        target_shape = self.pixel_data.shape
        channels = [self.pixel_data]
        
        for processor in dicom_processors:
            if processor.pixel_data.shape != target_shape:
                print("Error: All DICOM images must have the same dimensions for channel merging.")
                return None
            channels.append(processor.pixel_data)
        
        # 设置默认权重
        if weights is None:
            weights = [1.0 / len(channels)] * len(channels)
        else:
            if len(weights) != len(channels):
                print("Error: Number of weights must match number of channels.")
                return None
            # 归一化权重
            weight_sum = sum(weights)
            weights = [w / weight_sum for w in weights]
        
        # 合并通道
        merged = np.zeros_like(self.pixel_data, dtype=np.float32)
        for i, channel in enumerate(channels):
            merged += channel * weights[i]
        
        return merged.astype(self.pixel_data.dtype)
    
    def segment_gray_white_matter(self) -> Tuple[np.ndarray, np.ndarray]:
        """简单的灰白质分割（脑功能下）"""
        if self.pixel_data is None:
            print("Error: No pixel data available. Load a DICOM file first.")
            return None, None
        
        # 假设已经进行了脑部提取，这里简化处理
        # 实际应用中可能需要先进行颅骨剥离等预处理
        
        # 使用Otsu方法进行初步分割
        pixel_data = self.pixel_data.astype(np.float32)
        blurred = ndimage.gaussian_filter(pixel_data, sigma=1)
        
        # 获取两个阈值来区分脑脊液(CSF)、灰质(GM)和白质(WM)
        thresholds = filters.threshold_multiotsu(blurred, classes=3)
        
        # 创建分割掩码
        csf_mask = blurred <= thresholds[0]
        gm_mask = (blurred > thresholds[0]) & (blurred <= thresholds[1])
        wm_mask = blurred > thresholds[1]
        
        # 形态学操作优化分割结果
        gm_mask = ndimage.binary_closing(gm_mask, structure=np.ones((3, 3)))
        wm_mask = ndimage.binary_closing(wm_mask, structure=np.ones((3, 3)))
        
        return gm_mask, wm_mask
    
    def register_adapter(self, adapter: DicomAdapter) -> None:
        """注册新的DICOM适配器，用于扩展支持新的厂商"""
        self.adapters.append(adapter)
    
    def visualize_results(self, window_width: int = 400, window_level: int = 40, 
                          show_original: bool = True, show_windowed: bool = True,
                          show_segmentation: bool = True) -> None:
        """可视化处理结果"""
        if self.pixel_data is None:
            print("Error: No pixel data available. Load a DICOM file first.")
            return
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes = axes.flatten()
        
        # 显示原图
        if show_original:
            axes[0].imshow(self.pixel_data, cmap=plt.cm.gray)
            axes[0].set_title('Original Image')
            axes[0].axis('off')
        
        # 显示窗宽窗位调整后的图像
        if show_windowed:
            windowed = self.adjust_window(window_width, window_level)
            axes[1].imshow(windowed, cmap=plt.cm.gray)
            axes[1].set_title(f'Windowed (WW={window_width}, WL={window_level})')
            axes[1].axis('off')
        
        # 显示分割结果
        if show_segmentation:
            gm_mask, wm_mask = self.segment_gray_white_matter()
            
            # 创建RGB图像用于显示分割结果
            rgb_image = np.zeros((self.pixel_data.shape[0], self.pixel_data.shape[1], 3))
            windowed = self.adjust_window(window_width, window_level)
            rgb_image[:, :, 0] = windowed / 255.0  # 红色通道显示原始图像
            rgb_image[:, :, 1] = gm_mask * 0.5     # 绿色通道显示灰质
            rgb_image[:, :, 2] = wm_mask * 0.5     # 蓝色通道显示白质
            
            axes[2].imshow(rgb_image)
            axes[2].set_title('Gray & White Matter Segmentation')
            axes[2].axis('off')
        
        plt.tight_layout()
        plt.show()


# 扩展接口示例
class CustomDicomAdapter(DicomAdapter):
    """自定义DICOM适配器示例，用于扩展支持新的厂商"""
    
    def __init__(self, manufacturer_name: str):
        self.manufacturer_name = manufacturer_name
    
    def is_compatible(self, dicom_data: pydicom.FileDataset) -> bool:
        return self.manufacturer_name in str(dicom_data.Manufacturer).upper()
    
    def get_protocol_info(self, dicom_data: pydicom.FileDataset) -> Dict[str, Any]:
        protocol = {}
        protocol["Manufacturer"] = self.manufacturer_name
        protocol["SeriesDescription"] = dicom_data.get("SeriesDescription", "")
        
        # 添加特定于该厂商的参数提取逻辑
        protocol["CustomParameter"] = {"value": "CustomValue", "valid_range": "CustomRange"}
        
        return protocol
    
    def get_pixel_data(self, dicom_data: pydicom.FileDataset) -> np.ndarray:
        # 自定义像素数据处理逻辑
        pixel_data = dicom_data.pixel_array
        if hasattr(dicom_data, 'RescaleSlope') and hasattr(dicom_data, 'RescaleIntercept'):
            pixel_data = pixel_data * dicom_data.RescaleSlope + dicom_data.RescaleIntercept
        return pixel_data


if __name__ == "__main__":
    # 使用示例
    processor = DicomProcessor()
    
    # 加载DICOM文件
    if processor.load_dicom("example.dcm"):
        # 获取协议信息
        print("Protocol Information (JSON):")
        print(processor.get_protocol_info("json"))
        
        # 调整窗宽窗位
        windowed_image = processor.adjust_window(400, 40)
        
        # 灰白质分割
        gm_mask, wm_mask = processor.segment_gray_white_matter()
        
        # 可视化结果
        processor.visualize_results()
        
        # 扩展示例：注册新的适配器
        new_adapter = CustomDicomAdapter("NEW_MANUFACTURER")
        processor.register_adapter(new_adapter)
    else:
        print("Failed to load DICOM file.")    
