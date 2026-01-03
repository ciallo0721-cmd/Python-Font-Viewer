"""
字体查看器 - Python Font Viewer
Copyright (C) 2026  ciallo0721-cmd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog, simpledialog
import sys
import json
import os
from datetime import datetime
from io import BytesIO
import math

# 尝试导入PIL库用于导出图片
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class FontViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("字体查看器 - Python Font Viewer")
        self.root.geometry("1000x800")
        
        # 设置图标（如果有）
        self.set_icon()
        
        # 收藏的字体
        self.favorites = []
        self.load_favorites()
        
        # 字体分类
        self.font_categories = {
            "所有字体": [],
            "收藏夹": [],
            "中文字体": [],
            "英文字体": [],
            "等宽字体": [],
            "衬线字体": [],
            "无衬线字体": []
        }
        
        # 最近使用的字体
        self.recent_fonts = []
        self.max_recent = 10
        
        # 对比模式相关
        self.compare_mode = False
        self.compare_fonts_list = []
        
        # 设置示例文本
        self.sample_text = self.create_sample_text()
        
        # 创建界面
        self.create_widgets()
        
        # 加载系统字体
        self.load_system_fonts()
        
        # 绑定键盘快捷键
        self.bind_shortcuts()
    
    def set_icon(self):
        """设置窗口图标"""
        try:
            # 尝试加载图标文件
            icon_paths = [
                "font_viewer.ico",
                "icon.ico",
                os.path.join(os.path.dirname(__file__), "font_viewer.ico")
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    break
        except:
            pass
    
    def create_sample_text(self):
        """创建包含多种字符的示例文本"""
        # 基础文本
        base_text = {
            "english_alphabet": """ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz
The quick brown fox jumps over a lazy dog.
Pack my box with five dozen liquor jugs.
How vexingly quick daft zebras jump!
Mr. Jock, TV quiz PhD, bags few lynx.
The five boxing wizards jump quickly.""",
            
            "chinese": """中文示例文本：
这是一个用于测试字体显示效果的中文示例。
良好的字体设计应该同时支持中西文字符。
字体查看器可以帮助设计师选择合适的字体。
中文排版需要考虑字间距、行间距和阅读舒适度。
宋体、黑体、楷体和仿宋是常用的中文字体。
选择合适的字体可以提升文本的可读性。
随着技术的发展，越来越多的优质中文字体被开发出来。""",
            
            "numbers": "数字: 0 1 2 3 4 5 6 7 8 9 ¼ ½ ¾ ¹ ² ³",
            
            "punctuation": """标点符号：
英文: , . ; : ! ? " ' ( ) [ ] { } < > / \\ | ~ ` @ # $ % ^ & * - _ + =
中文：， 。 ； ： ！ ？ 「 」 《 》 【 】 、 · … —""",
            
            "special_chars": """特殊字符：
