import json
import os
import re # Import regular expressions for more robust parsing
from tqdm import tqdm # Import tqdm for progress bar
from langchain_community.llms import Tongyi
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
# Load API Key from environment variable for better security
# Create a .env file in the same directory with:
# TONGYI_API_KEY=your_actual_api_key
# or set the environment variable manually
# from dotenv import load_dotenv
# load_dotenv()
# api_key = os.getenv("TONGYI_API_KEY")
api_key = ""

if not api_key:
    raise ValueError("TONGXI_API_KEY environment variable not set.")

MODEL_NAME = "qwen3-235b-a22b" # Changed model name based on common Dashscope naming, adjust if 'qwq-plus' is correct
# MODEL_NAME = "qwq-plus" # Use this if 'qwq-plus' is definitely the correct identifier
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
INPUT_PAPERS_FILE = "./paper_collect/usenix_papers.json"
LABELS_FILE = "./labels.txt"
OUTPUT_JSON_FULL = "usenix_papers_keywords_v2.json"
OUTPUT_JSON_KEYWORDS_ONLY = "usenix_papers_keywords_only_v2.json"
DEFAULT_LABEL = "未分类"

# --- LLM Setup ---
# Configure Tongyi client, enable streaming, and specify the model
try:
    llm = Tongyi(
        model=MODEL_NAME,
        api_key=api_key, # Use the correct parameter name
        # streaming=True, # Enable streaming <--- THIS IS THE KEY FIX (if supported directly by constructor)
        # Note: As of recent Langchain versions, streaming might be controlled more by how you call the chain (.stream vs .invoke/.run)
        # Let's try without explicitly setting streaming=True first, and use chain.invoke
        # If it still fails, we might need to use chain.stream or check Tongyi constructor args again.
        # Based on the error, the *API endpoint* requires stream mode. Let's assume Langchain handles this when needed.
        base_url = BASE_URL,
    )
except Exception as e:
    print(f"Error initializing Tongyi LLM: {e}")
    exit()

# --- Prompt Template ---
# Create a Prompt template, including theme labels
prompt_template_str = """
你是一个网络安全领域的科研导师。给定以下论文的标题和摘要：

Title: {title}
Abstract: {abstract}

请执行以下任务：
1.  提取三个最能代表论文研究方向的核心关键词。
2.  每个关键词要求简洁、准确。
3.  在每个关键词后，提供其对应的中文翻译，格式为：`关键词 (中文翻译)`。
4.  在每个关键词及其翻译后，附上一句对该研究方向或关键词含义的简短归纳（15字以内）。
5.  将三个关键词及其相关信息按顺序列出，每个占一行。
6.  在关键词列表之后，另起一行，并根据论文内容从以下主题标签中选择一个最适合的主题标签：

{labels}

7.  请确保最后一行**只包含**所选主题标签的名称，不要有任何其他文字或格式。

输出格式示例：
Keyword1 (翻译1) - 简短归纳1
Keyword2 (翻译2) - 简短归纳2
Keyword3 (翻译3) - 简短归纳3

选定的主题标签名称
"""

# --- Load Labels ---
try:
    with open(LABELS_FILE, "r", encoding="utf-8") as file:
        labels = file.read().strip()
        # Ensure labels are distinct lines if needed by the prompt context
        # labels_list = [label.strip() for label in labels.split('\n') if label.strip()]
        # labels_formatted_for_prompt = "\n".join(f"- {label}" for label in labels_list)
        # Assuming the original file format is already suitable for the prompt:
        labels_formatted_for_prompt = labels
except FileNotFoundError:
    print(f"Error: Labels file not found at {LABELS_FILE}")
    exit()
except Exception as e:
    print(f"Error reading labels file: {e}")
    exit()


# --- LangChain Setup ---
prompt = PromptTemplate(
    input_variables=["title", "abstract", "labels"], template=prompt_template_str
)

# Using LLMChain (older) or the newer LCEL style
# Option 1: LLMChain (as in original code, but using .invoke which might handle streaming implicitly)
# chain = LLMChain(llm=llm, prompt=prompt)

# Option 2: LCEL (LangChain Expression Language - recommended)
chain = prompt | llm | StrOutputParser()

# --- Load Paper Data ---
try:
    with open(INPUT_PAPERS_FILE, "r", encoding="utf-8") as file:
        papers = json.load(file)
except FileNotFoundError:
    print(f"Error: Input papers file not found at {INPUT_PAPERS_FILE}")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {INPUT_PAPERS_FILE}")
    exit()
except Exception as e:
    print(f"Error reading input papers file: {e}")
    exit()


