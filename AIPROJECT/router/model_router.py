# import time

# from models.ollama_model import OllamaModel
# from logger.logger import log_request

# model = OllamaModel()


# # ------------------------------------
# # Task Classification
# # ------------------------------------
# def classify_task(query):

#     prompt = f"""
# You are an AI classifier.

# Classify the request into ONLY one category:

# simple
# summary
# complex

# Request:
# {query}

# Return only one word:
# simple
# summary
# complex
# """

#     result = model.small_model(prompt)

#     print("Classifier Result:", result)

#     if result.get("success"):

#         category = result.get("response", "").strip().lower()

#     else:

#         category = "complex"

#     if "summary" in category:
#         return "summary"

#     elif "complex" in category:
#         return "complex"

#     else:
#         return "simple"


# # ------------------------------------
# # Select Model
# # ------------------------------------
# def select_model(task_type):

#     if task_type == "simple":
#         return model.small

#     elif task_type == "summary":
#         return model.medium

#     else:
#         return model.large


# # ------------------------------------
# # Main Router
# # ------------------------------------
# def route_request(query, agent_name="General"):

#     start = time.time()

#     task_type = classify_task(query)

#     selected_model = select_model(task_type)

#     print("Task Type :", task_type)
#     print("Selected Model :", selected_model)

#     result = model.generate(selected_model, query)

#     print("Model Output :", result)

#     latency = round(time.time() - start, 2)

#     if not result.get("success"):

#         response = f"❌ Model Error:\n{result.get('response')}"

#     else:

#         response = result.get("response", "")

#         if response.strip() == "":

#             response = "⚠️ Model returned an empty response."

#     try:

#         log_request(
#             agent=agent_name,
#             model=selected_model,
#             input_text=query,
#             output_text=response,
#             latency=latency
#         )

#     except Exception as e:

#         print("Logger Error:", e)

#     return {

#         "success": result.get("success", False),

#         "response": response,

#         "model": selected_model,

#         "latency": latency,

#         "task_type": task_type

#     }