import os
import json
import pydicom
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from scipy import ndimage
from skimage import filters, segmentation, measure
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import logging

# 配置日志系统
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
        protocol["Manufacturer"] = "Siemens"
        protocol["SeriesDescription"] = dicom_data.get("SeriesDescription", "")
        protocol["SequenceName"] = dicom_data.get("SequenceName", "")
        
        protocol["SliceThickness"] = {"value": dicom_data.get("SliceThickness", ""), "valid_range": "0.1-10 mm"}
        protocol["EchoTime"] = {"value": dicom_data.get("EchoTime", ""), "valid_range": "0-500 ms"}
        protocol["RepetitionTime"] = {"value": dicom_data.get("RepetitionTime", ""), "valid_range": "0-5000 ms"}
        
        return protocol
    
    def get_pixel_data(self, dicom_data: pydicom.FileDataset) -> np.ndarray:
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
        protocol["Manufacturer"] = "GE"
        protocol["SeriesDescription"] = dicom_data.get("SeriesDescription", "")
        protocol["ProtocolName"] = dicom_data.get("ProtocolName", "")
        
        protocol["SliceThickness"] = {"value": dicom_data.get("SliceThickness", ""), "valid_range": "0.1-10 mm"}
        protocol["EchoTime"] = {"value": dicom_data.get("EchoTime", ""), "valid_range": "0-500 ms"}
        protocol["RepetitionTime"] = {"value": dicom_data.get("RepetitionTime", ""), "valid_range": "0-5000 ms"}
        
        return protocol
    
    def get_pixel_data(self, dicom_data: pydicom.FileDataset) -> np.ndarray:
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
        protocol["Manufacturer"] = "Philips"
        protocol["SeriesDescription"] = dicom_data.get("SeriesDescription", "")
        protocol["ProtocolName"] = dicom_data.get("ProtocolName", "")
        
        protocol["SliceThickness"] = {"value": dicom_data.get("SliceThickness", ""), "valid_range": "0.1-10 mm"}
        protocol["EchoTime"] = {"value": dicom_data.get("EchoTime", ""), "valid_range": "0-500 ms"}
        protocol["RepetitionTime"] = {"value": dicom_data.get("RepetitionTime", ""), "valid_range": "0-5000 ms"}
        
        return protocol
    
    def get_pixel_data(self, dicom_data: pydicom.FileDataset) -> np.ndarray:
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
        protocol["Manufacturer"] = "United Imaging"
        protocol["SeriesDescription"] = dicom_data.get("SeriesDescription", "")
        protocol["ProtocolName"] = dicom_data.get("ProtocolName", "")
        
        protocol["SliceThickness"] = {"value": dicom_data.get("SliceThickness", ""), "valid_range": "0.1-10 mm"}
        protocol["EchoTime"] = {"value": dicom_data.get("EchoTime", ""), "valid_range": "0-500 ms"}
        protocol["RepetitionTime"] = {"value": dicom_data.get("RepetitionTime", ""), "valid_range": "0-5000 ms"}
        
        return protocol
    
    def get_pixel_data(self, dicom_data: pydicom.FileDataset) -> np.ndarray:
        pixel_data = dicom_data.pixel_array
        if hasattr(dicom_data, 'RescaleSlope') and hasattr(dicom_data, 'RescaleIntercept'):
            pixel_data = pixel_data * dicom_data.RescaleSlope + dicom_data.RescaleIntercept
        return pixel_data


