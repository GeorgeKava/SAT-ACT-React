from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    SearchIndex,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters
)
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
import os
import logging  # Logging facility for Python
from dotenv import load_dotenv, set_key
from IPython.display import Image, display, Audio, Markdown
import base64  # Base16, Base32, Base64, Base85 Data Encodings
import json
import re  # Regular expression operations
from mimetypes import guess_type
import uuid  # Add this import

load_dotenv()

search_service_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_api_key = os.getenv("AZURE_SEARCH_KEY")


azure_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
model = os.getenv('AZURE_OPENAI_MODEL')

embedding_model = "text-embedding-3-small"

index_name = os.getenv('AZURE_SEARCH_INDEX_NAME')

env_file_path = '.env'

client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    base_url=f"{azure_endpoint}/openai/deployments/{model}",
)

embedding_client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    base_url=f"{azure_endpoint}/openai/deployments/{embedding_model}",
)

search_client = SearchClient(
    endpoint=search_service_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(search_api_key)
)

index_client = SearchIndexClient(
    endpoint=search_service_endpoint,
    credential=AzureKeyCredential(search_api_key)
)

qa_client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    base_url=f"{azure_endpoint}/openai/deployments/{model}"
)

index_schema = SearchIndex(
    name=index_name,
    fields=[
        SimpleField(name="chunk_id", type="Edm.String", sortable=True,
                    filterable=True, facetable=True, key=True),
        SearchableField(name="question", type="Edm.String",
                        searchable=True, retrievable=True),
        SearchableField(name="answer", type="Edm.String", 
                        searchable=False, retrievable=True),
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=int(1536),
            vector_search_profile_name="myHnswProfile",
        )
    ]
)

def create_vector_search():
    vector_search = VectorSearch(
        # 1) Your HNSW algos
        algorithms=[
            HnswAlgorithmConfiguration(name="myHnsw")
        ],
        # 2) The profile that ties the field to your vectorizer
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
                vectorizer_name="myVectorizer"        # <<< note this
            )
        ],
        # 3) Your actual OpenAI vectorizer
        vectorizers=[
            AzureOpenAIVectorizer(
                vectorizer_name="myVectorizer",      # <<< and this
                parameters=AzureOpenAIVectorizerParameters(
                    resource_uri=azure_endpoint,     # e.g. "https://<your>.openai.azure.com"
                    api_key=api_key,
                    deployment_id=embedding_model,   # e.g. "text-embedding-3-small"
                    model_name=embedding_model       # required in 2024-05-01-preview+
                )
            )
        ]
    )
    return vector_search

def create_index():
    try:
        index_schema.vector_search = create_vector_search()
        index_client.create_index(index_schema)
    except Exception as e:
        logging.error(f"Failed to create index: {e}")
        
