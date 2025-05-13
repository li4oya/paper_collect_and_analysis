import pandas as pd
import json

def extract_data_from_ccs(file_path):
    """
    从CCS24.xls文件中提取数据并转换为JSON格式
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 查看列名以确认列名正确
        print("Available columns:", df.columns.tolist())
        
        # 创建结果列表
        results = []
        
        # 遍历DataFrame的每一行
        for index, row in df.iterrows():
            # 创建每行的JSON数据
            json_data = {
                "Article Title": str(row.get("Article Title", "")),
                "Authors": str(row.get("Authors", "")),
                "Abstract": str(row.get("Abstract", "")),
                "Publication Year": str(row.get("Publication Year", "")),
                "DOI": str(row.get("DOI", ""))
            }
            
            results.append(json_data)
        
        return results
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return []

def save_to_json_file(data, output_file):
    """
    将数据保存到JSON文件（数组格式）
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving file: {e}")

# 主程序
if __name__ == "__main__":
    # 输入文件路径
    input_file = "CCS24.xls"
    output_file = "CCS24.json"
    
    # 提取数据
    data = extract_data_from_ccs(input_file)
    
    # 保存为JSON文件
    if data:
        save_to_json_file(data, output_file)
        print(f"\nTotal items saved: {len(data)}")
        print("\nExample output (first item):")
        print(json.dumps(data[0], indent=2, ensure_ascii=False))