© ® ™ € £ ¥ ¢ § ¶ † ‡ • · … – — 
ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ αβγδεζηθικλμνξοπρστυφχψω
АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ абвгдеёжзийклмнопрстуфхцчшщъыьэюя"""
        }
        
        # 组合所有文本
        full_text = "\n\n".join(base_text.values())
        return full_text
    
    def create_widgets(self):
        """创建界面控件"""
        # 创建菜单栏
        self.create_menu()
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # 字体分类标签和下拉框
        ttk.Label(main_frame, text="字体分类:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.font_category_var = tk.StringVar(value="所有字体")
        self.font_category_combo = ttk.Combobox(main_frame, textvariable=self.font_category_var, 
                                               width=15, state="readonly")
        self.font_category_combo.grid(row=0, column=0, sticky=tk.W, padx=(80, 5), pady=(0, 5))
        self.font_category_combo.bind('<<ComboboxSelected>>', self.filter_fonts_by_category)
        
        # 字体搜索框
        ttk.Label(main_frame, text="搜索字体:").grid(row=0, column=0, sticky=tk.W, padx=(200, 5), pady=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(main_frame, textvariable=self.search_var, width=25)
        self.search_entry.grid(row=0, column=0, sticky=tk.W, padx=(270, 5), pady=(0, 5))
        self.search_entry.bind('<KeyRelease>', self.filter_fonts_by_search)
        
        # 收藏按钮
        self.favorite_btn = ttk.Button(main_frame, text="★ 收藏", width=8, 
                                      command=self.toggle_favorite)
        self.favorite_btn.grid(row=0, column=0, sticky=tk.W, padx=(470, 5), pady=(0, 5))
        
        # 对比模式按钮
        self.compare_mode_btn = ttk.Button(main_frame, text="对比模式", width=8,
                                          command=self.toggle_compare_mode)
        self.compare_mode_btn.grid(row=0, column=0, sticky=tk.W, padx=(560, 5), pady=(0, 5))
        
        # 字体选择标签和下拉框
        ttk.Label(main_frame, text="选择字体:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.font_family_var = tk.StringVar()
        self.font_family_combo = ttk.Combobox(main_frame, textvariable=self.font_family_var, 
                                             width=65, height=15)
        self.font_family_combo.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                                   pady=(0, 5), padx=(80, 0))
        self.font_family_combo.bind('<<ComboboxSelected>>', self.on_font_selected)
        
        # 字体大小标签和滑块
        ttk.Label(main_frame, text="字体大小:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.font_size_var = tk.IntVar(value=16)
        font_size_frame = ttk.Frame(main_frame)
        font_size_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5), padx=(80, 0))
        
        ttk.Label(font_size_frame, text="8").pack(side=tk.LEFT, padx=(0, 5))
        self.font_size_scale = ttk.Scale(font_size_frame, from_=8, to=72, 
                                         variable=self.font_size_var, 
                                         command=lambda x: self.update_font_display())
        self.font_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(font_size_frame, text="72").pack(side=tk.LEFT, padx=(5, 0))
        
        # 字体大小输入框
        self.font_size_spinbox = ttk.Spinbox(font_size_frame, from_=8, to=200, 
                                            width=5, textvariable=self.font_size_var,
                                            command=self.update_font_display)
        self.font_size_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        self.font_size_var.trace('w', lambda *args: self.update_font_display())
        
        # 字体样式选项
        style_frame = ttk.LabelFrame(main_frame, text="字体样式", padding="10")
        style_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 创建样式复选框
        styles = [
            ("bold_var", "粗体", 0, 0),
            ("italic_var", "斜体", 0, 1),
            ("underline_var", "下划线", 0, 2),
            ("overstrike_var", "删除线", 0, 3)
        ]
        
        for var_name, text, row, col in styles:
            var = tk.BooleanVar(value=False)
            setattr(self, var_name, var)
            check = ttk.Checkbutton(style_frame, text=text, variable=var, 
                                   command=self.update_font_display)
            check.grid(row=row, column=col, padx=(0, 10))
        
        # 字体信息显示
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.font_info_label = ttk.Label(info_frame, text="", foreground="blue")
        self.font_info_label.pack(side=tk.LEFT)
        
        # 示例文本标签和自定义按钮
        text_label_frame = ttk.Frame(main_frame)
        text_label_frame.grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(text_label_frame, text="示例文本:").pack(side=tk.LEFT)
        ttk.Button(text_label_frame, text="自定义", width=8,
                  command=self.customize_sample_text).pack(side=tk.LEFT, padx=(10, 0))
        
        # 文本显示区域
        text_frame = ttk.Frame(main_frame, borderwidth=1, relief=tk.SUNKEN)
        text_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建文本显示区域和滚动条
        self.create_text_display(text_frame)
        
        # 底部按钮
        self.create_bottom_buttons(main_frame)
        
        # 状态栏
        self.create_status_bar()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导出为图片", command=self.export_as_image)
        file_menu.add_separator()
        file_menu.add_command(label="导入自定义文本", command=self.import_sample_text)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="复制字体信息", command=self.copy_font_info)
        edit_menu.add_command(label="复制示例文本", command=self.copy_sample_text)
        edit_menu.add_separator()
        edit_menu.add_command(label="重置设置", command=self.reset_settings)
        
        # 查看菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="查看", menu=view_menu)
        view_menu.add_command(label="刷新字体列表", command=self.refresh_fonts)
        view_menu.add_command(label="显示最近使用", command=self.show_recent_fonts)
        view_menu.add_command(label="显示收藏夹", command=lambda: self.show_font_category("收藏夹"))
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        help_menu.add_command(label="快捷键", command=self.show_shortcuts)
    
    def create_text_display(self, parent):
        """创建文本显示区域"""
        # 添加滚动条
        text_scrollbar = ttk.Scrollbar(parent)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 文本显示框
        self.text_display = tk.Text(parent, wrap=tk.WORD, yscrollcommand=text_scrollbar.set,
                                    padx=15, pady=15, undo=True, maxundo=10)
        self.text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.text_display.yview)
        
        # 设置示例文本
        self.text_display.insert(1.0, self.sample_text)
        
        # 添加右键菜单
        self.create_text_context_menu()
    
    def create_text_context_menu(self):
        """创建文本右键菜单"""
        self.text_context_menu = tk.Menu(self.root, tearoff=0)
        self.text_context_menu.add_command(label="复制", command=self.copy_text_selection)
        self.text_context_menu.add_command(label="粘贴", command=self.paste_to_text)
        self.text_context_menu.add_command(label="全选", command=self.select_all_text)
        self.text_context_menu.add_separator()
        self.text_context_menu.add_command(label="清除格式", command=self.clear_text_formatting)
        
        # 绑定右键事件
        self.text_display.bind("<Button-3>", self.show_text_context_menu)
    
    def create_bottom_buttons(self, parent):
        """创建底部按钮"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        
        buttons = [
            ("字体对比", self.compare_fonts, 0),
            ("生成报告", self.generate_report, 1),
            ("保存预设", self.save_preset, 2),
            ("加载预设", self.load_preset, 3),
            ("重置", self.reset_settings, 4),
            ("退出", self.root.quit, 5)
        ]
        
        for text, command, column in buttons:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.grid(row=0, column=column, padx=2)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_bar.config(text=f"{message} | {datetime.now().strftime('%H:%M:%S')}")
        self.root.after(3000, lambda: self.status_bar.config(text="就绪"))
    
    def load_system_fonts(self):
        """加载系统可用字体"""
        try:
            self.update_status("正在加载字体...")
            
            # 获取系统所有字体
            font_families = list(font.families())
            font_families.sort()
            
            # 分类字体
            self.categorize_fonts(font_families)
            
            # 设置字体分类下拉框
            self.font_category_combo['values'] = list(self.font_categories.keys())
            
            # 显示所有字体
            self.font_family_combo['values'] = self.font_categories["所有字体"]
            
            # 设置默认字体
            default_fonts = ['Microsoft YaHei', 'Arial', 'SimSun', 'Times New Roman', 'Segoe UI']
            for df in default_fonts:
                if df in font_families:
                    self.font_family_var.set(df)
                    self.add_to_recent(df)
                    break
            else:
                if font_families:
                    self.font_family_var.set(font_families[0])
                    self.add_to_recent(font_families[0])
            
            # 更新字体显示
            self.update_font_display()
            self.update_status(f"已加载 {len(font_families)} 种字体")
            
        except Exception as e:
            messagebox.showerror("错误", f"加载字体时出错: {e}")
            self.font_family_combo['values'] = ['字体加载失败']
            self.font_family_var.set('字体加载失败')
    
    def categorize_fonts(self, font_families):
        """对字体进行分类"""
        self.font_categories["所有字体"] = font_families
        
        # 简单分类逻辑（实际应用中可能需要更复杂的检测）
        for font_name in font_families:
            font_lower = font_name.lower()
            
            # 中文字体检测
            if any(keyword in font_lower for keyword in ['song', 'hei', 'kai', 'fang', 'sim', 'microsoft', 'yahei']):
                self.font_categories["中文字体"].append(font_name)
            
            # 英文字体检测
            if any(keyword in font_lower for keyword in ['arial', 'times', 'courier', 'verdana', 'tahoma', 'georgia']):
                self.font_categories["英文字体"].append(font_name)
            
            # 等宽字体检测
            if any(keyword in font_lower for keyword in ['mono', 'courier', 'consolas', 'fixedsys']):
                self.font_categories["等宽字体"].append(font_name)
            
            # 衬线/无衬线字体（简单判断）
            if any(keyword in font_lower for keyword in ['times', 'georgia', '宋体', 'simsun']):
                self.font_categories["衬线字体"].append(font_name)
            elif any(keyword in font_lower for keyword in ['arial', 'helvetica', 'verdana', 'tahoma', '黑体', 'yahei']):
                self.font_categories["无衬线字体"].append(font_name)
        
        # 收藏夹
        self.font_categories["收藏夹"] = self.favorites
    
    def filter_fonts_by_category(self, event=None):
        """根据分类过滤字体"""
        category = self.font_category_var.get()
        if category in self.font_categories:
            fonts = self.font_categories[category]
            self.font_family_combo['values'] = fonts
            if fonts:
                self.font_family_var.set(fonts[0])
                self.update_font_display()
    
    def filter_fonts_by_search(self, event=None):
        """根据搜索词过滤字体"""
        search_term = self.search_var.get().lower()
        if not search_term:
            self.filter_fonts_by_category()
            return
        
        current_category = self.font_category_var.get()
        if current_category in self.font_categories:
            all_fonts = self.font_categories[current_category]
        else:
            all_fonts = self.font_categories["所有字体"]
        
        filtered_fonts = [f for f in all_fonts if search_term in f.lower()]
        self.font_family_combo['values'] = filtered_fonts
        
        if filtered_fonts:
            self.font_family_var.set(filtered_fonts[0])
            self.update_font_display()
    
    def on_font_selected(self, event=None):
        """字体被选中时的处理"""
        font_name = self.font_family_var.get()
        if font_name:
            if self.compare_mode:
                self.add_to_compare_list(font_name)
            else:
                self.add_to_recent(font_name)
                self.update_font_display()
                self.update_favorite_button()
    
    def add_to_recent(self, font_name):
        """添加到最近使用"""
        if font_name in self.recent_fonts:
            self.recent_fonts.remove(font_name)
        self.recent_fonts.insert(0, font_name)
        
        # 限制最近使用的数量
        if len(self.recent_fonts) > self.max_recent:
            self.recent_fonts = self.recent_fonts[:self.max_recent]
    
    def add_to_compare_list(self, font_name):
        """添加到对比列表"""
        if font_name in self.compare_fonts_list:
            self.compare_fonts_list.remove(font_name)
            messagebox.showinfo("提示", f"已从对比列表移除: {font_name}")
        else:
            self.compare_fonts_list.append(font_name)
            messagebox.showinfo("提示", f"已添加到对比列表: {font_name}")
        
        # 更新对比模式按钮显示
        if self.compare_mode:
            self.compare_mode_btn.config(text=f"对比模式({len(self.compare_fonts_list)}/4)")
    
    def toggle_compare_mode(self):
        """切换对比模式"""
        self.compare_mode = not self.compare_mode
        
        if self.compare_mode:
            self.compare_fonts_list = []
            self.compare_mode_btn.config(text="对比模式(0/4)", style="Accent.TButton")
            self.update_status("对比模式已启用，请选择要对比的字体（最多4种）")
        else:
            self.compare_mode_btn.config(text="对比模式", style="TButton")
            self.update_status("对比模式已关闭")
            
            # 如果对比列表中有字体，则打开对比窗口
            if len(self.compare_fonts_list) > 1:
                self.show_compare_window()
            elif len(self.compare_fonts_list) == 1:
                self.font_family_var.set(self.compare_fonts_list[0])
                self.update_font_display()
    
    def update_font_display(self, *args):
        """更新字体显示"""
        try:
            # 获取当前字体设置
            font_family = self.font_family_var.get()
            font_size = self.font_size_var.get()
            
            # 构建字体样式
            font_weight = "bold" if self.bold_var.get() else "normal"
            font_slant = "italic" if self.italic_var.get() else "roman"
            font_underline = self.underline_var.get()
            font_overstrike = self.overstrike_var.get()
            
            # 创建字体
            current_font = font.Font(family=font_family, size=font_size,
                                     weight=font_weight, slant=font_slant,
                                     underline=font_underline, overstrike=font_overstrike)
            
            # 应用到文本显示框
            self.text_display.configure(font=current_font)
            
            # 更新字体信息标签
            font_info_parts = [font_family, f"{font_size}pt"]
            
            if self.bold_var.get():
                font_info_parts.append("粗体")
            if self.italic_var.get():
                font_info_parts.append("斜体")
            if self.underline_var.get():
                font_info_parts.append("下划线")
            if self.overstrike_var.get():
                font_info_parts.append("删除线")
            
            font_info = " | ".join(font_info_parts)
            self.font_info_label.config(text=font_info)
            
        except Exception as e:
            messagebox.showerror("错误", f"更新字体时出错: {e}")
    
    def toggle_favorite(self):
        """切换收藏状态"""
        font_name = self.font_family_var.get()
        if not font_name:
            return
        
        if font_name in self.favorites:
            self.favorites.remove(font_name)
            messagebox.showinfo("提示", f"已从收藏夹移除: {font_name}")
        else:
            self.favorites.append(font_name)
            messagebox.showinfo("提示", f"已添加到收藏夹: {font_name}")
        
        self.save_favorites()
        self.font_categories["收藏夹"] = self.favorites
        self.update_favorite_button()
    
    def update_favorite_button(self):
        """更新收藏按钮状态"""
        font_name = self.font_family_var.get()
        if font_name in self.favorites:
            self.favorite_btn.config(text="★ 已收藏")
        else:
            self.favorite_btn.config(text="☆ 收藏")
    
    def load_favorites(self):
        """加载收藏的字体"""
        try:
            if os.path.exists("favorites.json"):
                with open("favorites.json", "r", encoding="utf-8") as f:
                    self.favorites = json.load(f)
        except:
            self.favorites = []
    
    def save_favorites(self):
        """保存收藏的字体"""
        try:
            with open("favorites.json", "w", encoding="utf-8") as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存收藏时出错: {e}")
    
    def customize_sample_text(self):
        """自定义示例文本"""
        current_text = self.text_display.get(1.0, tk.END).strip()
        new_text = simpledialog.askstring("自定义文本", "请输入新的示例文本:", 
                                         initialvalue=current_text)
        if new_text:
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(1.0, new_text)
            self.update_status("示例文本已更新")
    
    def import_sample_text(self):
        """从文件导入示例文本"""
        file_path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                self.text_display.delete(1.0, tk.END)
                self.text_display.insert(1.0, content)
                self.update_status(f"已导入文件: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"读取文件时出错: {e}")
    
    def export_as_image(self):
        """导出为图片"""
        if not PIL_AVAILABLE:
            result = messagebox.askyesno("缺少依赖库", 
                "导出为图片功能需要PIL库。\n是否要安装Pillow库？\n\n安装命令: pip install pillow")
            if result:
                import webbrowser
                webbrowser.open("https://pypi.org/project/pillow/")
            return
        
        try:
            # 获取文本内容
            text_content = self.text_display.get(1.0, tk.END)
            font_name = self.font_family_var.get()
            font_size = self.font_size_var.get()
            
            # 询问图片尺寸
            size_window = tk.Toplevel(self.root)
            size_window.title("设置图片尺寸")
            size_window.geometry("300x200")
            size_window.transient(self.root)
            size_window.grab_set()
            
            ttk.Label(size_window, text="设置导出图片尺寸", font=("Microsoft YaHei", 12)).pack(pady=10)
            
            size_frame = ttk.Frame(size_window, padding="10")
            size_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(size_frame, text="宽度:").grid(row=0, column=0, sticky=tk.W, pady=5)
            width_var = tk.IntVar(value=800)
            ttk.Spinbox(size_frame, from_=100, to=3000, textvariable=width_var, width=10).grid(row=0, column=1, pady=5)
            
            ttk.Label(size_frame, text="高度:").grid(row=1, column=0, sticky=tk.W, pady=5)
            height_var = tk.IntVar(value=600)
            ttk.Spinbox(size_frame, from_=100, to=3000, textvariable=height_var, width=10).grid(row=1, column=1, pady=5)
            
            ttk.Label(size_frame, text="背景色:").grid(row=2, column=0, sticky=tk.W, pady=5)
            bg_color_var = tk.StringVar(value="#FFFFFF")
            ttk.Entry(size_frame, textvariable=bg_color_var, width=10).grid(row=2, column=1, pady=5)
            
            ttk.Label(size_frame, text="文字颜色:").grid(row=3, column=0, sticky=tk.W, pady=5)
            text_color_var = tk.StringVar(value="#000000")
            ttk.Entry(size_frame, textvariable=text_color_var, width=10).grid(row=3, column=1, pady=5)
            
            def do_export():
                width = width_var.get()
                height = height_var.get()
                bg_color = bg_color_var.get()
                text_color = text_color_var.get()
                
                # 选择保存路径
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[
                        ("PNG 图片", "*.png"),
                        ("JPEG 图片", "*.jpg"),
                        ("BMP 图片", "*.bmp"),
                        ("所有文件", "*.*")
                    ],
                    initialfile=f"font_{font_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                
                if file_path:
                    try:
                        # 创建图片
                        image = Image.new('RGB', (width, height), bg_color)
                        draw = ImageDraw.Draw(image)
                        
                        # 尝试加载字体
                        try:
                            img_font = ImageFont.truetype(font_name, font_size)
                        except:
                            img_font = ImageFont.load_default()
                        
                        # 绘制文字
                        draw.text((20, 20), text_content, fill=text_color, font=img_font)
                        
                        # 保存图片
                        image.save(file_path)
                        
                        size_window.destroy()
                        self.update_status(f"已导出图片: {os.path.basename(file_path)}")
                        messagebox.showinfo("导出成功", f"图片已成功导出到:\n{file_path}")
                        
                    except Exception as e:
                        messagebox.showerror("导出失败", f"导出图片时出错: {e}")
            
            ttk.Button(size_window, text="导出", command=do_export).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("错误", f"导出图片时出错: {e}")
    
    def copy_font_info(self):
        """复制字体信息到剪贴板"""
        try:
            font_info = self.font_info_label.cget('text')
            self.root.clipboard_clear()
            self.root.clipboard_append(font_info)
            self.update_status("字体信息已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制字体信息时出错: {e}")
    
    def copy_sample_text(self):
        """复制示例文本到剪贴板"""
        try:
            text = self.text_display.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.update_status("示例文本已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制文本时出错: {e}")
    
    def copy_text_selection(self):
        """复制选中的文本"""
        try:
            selected_text = self.text_display.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except:
            pass
    
    def paste_to_text(self):
        """粘贴到文本框中"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.text_display.insert(tk.INSERT, clipboard_text)
        except:
            pass
    
    def select_all_text(self):
        """全选文本框内容"""
        self.text_display.tag_add(tk.SEL, "1.0", tk.END)
        self.text_display.mark_set(tk.INSERT, "1.0")
        self.text_display.see(tk.INSERT)
        return 'break'
    
    def clear_text_formatting(self):
        """清除文本格式（重置为默认格式）"""
        self.text_display.tag_remove(tk.SEL, "1.0", tk.END)
        self.update_status("文本格式已清除")
    
    def show_text_context_menu(self, event):
        """显示文本右键菜单"""
        try:
            self.text_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.text_context_menu.grab_release()
    
    def refresh_fonts(self):
        """刷新字体列表"""
        self.load_system_fonts()
        self.update_status("字体列表已刷新")
    
    def show_recent_fonts(self):
        """显示最近使用的字体"""
        self.font_category_var.set("所有字体")
        self.search_var.set("")
        
        if self.recent_fonts:
            recent_window = tk.Toplevel(self.root)
            recent_window.title("最近使用的字体")
            recent_window.geometry("300x400")
            
            listbox = tk.Listbox(recent_window, font=("Microsoft YaHei", 10))
            scrollbar = ttk.Scrollbar(recent_window, orient=tk.VERTICAL, command=listbox.yview)
            listbox.config(yscrollcommand=scrollbar.set)
            
            for font_name in self.recent_fonts:
                listbox.insert(tk.END, font_name)
            
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            def select_font(event):
                selection = listbox.curselection()
                if selection:
                    font_name = listbox.get(selection[0])
                    self.font_family_var.set(font_name)
                    self.update_font_display()
                    recent_window.destroy()
            
            listbox.bind('<Double-Button-1>', select_font)
        else:
            messagebox.showinfo("最近使用", "暂无最近使用的字体")
    
    def show_font_category(self, category):
        """显示指定分类的字体"""
        self.font_category_var.set(category)
        self.filter_fonts_by_category()
    
    def compare_fonts(self):
        """字体对比功能"""
        if not self.compare_fonts_list or len(self.compare_fonts_list) < 2:
            messagebox.showinfo("字体对比", "请先选择至少2种字体进行对比")
            return
        
        self.show_compare_window()
    
    def show_compare_window(self):
        """显示对比窗口"""
        compare_window = tk.Toplevel(self.root)
        compare_window.title("字体对比")
        compare_window.geometry("1200x700")
        
        # 获取当前字体大小和样式
        font_size = self.font_size_var.get()
        bold = self.bold_var.get()
        italic = self.italic_var.get()
        underline = self.underline_var.get()
        overstrike = self.overstrike_var.get()
        
        # 创建对比框架
        main_frame = ttk.Frame(compare_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 计算列数（最多4列）
        num_fonts = min(len(self.compare_fonts_list), 4)
        cols = math.ceil(math.sqrt(num_fonts))
        rows = math.ceil(num_fonts / cols)
        
        # 获取文本内容
        sample_text = self.text_display.get(1.0, tk.END)
        
        # 创建字体显示区域
        for i, font_name in enumerate(self.compare_fonts_list[:num_fonts]):
            row = i // cols
            col = i % cols
            
            # 创建字体框架
            font_frame = ttk.LabelFrame(scrollable_frame, text=font_name, padding="10")
            font_frame.grid(row=row, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
            
            # 配置网格权重
            scrollable_frame.columnconfigure(col, weight=1)
            scrollable_frame.rowconfigure(row, weight=1)
            font_frame.columnconfigure(0, weight=1)
            font_frame.rowconfigure(0, weight=1)
            
            # 创建字体
            current_font = font.Font(
                family=font_name, 
                size=font_size,
                weight="bold" if bold else "normal",
                slant="italic" if italic else "roman",
                underline=underline,
                overstrike=overstrike
            )
            
            # 创建文本显示框
            text_widget = tk.Text(
                font_frame, 
                wrap=tk.WORD, 
                font=current_font,
                padx=10, 
                pady=10,
                height=15
            )
            
            # 添加滚动条
            text_scrollbar = ttk.Scrollbar(font_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=text_scrollbar.set)
            
            text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            text_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            
            # 添加文本
            text_widget.insert(1.0, sample_text)
            text_widget.config(state=tk.DISABLED)
        
        # 添加控制按钮
        button_frame = ttk.Frame(compare_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def export_comparison():
            """导出对比结果为图片"""
            if not PIL_AVAILABLE:
                messagebox.showerror("缺少依赖库", "导出图片功能需要PIL库。\n请安装: pip install pillow")
                return
            
            try:
                # 选择保存路径
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[
                        ("PNG 图片", "*.png"),
                        ("JPEG 图片", "*.jpg"),
                        ("所有文件", "*.*")
                    ],
                    initialfile=f"font_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                
                if file_path:
                    # 计算图片尺寸
                    img_width = 1200
                    img_height = 800
                    
                    # 创建图片
                    image = Image.new('RGB', (img_width, img_height), '#FFFFFF')
                    draw = ImageDraw.Draw(image)
                    
                    # 绘制标题
                    draw.text((50, 20), "字体对比结果", fill='#000000', 
                             font=ImageFont.truetype("arial.ttf", 20))
                    
                    # 绘制字体对比
                    y_offset = 60
                    sample_lines = sample_text.split('\n')[:10]  # 只取前10行
                    
                    for i, font_name in enumerate(self.compare_fonts_list[:num_fonts]):
                        try:
                            img_font = ImageFont.truetype(font_name, font_size)
                        except:
                            img_font = ImageFont.load_default()
                        
                        # 绘制字体名称
                        draw.text((50, y_offset), f"{font_name}:", fill='#000000', 
                                 font=ImageFont.truetype("arial.ttf", 14))
                        
                        # 绘制示例文本
                        text_y = y_offset + 30
                        for line in sample_lines[:3]:  # 只取前3行
                            draw.text((70, text_y), line, fill='#000000', font=img_font)
                            text_y += 30
                        
                        y_offset += 150
                    
                    # 保存图片
                    image.save(file_path)
                    self.update_status(f"对比结果已导出: {os.path.basename(file_path)}")
                    messagebox.showinfo("导出成功", f"对比结果已导出到:\n{file_path}")
                    
            except Exception as e:
                messagebox.showerror("导出失败", f"导出对比结果时出错: {e}")
        
        ttk.Button(button_frame, text="导出为图片", command=export_comparison).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=compare_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def generate_report(self):
        """生成字体报告"""
        try:
            font_name = self.font_family_var.get()
            font_size = self.font_size_var.get()
            
            report = f"""字体分析报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

字体信息:
- 名称: {font_name}
- 大小: {font_size}pt
- 样式: {self.font_info_label.cget('text')}

字符集测试:
"""
            # 添加字符集测试
            test_chars = {
                "字母": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                "数字": "0123456789",
                "标点": "!@#$%^&*()_+-=[]{}|;:,.<>?",
                "中文": "中文测试字体显示效果"
            }
            
            for category, chars in test_chars.items():
                report += f"\n{category}:\n{chars}\n"
            
            # 显示报告
            report_window = tk.Toplevel(self.root)
            report_window.title(f"字体报告 - {font_name}")
            report_window.geometry("600x500")
            
            text_widget = tk.Text(report_window, wrap=tk.WORD, font=("Microsoft YaHei", 10))
            scrollbar = ttk.Scrollbar(report_window, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget.insert(1.0, report)
            text_widget.config(state=tk.DISABLED)
            
            # 保存报告按钮
            def save_report():
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                    initialfile=f"字体报告_{font_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                )
                
                if file_path:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(report)
                    self.update_status(f"报告已保存: {os.path.basename(file_path)}")
            
            ttk.Button(report_window, text="保存报告", command=save_report).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("错误", f"生成报告时出错: {e}")
    
    def save_preset(self):
        """保存当前设置为预设"""
        preset = {
            "font_family": self.font_family_var.get(),
            "font_size": self.font_size_var.get(),
            "bold": self.bold_var.get(),
            "italic": self.italic_var.get(),
            "underline": self.underline_var.get(),
            "overstrike": self.overstrike_var.get(),
            "sample_text": self.text_display.get(1.0, tk.END).strip()
        }
        
        preset_name = simpledialog.askstring("保存预设", "请输入预设名称:")
        if preset_name:
            try:
                if os.path.exists("presets.json"):
                    with open("presets.json", "r", encoding="utf-8") as f:
                        presets = json.load(f)
                else:
                    presets = {}
                
                presets[preset_name] = preset
                
                with open("presets.json", "w", encoding="utf-8") as f:
                    json.dump(presets, f, ensure_ascii=False, indent=2)
                
                self.update_status(f"预设 '{preset_name}' 已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存预设时出错: {e}")
    
    def load_preset(self):
        """加载预设"""
        try:
            if not os.path.exists("presets.json"):
                messagebox.showinfo("加载预设", "暂无保存的预设")
                return
            
            with open("presets.json", "r", encoding="utf-8") as f:
                presets = json.load(f)
            
            if not presets:
                messagebox.showinfo("加载预设", "暂无保存的预设")
                return
            
            # 创建选择窗口
            preset_window = tk.Toplevel(self.root)
            preset_window.title("加载预设")
            preset_window.geometry("400x300")
            
            listbox = tk.Listbox(preset_window, font=("Microsoft YaHei", 10))
            scrollbar = ttk.Scrollbar(preset_window, orient=tk.VERTICAL, command=listbox.yview)
            listbox.config(yscrollcommand=scrollbar.set)
            
            for preset_name in presets.keys():
                listbox.insert(tk.END, preset_name)
            
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
            
            def load_selected_preset():
                selection = listbox.curselection()
                if selection:
                    preset_name = listbox.get(selection[0])
                    preset = presets[preset_name]
                    
                    self.font_family_var.set(preset["font_family"])
                    self.font_size_var.set(preset["font_size"])
                    self.bold_var.set(preset["bold"])
                    self.italic_var.set(preset["italic"])
                    self.underline_var.set(preset["underline"])
                    self.overstrike_var.set(preset["overstrike"])
                    
                    self.text_display.delete(1.0, tk.END)
                    self.text_display.insert(1.0, preset["sample_text"])
                    
                    self.update_font_display()
                    preset_window.destroy()
                    self.update_status(f"已加载预设 '{preset_name}'")
            
            ttk.Button(preset_window, text="加载选中预设", 
                      command=load_selected_preset).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("错误", f"加载预设时出错: {e}")
    
    def reset_settings(self):
        """重置所有设置到默认值"""
        self.font_size_var.set(16)
        self.bold_var.set(False)
        self.italic_var.set(False)
        self.underline_var.set(False)
        self.overstrike_var.set(False)
        
        # 重置示例文本
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(1.0, self.sample_text)
        
        self.update_font_display()
        self.update_status("设置已重置")
    
    def bind_shortcuts(self):
        """绑定键盘快捷键"""
        # Ctrl+S: 保存预设
        self.root.bind('<Control-s>', lambda e: self.save_preset())
        
        # Ctrl+L: 加载预设
        self.root.bind('<Control-l>', lambda e: self.load_preset())
        
        # Ctrl+F: 搜索焦点
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus())
        
        # Ctrl+R: 刷新字体列表
        self.root.bind('<Control-r>', lambda e: self.refresh_fonts())
        
        # Ctrl+C: 复制字体信息
        self.root.bind('<Control-c>', lambda e: self.copy_font_info())
        
        # Ctrl+T: 自定义文本
        self.root.bind('<Control-t>', lambda e: self.customize_sample_text())
        
        # Ctrl+Q: 退出
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
        # Ctrl+M: 对比模式
        self.root.bind('<Control-m>', lambda e: self.toggle_compare_mode())
    
    def show_about(self):
        """显示关于信息"""
        about_text = """字体查看器 v2.0

一个功能丰富的字体预览和测试工具

功能特点:
• 预览系统所有可用字体
• 支持中、英、日、泰等多种语言
• 字体分类和搜索功能
• 收藏常用字体
• 自定义示例文本
• 字体对比功能
• 生成字体报告
• 保存/加载预设

作者: ciallo0721-cmd
版本: 2.0
发布日期: 2026"""
        
        messagebox.showinfo("关于字体查看器", about_text)
    
    def show_shortcuts(self):
        """显示快捷键"""
        shortcuts = """键盘快捷键:

Ctrl + F: 聚焦搜索框
Ctrl + R: 刷新字体列表
Ctrl + S: 保存当前预设
Ctrl + L: 加载预设
Ctrl + C: 复制字体信息
Ctrl + T: 自定义示例文本
Ctrl + M: 对比模式开关
Ctrl + Q: 退出程序

双击字体名称: 快速应用字体
"""
        messagebox.showinfo("快捷键", shortcuts)

def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置窗口风格
    try:
        # 尝试使用更好的主题
        style = ttk.Style()
        style.theme_use('clam')
        
        # 创建对比模式按钮的特殊样式
        style.configure('Accent.TButton', 
                       background='#007acc', 
                       foreground='white',
                       borderwidth=1)
    except:
        pass
    
    app = FontViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