def local_image_to_data_url(image_path):  # Get the url of a local image
    mime_type, _ = guess_type(image_path)

    if (mime_type is None):
        mime_type = "application/octet-stream"

    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(
            image_file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{base64_encoded_data}"

def process_img_llm(img_name):
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        base_url=f"{azure_endpoint}/openai/deployments/{model}",
    )
    prompt = """You are a expert math assistant. Analyze the image provided and extract any math problems.
                Solve the math problems and provide detailed solutions.
                If there are multiple problems, solve each one and provide solutions in a JSON format.
                JSON Format:
                [
                    {
                        "problem": "2 + 2",
                        "solution": "The solution is 4."
                    },
                    {
                        "problem": "5 * 3",
                        "solution": "The solution is 15."
                    }
                ]
            """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant to analyse images.",
            },
            {
                "role": "user",
                "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": local_image_to_data_url(img_name)},
                        },
                ],
            },
        ],
        max_tokens=2000,
        temperature=0.0,
    )
    response_content = response.choices[0].message.content.strip()
    logging.debug(f"Response content: {response_content}")

    # Attempt to parse the response content as JSON
    json_match = re.search(r'\{.*\}', response_content,
                           re.DOTALL)  # Match a JSON object
    if json_match:
        # Extract the JSON object from the response content
        json_str = json_match.group(0)
        # Remove the JSON object from the response content
        summary = response_content.replace(json_str, '').strip()
        # Remove 'json[]' from the summary
        summary = re.sub(r'json\s*\[\s*\]', '', summary).strip()
        # Remove code blocks from the summary
        summary = summary.replace('```', '').strip()
        try:
            response_json = json.loads(json_str)
            logging.debug(f"Parsed JSON: {response_json}")
            # Ensure the response contains the required keys
            required_keys = ["problem", "solution"]
            if not all(key in response_json for key in required_keys):
                raise ValueError(
                    "Response JSON does not contain all required keys")
            # Create a formatted summary
            formatted_summary = (
                f"Problem: {response_json['problem']}<br>"
                f"Solution: {response_json['solution']}<br>"
                f"{summary}"
            )
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(
                f"Failed to parse response as JSON or missing keys: {e}")
            response_json = {
                "error": "Failed to parse response as JSON or missing keys",
                "response": response_content
            }
            formatted_summary = response_content
    else:
        logging.error("No JSON object found in the response content")
        response_json = {
            "error": "No JSON object found in the response content",
            "response": response_content
        }
        formatted_summary = response_content

    # Read existing data from the JSON file
    json_filename = 'math.json'
    try:
        with open(json_filename, 'r') as json_file:  # Open the JSON file for reading
            # Load the existing data from the JSON file
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty, initialize existing data as an empty list
        existing_data = []

    # Append the new data to the existing data
    if isinstance(existing_data, list):
        existing_data.append(response_json)
    else:
        existing_data = [existing_data, response_json]

    # Save the updated data back to the JSON file
    with open(json_filename, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

    return {
        "formatted_summary": formatted_summary
    }

def format_result_for_display(result):
    # Example: Convert the result dictionary into Markdown with LaTeX
    formatted_result = "### Extracted Problems and Solutions:\n\n"
    for i, item in enumerate(result, start=1):
        problem = item.get("problem", "No problem provided")
        solution = item.get("solution", "No solution provided")
        formatted_result += f"**Problem {i}:**\n"
        formatted_result += f"\\[\n{problem}\n\\]\n"
        formatted_result += f"**Solution:**\n"
        formatted_result += f"\\[\n{solution}\n\\]\n\n"
    return formatted_result

def process_text_math_problem(problem):
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        base_url=f"{azure_endpoint}/openai/deployments/{model}",
    )
    prompt = f"""You are an expert math assistant. Solve the following problem:
                {problem}
                Provide a detailed solution in plain text."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for solving math problems.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=2000,
        temperature=0.0,
    )
    response_content = response.choices[0].message.content.strip()
    return response_content

def process_img_llm_SAT(img_name):
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        base_url=f"{azure_endpoint}/openai/deployments/{model}",
    )
    prompt = """You are an expert SAT assistant designed to help students solve problems in Math, Critical Reading, and Writing. Your role is to analyze the input provided by the user, whether it is text or an image, and extract any problems. You will then solve the problems and provide detailed, step-by-step solutions or explanations. If the problem is a multiple-choice question, you will first state the correct answer and then provide a detailed explanation.

                Your responses should be clear, concise, and formatted in JSON for easy integration into applications. Use the following format for your responses:

                JSON Format:
                [
                    {
                        "problem": "<The problem statement>",
                        "solution": "<The detailed solution or explanation>"
                    }
                ]

                ### Examples:

                #### Example 1: Math Problem
                Input: "Solve x^2 + 2x - 8 = 0"
                Output:
                [
                    {
                        "problem": "Solve x^2 + 2x - 8 = 0",
                        "solution": "To solve the quadratic equation x^2 + 2x - 8 = 0, we factorize it as (x + 4)(x - 2) = 0. Therefore, the solutions are x = -4 and x = 2."
                    }
                ]

                #### Example 2: Critical Reading Problem
                Input: "Which of the following best describes the tone of the passage?"
                Options: (a) Optimistic, (b) Neutral, (c) Critical, (d) Nostalgic
                Output:
                [
                    {
                        "problem": "Which of the following best describes the tone of the passage?",
                        "solution": "The correct answer is (c) Critical. The passage uses language that critiques the subject matter, indicating a critical tone."
                    }
                ]

                #### Example 3: Writing Problem
                Input: "Choose the best revision for the following sentence: 'The dog, who was barking loudly, it scared the neighbors.'"
                Options: (a) The dog, who was barking loudly, scared the neighbors. (b) The dog who was barking loudly scared the neighbors. (c) The dog, barking loudly, scared the neighbors. (d) The dog it scared the neighbors, barking loudly.
                Output:
                [
                    {
                        "problem": "Choose the best revision for the following sentence: 'The dog, who was barking loudly, it scared the neighbors.'",
                        "solution": "The correct answer is (c) The dog, barking loudly, scared the neighbors. This revision eliminates redundancy and maintains grammatical correctness."
                    }
                ]

                #### Example 4: Image Input (Math Problem)
                Input: An image containing a math problem.
                Output:
                [
                    {
                        "problem": "What is the area of a triangle with a base of 10 cm and a height of 5 cm?",
                        "solution": "The area of a triangle is calculated as (1/2) × base × height. Substituting, (1/2) × 10 × 5 = 25 cm²."
                    }
                ]

                #### Example 5: Image Input (Critical Reading)
                Input: An image containing a passage with a question about the main idea.
                Output:
                [
                    {
                        "problem": "What is the main idea of the passage?",
                        "solution": "The main idea of the passage is that technological advancements have significantly improved communication efficiency over the past century."
                    }
                ]

                Always ensure your responses are accurate, detailed, and formatted in the specified JSON structure.
            """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant to analyze SAT problems.",
            },
            {
                "role": "user",
                "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": local_image_to_data_url(img_name)},
                        },
                ],
            },
        ],
        max_tokens=2000,
        temperature=0.0,
    )
    response_content = response.choices[0].message.content.strip()
    logging.debug(f"Response content: {response_content}")

    # Attempt to parse the response content as JSON
    try:
        response_json = json.loads(response_content)
        formatted_summary = format_result_for_display(response_json.get("detailed_solutions", []))
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse response as JSON: {e}")
        response_json = {"error": "Failed to parse response as JSON"}
        formatted_summary = response_content

    return {
        "formatted_summary": formatted_summary
    }

def process_text_SAT_problem(problem):
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        base_url=f"{azure_endpoint}/openai/deployments/{model}",
    )
    prompt = f"""You are an expert SAT assistant. Solve the following problem:
                {problem}
                Provide a detailed solution in plain text."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for solving SAT problems.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=2000,
        temperature=0.0,
    )
    response_content = response.choices[0].message.content.strip()
    return response_content

