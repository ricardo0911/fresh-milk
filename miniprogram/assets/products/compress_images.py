from PIL import Image
import os

# 图片目录
input_dir = r"c:\Users\root\Desktop\fresh-milk\miniprogram\assets\products"
output_dir = input_dir

# 目标大小 KB
target_kb = 35

# 处理每个图片
for filename in os.listdir(input_dir):
    if filename.endswith('.png'):
        filepath = os.path.join(input_dir, filename)
        img = Image.open(filepath)
        
        # 转换为 RGB
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # 缩小尺寸
        img = img.resize((400, 400), Image.Resampling.LANCZOS)
        
        # 保存为 JPEG，调整质量直到小于目标大小
        output_path = os.path.join(output_dir, filename.replace('.png', '.jpg'))
        quality = 80
        
        while quality > 10:
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            size_kb = os.path.getsize(output_path) / 1024
            print(f"{filename} -> {size_kb:.1f}KB (quality={quality})")
            if size_kb <= target_kb:
                break
            quality -= 10
        
        # 删除原 PNG
        os.remove(filepath)
        print(f"Saved: {output_path}")

print("Done!")
