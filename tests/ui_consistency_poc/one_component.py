import asyncio
import os
from next_gen_ui_agent import NextGenUIAgent
from next_gen_ui_agent.types import InputData
from next_gen_ui_llama_stack_embedded import init_inference_from_env


if True:
    # Ollama models:
    LLAMASTACK_CONFIG_PATH_DEFAULT = "tests/ai_eval_components/llamastack-ollama.yaml"
    #INFERENCE_MODEL_DEFAULT = "granite3.2:2b"
    #INFERENCE_MODEL_DEFAULT = "granite3.3:2b"
    INFERENCE_MODEL_DEFAULT="granite3.3:8b"
    #INFERENCE_MODEL_DEFAULT="ollama/llama3.2:latest"

else:
    # Gemini API models:
    LLAMASTACK_CONFIG_PATH_DEFAULT = "tests/ai_eval_components/llamastack-m.gemini.yaml"
    INFERENCE_MODEL_DEFAULT="gemini/gemini-2.0-flash-lite"
    #INFERENCE_MODEL_DEFAULT="gemini/gemini-2.0-flash"
    #INFERENCE_MODEL_DEFAULT="gemini/gemini-2.5-flash-lite"
    #INFERENCE_MODEL_DEFAULT="gemini/gemini-2.5-flash"
    os.environ["INFERENCE_MODEL"] = INFERENCE_MODEL_DEFAULT

BY_PREVIOUS_COMPONENT_PROMPT_PRFIX = '\nKeep UI component and its configuration consistent with previously shown '
BY_PREVIOUS_COMPONENT_PROMPT_SUFFIX = ' and only update it to match the "User Query" and "Data" if applicable pushing requested info up, otherwise replace it with another one.'

#TOYSTORY_DATA = '{"movie": {"title": "Toy Story", "pictureUrl": "https://example.com/poster.jpg", "imdb" : { "rating": 8.3 }, "countries": ["USA"], "actors": ["Tom Hanks", "Tim Allen", "Jim Varney", "Don Rickles"], "released": 1995}}'
TOYSTORY_DATA = '''{
    "movie": {
        "languages": [
            "English"
        ],
        "year": 1995,
        "pictureUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
        "runtime": 81,
        "movieId": "1",
        "imdb": {
            "votes": 591836,
            "id": "0114709",
            "rating": 8.3
        },
        "countries": [
            "USA",
            "Germany",
            "Czech Republic"
        ],
        "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
        "title": "Toy Story",
        "url": "https://themoviedb.org/movie/862",
        "revenue": 373554033,
        "tmdbId": "862",
        "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
        "released": "1995-11-22",
        "budget": 30000000
    },
    "actors": [
        "Jim Varney",
        "Tim Allen",
        "Tom Hanks",
        "Don Rickles"
    ]
}'''

PROMPT_MOVIE_INFO = "Show me basic info about Toy Story."
PROMPT_MOVIE_RELEASED = "When was the movie released?"
PROMPT_MOVIE_POSTER = "Show me the poster only."
PROMPT_MOVIE_SUBSCRIPTIONS = "Show me my subscriptions"

def open_results_file():
    """
    Generate a valid filename from INFERENCE_MODEL_DEFAULT and open it for writing.
    Keeps only the part after the last '/' and adds .txt suffix.
    If file exists, it will be replaced.
    Creates the file in the 'one_component_results' subfolder relative to this script's directory.
    
    Returns:
        file: Open file handle for writing
    """
    import os
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, 'one_component_results')
    
    # Create the subfolder if it doesn't exist
    os.makedirs(results_dir, exist_ok=True)
    
    # Extract the part after the last '/'
    filename = INFERENCE_MODEL_DEFAULT.split('/')[-1]
    # Add .txt suffix
    full_filename = os.path.join(results_dir, f"{filename}.txt")

    print(f"\nWriting results to {full_filename} ...\n")

    # Open file for writing, replacing if it exists
    return open(full_filename, 'w')