class DicomProcessor:
    """DICOM文件处理器，负责协调各种处理功能"""
    
    def __init__(self, debug_mode: bool = False):
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
        self.debug_mode = debug_mode
        
        if self.debug_mode:
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode is enabled")
        else:
            logger.setLevel(logging.INFO)
    
    def load_dicom(self, file_path: str) -> bool:
        """加载DICOM文件"""
        try:
            if self.debug_mode:
                logger.debug(f"Loading DICOM file: {file_path}")
                
            self.dicom_data = pydicom.dcmread(file_path)
            self.adapter = self._find_compatible_adapter()
            
            if self.adapter:
                self.pixel_data = self.adapter.get_pixel_data(self.dicom_data)
                self.protocol_info = self.adapter.get_protocol_info(self.dicom_data)
                
                if self.debug_mode:
                    logger.debug(f"Successfully loaded DICOM file using {self.adapter.__class__.__name__}")
                    logger.debug(f"Image shape: {self.pixel_data.shape}")
                    logger.debug(f"Protocol information: {self.protocol_info}")
                    
                return True
            else:
                logger.error("No compatible DICOM adapter found for this file.")
                return False
        except Exception as e:
            logger.error(f"Error loading DICOM file: {e}")
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
            logger.error("No pixel data available. Load a DICOM file first.")
            return None
        
        if self.debug_mode:
            logger.debug(f"Adjusting window: Width={window_width}, Level={window_level}")
        
        min_value = window_level - window_width // 2
        max_value = window_level + window_width // 2
        
        windowed_data = np.copy(self.pixel_data)
        windowed_data[windowed_data < min_value] = min_value
        windowed_data[windowed_data > max_value] = max_value
        
        windowed_data = ((windowed_data - min_value) / window_width * 255).astype(np.uint8)
        
        return windowed_data
    
    def merge_channels(self, dicom_processors: List["DicomProcessor"], weights: List[float] = None) -> np.ndarray:
        """合并多个DICOM图像通道"""
        if self.pixel_data is None:
            logger.error("No pixel data available. Load a DICOM file first.")
            return None
        
        if self.debug_mode:
            logger.debug(f"Merging {len(dicom_processors) + 1} channels")
        
        target_shape = self.pixel_data.shape
        channels = [self.pixel_data]
        
        for processor in dicom_processors:
            if processor.pixel_data.shape != target_shape:
                logger.error("All DICOM images must have the same dimensions for channel merging.")
                return None
            channels.append(processor.pixel_data)
        
        if weights is None:
            weights = [1.0 / len(channels)] * len(channels)
        else:
            if len(weights) != len(channels):
                logger.error("Number of weights must match number of channels.")
                return None
            weight_sum = sum(weights)
            weights = [w / weight_sum for w in weights]
        
        merged = np.zeros_like(self.pixel_data, dtype=np.float32)
        for i, channel in enumerate(channels):
            merged += channel * weights[i]
        
        return merged.astype(self.pixel_data.dtype)
    
    def segment_gray_white_matter(self) -> Tuple[np.ndarray, np.ndarray]:
        """简单的灰白质分割（脑功能下）"""
        if self.pixel_data is None:
            logger.error("No pixel data available. Load a DICOM file first.")
            return None, None
        
        if self.debug_mode:
            logger.debug("Performing gray and white matter segmentation")
        
        pixel_data = self.pixel_data.astype(np.float32)
        blurred = ndimage.gaussian_filter(pixel_data, sigma=1)
        
        thresholds = filters.threshold_multiotsu(blurred, classes=3)
        
        csf_mask = blurred <= thresholds[0]
        gm_mask = (blurred > thresholds[0]) & (blurred <= thresholds[1])
        wm_mask = blurred > thresholds[1]
        
        gm_mask = ndimage.binary_closing(gm_mask, structure=np.ones((3, 3)))
        wm_mask = ndimage.binary_closing(wm_mask, structure=np.ones((3, 3)))
        
        return gm_mask, wm_mask
    
    def register_adapter(self, adapter: DicomAdapter) -> None:
        """注册新的DICOM适配器，用于扩展支持新的厂商"""
        self.adapters.append(adapter)
        if self.debug_mode:
            logger.debug(f"New adapter registered: {adapter.__class__.__name__}")


