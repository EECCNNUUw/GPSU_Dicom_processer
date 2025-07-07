# 医疗DICOM文件后处理工具

## 简介

本项目是一个功能全面、可扩展的DICOM后处理Python程序，专为医疗设备公司的DICOM文件处理需求设计。程序支持多种厂商的DICOM文件自适应处理，提供了丰富的图像处理功能，包括窗宽窗位调整、通道合并和灰白质分割等。框架采用模块化设计，易于扩展新的功能和支持新的医疗设备厂商。

## 功能特点

1. **多厂商DICOM自适应**：支持西门子、GE、飞利浦和联影等主流医疗设备厂商的DICOM文件（东软待添加）。
2. **DICOM字段识别**：自动提取DICOM文件中的关键参数，生成包含参数名称、有效范围和参数值的临床协议。
3. **灵活的输出格式**：支持将协议信息导出为JSON或XML格式。
4. **窗宽窗位调整**：提供专业的医学图像处理功能，优化图像显示效果。
5. **通道合并操作**：支持多模态医学图像的通道融合处理。
6. **灰白质分割**：针对脑部DICOM图像实现简单有效的灰白质分割（功能待测试）。
7. **高度可扩展**：通过清晰的接口设计，方便添加新的DICOM适配器和扩展功能。

## 安装要求

- Python 3.7+
- 主要依赖库：
  - pydicom：用于DICOM文件解析
  - numpy：用于图像处理
  - matplotlib：用于结果可视化
  - scipy：用于科学计算
  - scikit-image：用于图像分割和处理

可以使用以下命令安装所需依赖：
pip install pydicom numpy matplotlib scipy scikit-image
## 使用示例

以下是一个基本的使用流程示例：
from dicom_processor import DicomProcessor

# 创建DICOM处理器实例
processor = DicomProcessor()

# 加载DICOM文件
if processor.load_dicom("example.dcm"):
    # 获取协议信息（JSON格式）
    print("Protocol Information (JSON):")
    print(processor.get_protocol_info("json"))
    
    # 调整窗宽窗位（WW=400, WL=40）
    windowed_image = processor.adjust_window(400, 40)
    
    # 执行灰白质分割（待测试）
    gm_mask, wm_mask = processor.segment_gray_white_matter()
    
    # 可视化处理结果
    processor.visualize_results()
    
    # 扩展示例：注册新的适配器
    new_adapter = CustomDicomAdapter("NEW_MANUFACTURER")
    processor.register_adapter(new_adapter)
else:
    print("Failed to load DICOM file.")
## 代码结构

项目主要包含以下几个核心组件：

1. **DicomAdapter**：抽象基类，为不同厂商的DICOM文件提供统一接口。
2. **厂商适配器实现**：针对各主流医疗设备厂商的具体适配器实现（如SiemensDicomAdapter、GE_DicomAdapter等）。
3. **DicomProcessor**：核心处理类，负责协调各种处理功能，包括加载DICOM文件、协议提取、图像处理等。
4. **扩展接口**：提供了简单的扩展机制，方便添加新的适配器和功能。

## 扩展方法

### 添加新的DICOM适配器

如果需要支持新的医疗设备厂商，只需创建一个新的适配器类，继承自`DicomAdapter`，并实现相应的抽象方法：
class NewManufacturerDicomAdapter(DicomAdapter):
    """新厂商DICOM文件适配器"""
    
    def is_compatible(self, dicom_data: pydicom.FileDataset) -> bool:
        return "NEW_MANUFACTURER" in str(dicom_data.Manufacturer).upper()
    
    def get_protocol_info(self, dicom_data: pydicom.FileDataset) -> Dict[str, Any]:
        # 实现特定于该厂商的协议信息提取逻辑
        protocol = {}
        protocol["Manufacturer"] = "New Manufacturer"
        # 添加其他特定参数...
        return protocol
    
    def get_pixel_data(self, dicom_data: pydicom.FileDataset) -> np.ndarray:
        # 实现特定于该厂商的像素数据处理逻辑
        pixel_data = dicom_data.pixel_array
        # 可能需要的特定处理...
        return pixel_data

# 注册新适配器
processor.register_adapter(NewManufacturerDicomAdapter())
### 添加新的处理功能

要添加新的处理功能，只需在`DicomProcessor`类中添加新的方法即可：
class DicomProcessor:
    # ... 现有代码 ...
    
    def new_processing_function(self, param1, param2):
        """新的处理功能示例"""
        # 实现新功能的处理逻辑
        result = self.pixel_data * param1 + param2
        return result


## 联系信息

如果你有任何问题或建议，请通过以下方式联系我：

- 邮箱：1849668628@qq.com
- GitHub：https://github.com/EECCNNUUw/GPSU_Dicom_processer
    