# open results file
results_file = open_results_file()

def print_response(title, llm_response):
    response_text = f"{title}{llm_response[0].model_dump_json(indent=2)}\n\n"
    print(response_text, end='')
    results_file.write(response_text)
    results_file.flush()
    
def print_header(title):
    header_text = f"{title}\n\n"
    print(header_text, end='')
    results_file.write(header_text)
    results_file.flush()

if __name__ == "__main__":

    inference = init_inference_from_env(
        default_model=INFERENCE_MODEL_DEFAULT,
        default_config_file=LLAMASTACK_CONFIG_PATH_DEFAULT,
    )

    agent = NextGenUIAgent(config = {"inference": inference, "unsupported_components": True})

    print_header("*** 1. Current: Info about Toy Story. Previous: subscriptions table - change of the data entity ***")

    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_INFO+BY_PREVIOUS_COMPONENT_PROMPT_PRFIX+"'table' with title 'My Subscriptions' and fields ['subscription.id', 'subscription.endDate']"+BY_PREVIOUS_COMPONENT_PROMPT_SUFFIX,
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response one previous component: ", llm_response)
    
    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_INFO,
            "previous_user_prompts": [PROMPT_MOVIE_SUBSCRIPTIONS],
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response multipleprevious prompts: ", llm_response)

    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_INFO,
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response no history: ", llm_response)

# ----------------- 2 -----------------
    print_header("*** 2. Current: When was the movie released? Previous: Info about Toy Story - additional info asked about data entity from previous conversation step ***")

    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_RELEASED+BY_PREVIOUS_COMPONENT_PROMPT_PRFIX+"'one-card' with title 'Toy Story' and fields ['movie.title', 'movie.pictureUrl', 'movie.imdb.rating', 'movie.imdb.year']"+BY_PREVIOUS_COMPONENT_PROMPT_SUFFIX,
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response one previous component: ", llm_response)

    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_RELEASED,
            "previous_user_prompts": [PROMPT_MOVIE_INFO],
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response multiple previous prompts: ", llm_response)
    
    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_RELEASED,
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response no history: ", llm_response)

# ----------------- 3 -----------------
    print_header("*** 3. Current: Show me the poster only. Previous: Info about Toy Story - the same data entity, but user prompt asks for different UI component  ***")

    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_POSTER+BY_PREVIOUS_COMPONENT_PROMPT_PRFIX+"'one-card' with title 'Toy Story' and fields ['movie.title', 'movie.released', 'movie.imdb.rating']"+BY_PREVIOUS_COMPONENT_PROMPT_SUFFIX,
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response one previous component: ", llm_response)
    
    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_POSTER,
            "previous_user_prompts": [PROMPT_MOVIE_INFO],
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response multiple previous prompts: ", llm_response)

    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_POSTER,
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response no history: ", llm_response)

# ----------------- 4 -----------------
    print_header("*** 4. Current: When was the movie released? Previous: Poster only, Info about Toy Story, Subscriptions table - multiple previous conversation steps including entity change and then component type change to another and back ***")

    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_RELEASED+BY_PREVIOUS_COMPONENT_PROMPT_PRFIX+"'image' with title 'Toy Story Poster' and fields ['movie.pictureUrl']"+BY_PREVIOUS_COMPONENT_PROMPT_SUFFIX,
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response one previous component: ", llm_response)
    
    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_RELEASED,
            "previous_user_prompts": [PROMPT_MOVIE_POSTER, PROMPT_MOVIE_INFO, PROMPT_MOVIE_SUBSCRIPTIONS],
            #"previous_user_prompts": [PROMPT_MOVIE_POSTER],
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response multiple previous prompts: ", llm_response)

    llm_response = asyncio.run(agent.component_selection(
        input={
            "user_prompt": PROMPT_MOVIE_RELEASED,
            "input_data": [InputData({"id": "1", "data": TOYSTORY_DATA})],
        },
    ))
    
    print_response("Response no history: ", llm_response)
    