def process_img_llm_ACT(img_name):
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        base_url=f"{azure_endpoint}/openai/deployments/{model}",
    )
    prompt = """You are an expert ACT assistant designed to help students solve problems in Math, Reading, English, and Science. Your role is to analyze the input provided by the user, whether it is text or an image, and extract any problems. You will then solve the problems and provide detailed, step-by-step solutions or explanations. If the problem is a multiple-choice question, you will first state the correct answer and then provide a detailed explanation.

                Your responses should be clear, concise, and formatted in JSON for easy integration into applications. Use the following format for your responses:

                JSON Format:
                [
                    {
                        "problem": "<The problem statement>",
                        "solution": "<The detailed solution or explanation>"
                    }
                ]

                ### Examples:

                #### Example 1: Math Problem
                Input: "Solve 3x + 5 = 20"
                Output:
                [
                    {
                        "problem": "Solve 3x + 5 = 20",
                        "solution": "To solve the equation, subtract 5 from both sides: 3x = 15. Then divide by 3: x = 5."
                    }
                ]

                #### Example 2: Reading Problem
                Input: "What is the main idea of the passage?"
                Options: (a) The importance of teamwork, (b) The benefits of exercise, (c) The history of space exploration, (d) The challenges of modern technology
                Output:
                [
                    {
                        "problem": "What is the main idea of the passage?",
                        "solution": "The correct answer is (c) The history of space exploration. The passage discusses key milestones in space exploration and their significance."
                    }
                ]

                #### Example 3: English Problem
                Input: "Choose the best revision for the following sentence: 'The cat, who was sleeping on the couch, it woke up suddenly.'"
                Options: (a) The cat, who was sleeping on the couch, woke up suddenly. (b) The cat who was sleeping on the couch woke up suddenly. (c) The cat, sleeping on the couch, woke up suddenly. (d) The cat it woke up suddenly, sleeping on the couch.
                Output:
                [
                    {
                        "problem": "Choose the best revision for the following sentence: 'The cat, who was sleeping on the couch, it woke up suddenly.'",
                        "solution": "The correct answer is (c) The cat, sleeping on the couch, woke up suddenly. This revision eliminates redundancy and maintains grammatical correctness."
                    }
                ]

                #### Example 4: Science Problem
                Input: "What is the pH of a solution with a hydrogen ion concentration of 1 × 10^-4 M?"
                Output:
                [
                    {
                        "problem": "What is the pH of a solution with a hydrogen ion concentration of 1 × 10^-4 M?",
                        "solution": "The pH is calculated as -log[H+]. Substituting the concentration: pH = -log(1 × 10^-4) = 4."
                    }
                ]

                #### Example 5: Image Input (Math Problem)
                Input: An image containing a math problem.
                Output:
                [
                    {
                        "problem": "What is the area of a rectangle with a length of 8 cm and a width of 3 cm?",
                        "solution": "The area of a rectangle is calculated as length × width. Substituting, 8 × 3 = 24 cm²."
                    }
                ]

                #### Example 6: Image Input (Science Problem)
                Input: An image containing a graph of temperature vs. time with a question about the boiling point of a substance.
                Output:
                [
                    {
                        "problem": "What is the boiling point of the substance based on the graph?",
                        "solution": "The boiling point of the substance is the temperature at which the graph plateaus. Based on the graph, the boiling point is 100°C."
                    }
                ]

                Always ensure your responses are accurate, detailed, and formatted in the specified JSON structure.
            """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant to analyze ACT problems.",
            },
            {
                "role": "user",
                "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": local_image_to_data_url(img_name)},
                        },
                ],
            },
        ],
        max_tokens=2000,
        temperature=0.0,
    )
    response_content = response.choices[0].message.content.strip()
    logging.debug(f"Response content: {response_content}")

    # Attempt to parse the response content as JSON
    try:
        response_json = json.loads(response_content)
        formatted_summary = format_result_for_display(response_json.get("detailed_solutions", []))
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse response as JSON: {e}")
        response_json = {"error": "Failed to parse response as JSON"}
        formatted_summary = response_content

    return {
        "formatted_summary": formatted_summary
    }