class DicomGUI:
    """DICOM处理GUI界面"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("医疗DICOM文件后处理工具")
        self.root.geometry("1000x800")
        
        self.processor = DicomProcessor(debug_mode=False)
        self.current_file = None
        
        self._create_widgets()
        self._create_layout()
        
    def _create_widgets(self):
        # 文件选择区域
        self.file_frame = ttk.LabelFrame(self.root, text="文件操作")
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(self.file_frame, textvariable=self.file_path_var, width=50)
        self.browse_button = ttk.Button(self.file_frame, text="浏览...", command=self._browse_file)
        self.load_button = ttk.Button(self.file_frame, text="加载DICOM", command=self._load_dicom)
        
        # 调试开关
        self.debug_var = tk.BooleanVar()
        self.debug_checkbox = ttk.Checkbutton(self.file_frame, text="调试模式", 
                                            variable=self.debug_var, command=self._toggle_debug)
        
        # 图像处理控制区域
        self.process_frame = ttk.LabelFrame(self.root, text="图像处理")
        
        # 窗宽窗位控制
        self.window_frame = ttk.LabelFrame(self.process_frame, text="窗宽窗位")
        self.ww_var = tk.IntVar(value=400)
        self.wl_var = tk.IntVar(value=40)
        
        ttk.Label(self.window_frame, text="窗宽:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(self.window_frame, textvariable=self.ww_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.window_frame, text="窗位:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(self.window_frame, textvariable=self.wl_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        self.window_button = ttk.Button(self.window_frame, text="应用窗宽窗位", command=self._apply_window)
        
        # 分割控制
        self.segment_frame = ttk.LabelFrame(self.process_frame, text="灰白质分割")
        self.segment_button = ttk.Button(self.segment_frame, text="执行分割", command=self._segment)
        
        # 协议信息区域
        self.protocol_frame = ttk.LabelFrame(self.root, text="协议信息")
        self.protocol_text = tk.Text(self.protocol_frame, height=15, width=60)
        self.protocol_scroll = ttk.Scrollbar(self.protocol_frame, orient=tk.VERTICAL, command=self.protocol_text.yview)
        self.protocol_text.configure(yscrollcommand=self.protocol_scroll.set)
        
        # 显示格式选择
        self.format_var = tk.StringVar(value="json")
        self.json_radio = ttk.Radiobutton(self.protocol_frame, text="JSON", variable=self.format_var, value="json")
        self.xml_radio = ttk.Radiobutton(self.protocol_frame, text="XML", variable=self.format_var, value="xml")
        self.show_protocol_button = ttk.Button(self.protocol_frame, text="显示协议信息", command=self._show_protocol)
        
        # 图像显示区域
        self.display_frame = ttk.LabelFrame(self.root, text="图像显示")
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.display_frame)
        self.canvas.draw()
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
    
    def _create_layout(self):
        # 布局文件选择区域
        self.file_frame.pack(fill=tk.X, padx=10, pady=10)
        self.file_path_entry.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.browse_button.grid(row=0, column=1, padx=5, pady=5)
        self.load_button.grid(row=0, column=2, padx=5, pady=5)
        self.debug_checkbox.grid(row=0, column=3, padx=20, pady=5)
        
        # 布局图像处理控制区域
        self.process_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.window_frame.pack(side=tk.LEFT, padx=10, pady=5)
        self.window_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        
        self.segment_frame.pack(side=tk.LEFT, padx=10, pady=5)
        self.segment_button.pack(padx=5, pady=10)
        
        # 布局协议信息区域
        self.protocol_frame.pack(fill=tk.X, padx=10, pady=5)
        self.protocol_text.grid(row=0, column=0, rowspan=3, padx=5, pady=5, sticky=tk.NSEW)
        self.protocol_scroll.grid(row=0, column=1, rowspan=3, sticky=tk.NS)
        self.json_radio.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.xml_radio.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.show_protocol_button.grid(row=2, column=2, padx=5, pady=5)
        
        # 布局图像显示区域
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 布局状态栏
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")])
        if file_path:
            self.file_path_var.set(file_path)
            self.current_file = file_path
    
    def _load_dicom(self):
        if not self.current_file:
            messagebox.showerror("错误", "请先选择DICOM文件")
            return
        
        self.status_var.set(f"正在加载: {self.current_file}")
        self.root.update()
        
        if self.processor.load_dicom(self.current_file):
            self.status_var.set(f"已加载: {self.current_file}")
            self._update_image_display(self.processor.pixel_data)
            messagebox.showinfo("成功", "DICOM文件加载成功")
        else:
            self.status_var.set("加载失败")
            messagebox.showerror("错误", "无法加载DICOM文件")
    
    def _toggle_debug(self):
        self.processor.debug_mode = self.debug_var.get()
        status = "启用" if self.processor.debug_mode else "禁用"
        self.status_var.set(f"调试模式已{status}")
        logger.info(f"Debug mode: {status}")
    
    def _apply_window(self):
        if self.processor.pixel_data is None:
            messagebox.showerror("错误", "请先加载DICOM文件")
            return
        
        try:
            ww = self.ww_var.get()
            wl = self.wl_var.get()
            windowed = self.processor.adjust_window(ww, wl)
            self._update_image_display(windowed)
            self.status_var.set(f"已应用窗宽窗位: WW={ww}, WL={wl}")
        except Exception as e:
            self.status_var.set(f"窗宽窗位应用失败: {str(e)}")
            messagebox.showerror("错误", f"窗宽窗位应用失败: {str(e)}")
    
    def _segment(self):
        if self.processor.pixel_data is None:
            messagebox.showerror("错误", "请先加载DICOM文件")
            return
        
        self.status_var.set("正在执行灰白质分割...")
        self.root.update()
        
        try:
            gm_mask, wm_mask = self.processor.segment_gray_white_matter()
            
            rgb_image = np.zeros((self.processor.pixel_data.shape[0], self.processor.pixel_data.shape[1], 3))
            windowed = self.processor.adjust_window(400, 40)
            rgb_image[:, :, 0] = windowed / 255.0
            rgb_image[:, :, 1] = gm_mask * 0.5
            rgb_image[:, :, 2] = wm_mask * 0.5
            
            self._update_image_display(rgb_image)
            self.status_var.set("灰白质分割完成")
        except Exception as e:
            self.status_var.set(f"分割失败: {str(e)}")
            messagebox.showerror("错误", f"分割失败: {str(e)}")
    
    def _show_protocol(self):
        if not self.processor.protocol_info:
            messagebox.showerror("错误", "请先加载DICOM文件")
            return
        
        format_type = self.format_var.get()
        protocol_text = self.processor.get_protocol_info(format_type)
        
        self.protocol_text.delete(1.0, tk.END)
        self.protocol_text.insert(tk.END, protocol_text)
        self.status_var.set(f"已显示{format_type.upper()}格式协议信息")
    
    def _update_image_display(self, image_data):
        self.axes.clear()
        
        if len(image_data.shape) == 2:
            self.axes.imshow(image_data, cmap=plt.cm.gray)
        else:
            self.axes.imshow(image_data)
        
        self.axes.axis('off')
        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = DicomGUI(root)
    root.mainloop()    