# --- Process Papers ---
papers_data = []
papers_keywords_only = []

print(f"Processing {len(papers)} papers...")
# Use tqdm for a progress bar
for paper in tqdm(papers, desc="Extracting Keywords and Labels"):
    title = paper.get('title', 'No Title Provided')
    abstract = paper.get('abstract', 'No Abstract Provided')
    authors = paper.get('authors', [])
    pdf_link = paper.get('pdf_link', '')

    if not abstract or abstract == 'No Abstract Provided':
        print(f"Skipping paper '{title}' due to missing abstract.")
        keywords_output = "关键词提取失败 (无摘要)"
        theme_label = DEFAULT_LABEL
    else:
        try:
            # Use chain.invoke with LCEL or chain.run with LLMChain
            # .invoke is generally preferred in newer Langchain versions
            response = chain.invoke({
                "title": title,
                "abstract": abstract,
                "labels": labels_formatted_for_prompt
            })

            # --- Parse the response ---
            # Improved parsing: Handle potential variations in line breaks and content
            lines = [line.strip() for line in response.strip().split('\n') if line.strip()]

            if len(lines) >= 4:
                # Assume first 3 lines are keywords, last line is the label
                keywords_output = "\n".join(lines[:-1])
                theme_label = lines[-1]

                # Optional: Validate if the extracted label is in the provided list
                # known_labels = set(labels_list) # If you created labels_list earlier
                # if theme_label not in known_labels:
                #     print(f"Warning: Extracted label '{theme_label}' for paper '{title}' is not in the known labels list. Using default.")
                #     theme_label = DEFAULT_LABEL

            elif len(lines) > 0:
                 # Fallback: Maybe only keywords or only label returned, or format mismatch
                 print(f"Warning: Unexpected response format for paper '{title}'. Attempting fallback parsing.")
                 # Heuristic: Assume the last line is the label if it looks like one, else all is keywords
                 potential_label = lines[-1]
                 # A simple check: if the potential label exists in the original labels string
                 if potential_label in labels: # Simple substring check, might need refinement
                     theme_label = potential_label
                     keywords_output = "\n".join(lines[:-1]) if len(lines) > 1 else "关键词提取失败 (格式错误)"
                 else:
                     theme_label = DEFAULT_LABEL
                     keywords_output = "\n".join(lines) # Assume all lines are keyword related
            else:
                # Empty response
                print(f"Warning: Empty response received for paper '{title}'.")
                keywords_output = "关键词提取失败 (空响应)"
                theme_label = DEFAULT_LABEL

        # except OutputParsingException as ope:
        #     print(f"Error parsing LLM output for paper '{title}': {ope}")
        #     keywords_output = "关键词提取失败 (解析错误)"
        #     theme_label = DEFAULT_LABEL
        except ValueError as ve: # Catch the specific ValueError from the API if it happens here
             print(f"API Error for paper '{title}': {ve}")
             print("This might indicate the streaming requirement is still not met.")
             print("Consider using chain.stream() or double-checking LLM initialization.")
             keywords_output = "关键词提取失败 (API错误)"
             theme_label = DEFAULT_LABEL
             # Optional: break or continue depending on desired behavior for API errors
             # continue
        except Exception as e:
            print(f"An unexpected error occurred processing paper '{title}': {e}")
            keywords_output = "关键词提取失败 (未知错误)"
            theme_label = DEFAULT_LABEL

    # --- Store Results ---
    paper_data = {
        'title': title,
        'authors': authors,
        'keywords': keywords_output,
        'abstract': abstract,
        'pdf_link': pdf_link,
        'theme_label': theme_label
    }
    papers_data.append(paper_data)

    paper_keywords_data = {
        'title': title,
        'keywords': keywords_output,
        'theme_label': theme_label
    }
    papers_keywords_only.append(paper_keywords_data)

# --- Save Results ---
try:
    with open(OUTPUT_JSON_FULL, mode='w', encoding='utf-8') as json_file:
        json.dump(papers_data, json_file, ensure_ascii=False, indent=4)
    print(f"\nFull data with keywords saved to {OUTPUT_JSON_FULL}")

    with open(OUTPUT_JSON_KEYWORDS_ONLY, mode='w', encoding='utf-8') as json_file:
        json.dump(papers_keywords_only, json_file, ensure_ascii=False, indent=4)
    print(f"Keywords-only data saved to {OUTPUT_JSON_KEYWORDS_ONLY}")

except IOError as e:
    print(f"Error writing output JSON file: {e}")
except Exception as e:
    print(f"An unexpected error occurred during file writing: {e}")