def process_text_ACT_problem(problem):
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        base_url=f"{azure_endpoint}/openai/deployments/{model}",
    )
    prompt = f"""You are an expert ACT assistant. Solve the following problem:
                {problem}
                Provide a detailed solution in plain text."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for solving ACT problems.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=2000,
        temperature=0.0,
    )
    response_content = response.choices[0].message.content.strip()
    return response_content

def extract_qa_and_store(image_path: str):
    # 1) Define the prompt for extracting Q&A
    prompt = (
        "You are an expert assistant. "
        "Analyze the image and extract all question-and-answer pairs, including the answer choices. "
        "Return the result in valid JSON format like this: "
        '[{"question": "What is the capital of France?", "choices": ["Paris", "London", "Berlin", "Madrid"]}]'
    )

    # 2) Send the image and prompt to the AI model
    try:
        resp = qa_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You extract Q&A from images."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": local_image_to_data_url(image_path)}}
                    ]
                }
            ],
            temperature=0.0
        )
    except Exception as e:
        logging.error(f"Failed to get a response from the AI model: {e}")
        return {"error": "Failed to get a response from the AI model"}

    # 3) Parse the AI model's response
    try:
        if not resp.choices or not resp.choices[0].message.content:
            logging.error("AI model returned an empty response.")
            logging.error(f"Full AI response: {resp}")
            return {"error": "AI model returned an empty response"}
        
        # Extract the raw response content
        response_content = resp.choices[0].message.content.strip()
        logging.debug(f"Raw AI response content: {response_content}")

        # Remove code block markers (```json and ````)
        if response_content.startswith("```json"):
            response_content = response_content[7:]  # Remove the opening ```json
        if response_content.endswith("```"):
            response_content = response_content[:-3]  # Remove the closing ```

        # Extract only the JSON portion using regex
        json_match = re.search(r'\[.*\]', response_content, re.DOTALL)  # Match JSON array
        if not json_match:
            raise ValueError("No valid JSON array found in the AI response")

        json_str = json_match.group(0)  # Extract the JSON string
        logging.debug(f"Extracted JSON string: {json_str}")

        # Parse the JSON string
        qa_list = json.loads(json_str)

        # Validate that each Q&A pair contains the required fields
        for qa in qa_list:
            if "question" not in qa or "choices" not in qa:
                raise ValueError("Missing 'question' or 'choices' in AI response")
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Failed to parse AI response as JSON: {e}")
        logging.error(f"Full AI response: {resp}")
        return {"error": "Failed to parse AI response", "response": response_content if 'response_content' in locals() else None}

    # 4) Save the extracted Q&A to qa.json
    json_filename = 'qa.json'
    try:
        with open(json_filename, 'r') as json_file:
            existing_data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []  # Initialize as an empty list if the file doesn't exist or is invalid

    # Convert choices into a single string and append to the existing data
    for qa in qa_list:
        qa["answer"] = ", ".join(qa["choices"])  # Combine choices into a single string
        del qa["choices"]  # Remove the choices field

    if isinstance(existing_data, list):
        existing_data.extend(qa_list)
    else:
        existing_data = [existing_data] + qa_list

    with open(json_filename, 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)
    logging.info(f"Extracted Q&A saved to {json_filename}")

    # 5) Prepare documents for uploading to the Azure Cognitive Search index
    documents = []
    for qa in qa_list:
        try:
            doc_id = str(uuid.uuid4())
            documents.append({
                "id": doc_id,
                "question": qa["question"],
                "answer": qa["answer"]  # Store the combined choices as the answer
            })
        except KeyError as e:
            logging.error(f"Missing key in Q&A pair: {e}")
            continue

    # 6) Upload documents to the Azure Cognitive Search index
    try:
        result = search_client.upload_documents(documents)
        upload_status = [r.succeeded for r in result]
        logging.info(f"Uploaded {len(documents)} documents to the index with status: {upload_status}")
    except Exception as e:
        logging.error(f"Failed to upload documents to the index: {e}")
        return {"error": "Failed to upload documents to the index"}

    # 7) Return the extracted Q&A and upload status
    return {
        "extracted": qa_list,
        "vectorUpsert": upload_status
    }

# if __name__ == "__main__":
#     create_index()