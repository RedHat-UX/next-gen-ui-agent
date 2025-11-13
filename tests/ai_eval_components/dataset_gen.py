import getopt
import json
import sys
from pathlib import Path

from ai_eval_components.types import (
    BASE_DATASET_PATH,
    BASE_MODULE_PATH,
    DATASET_FILE_SUFFIX,
    DatasetRow,
    ItemsGenerate,
)

BASE_DATASETSRC_PATH = BASE_MODULE_PATH + "dataset_src/"
BASE_DATASETSRC_SHAREDDATA_PATH = BASE_DATASETSRC_PATH + "backend_data_shared/"


def get_components_dirs(src_path):
    components_dir_path = Path.cwd() / (src_path + "/components/")
    components_dirs = [f for f in components_dir_path.iterdir() if f.is_dir()]
    components_dirs.sort()
    return components_dirs


def get_dataset_dir(dest_path):
    dataset_dir_path = Path.cwd() / dest_path
    print(f"Writing dataset into folder: {dataset_dir_path}")
    if not dataset_dir_path.exists():
        dataset_dir_path.mkdir(parents=True)
    else:
        [
            f.unlink()
            for f in dataset_dir_path.iterdir()
            if f.is_file() and f.match("*" + DATASET_FILE_SUFFIX)
        ]
    return dataset_dir_path


def load_component_items_generate_file(component_dir: Path):
    items_generate: list[ItemsGenerate]

    filepath = component_dir / "items_generate.json"
    with filepath.open("r") as f:
        items_generate = json.load(f)

    return items_generate


def read_prompts(component_dir, prompts_file_name):
    prompts_file = component_dir / prompts_file_name
    with prompts_file.open("r") as f:
        prompts = json.load(f)
    return prompts


def load_backend_data(
    backend_data_file_name: str, component_dir: Path, shared_data_dir_path: Path
):
    component_data_path = component_dir / "backend_data/" / backend_data_file_name
    shared = False
    if component_data_path.exists() and component_data_path.is_file():
        with component_data_path.open("r") as f:
            backend_data = f.read()
    else:
        shared_data_path = shared_data_dir_path / backend_data_file_name
        if shared_data_path.exists() and shared_data_path.is_file():
            with shared_data_path.open("r") as f:
                backend_data = f.read()
                shared = True
        else:
            print(
                f"Backend data file {backend_data_file_name} not found in any location"
            )
            raise FileNotFoundError()
    return backend_data, shared


def get_component_items_prompt_files(component_dir: Path):
    items_dir_path = component_dir / "items/"
    if not items_dir_path.exists():
        return []
    prompt_files = [
        f for f in items_dir_path.iterdir() if f.is_file() and f.match("*.txt")
    ]
    prompt_files.sort()
    return prompt_files


def write_dataset_file(dataset_dir_path, component_name, file_index, dataset):
    dataset_file_path = dataset_dir_path / f"{component_name}-{file_index}.json"
    print(f"Writing dataset file '{dataset_file_path.name}'")
    with dataset_file_path.open("a") as f:
        json.dump(dataset, f, indent=2, separators=(",", ": "))


def print_help():
    """Print help message for command line arguments."""
    print("dataset_gen.py [options]")
    print("\nOptions:")
    print(
        "  -s, --src <path>   Source directory (default: tests/ai_eval_components/dataset_src/)"
    )
    print(
        "  -d, --dest <path>  Destination directory (default: tests/ai_eval_components/dataset/)"
    )
    print("  -h                 Show this help message")


def load_config():
    """
    Load configuration from command line arguments.

    Returns:
        tuple: (src_path, dest_path) - source and destination directory paths
    """
    src_path = BASE_MODULE_PATH + "dataset_src/"
    dest_path = BASE_DATASET_PATH
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:d:", ["src=", "dest="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print_help()
            sys.exit()
        elif opt in ("-s", "--src"):
            src_path = arg
        elif opt in ("-d", "--dest"):
            dest_path = arg

    return src_path, dest_path


if __name__ == "__main__":
    src_path, dest_path = load_config()

    print("Dataset generation started...")
    print(f"Source directory: {src_path}")
    print(f"Destination directory: {dest_path}")

    dataset_dir_path = get_dataset_dir(dest_path)
    shared_data_dir_path = Path.cwd() / (src_path + "backend_data_shared/")
    components_dirs = get_components_dirs(src_path)

    for component_dir in components_dirs:
        component_name = component_dir.name
        id_per_component = 0
        print(f"\nGenerating dataset for UI component '{component_name}'")

        print("Processing 'items_generate.json'...")
        items_generate = load_component_items_generate_file(component_dir)

        for i, item_generate in enumerate(items_generate):
            dataset: list[DatasetRow] = []

            prompts_file_name = item_generate["prompts_file"]
            print(f"Reading user prompts from '{prompts_file_name}'")
            prompts = read_prompts(component_dir, prompts_file_name)

            for backend_data_file_name in item_generate["backend_data_files"]:
                backend_data, shared = load_backend_data(
                    backend_data_file_name, component_dir, shared_data_dir_path
                )
                # validate backend data JSON
                try:
                    json.loads(backend_data)
                except json.decoder.JSONDecodeError as e:
                    print(
                        f"Backend data in '{backend_data_file_name}' are not valid JSON"
                    )
                    raise e
                for prompt in prompts:
                    id_per_component += 1
                    dataset_row = DatasetRow()  # type: ignore
                    dataset_row["id"] = f"{component_name}-{id_per_component:06d}"
                    dataset_row["user_prompt"] = prompt
                    dataset_row["backend_data"] = backend_data
                    if "input_data_type" in item_generate:
                        dataset_row["input_data_type"] = item_generate[
                            "input_data_type"
                        ]
                    dataset_row["expected_component"] = component_name
                    dataset_row["warn_only"] = item_generate.get("warn_only", False)
                    if shared:
                        df = "backend_data_shared/" + backend_data_file_name
                    else:
                        df = backend_data_file_name
                    dataset_row["src"] = {
                        "data_file": df,
                        "prompt_file": prompts_file_name,
                    }
                    dataset.append(dataset_row)

            write_dataset_file(dataset_dir_path, component_name, i + 1, dataset)

        prompt_files = get_component_items_prompt_files(component_dir)
        if len(prompt_files) > 0:
            print("Processing individual '/items/'...")
            dataset = []
            for prompt_file in prompt_files:
                id_per_component += 1
                dataset_row = DatasetRow()  # type: ignore
                dataset_row["id"] = f"{component_name}-{id_per_component:06d}"
                with prompt_file.open("r") as f:
                    dataset_row["user_prompt"] = f.read()
                data_file = component_dir / (
                    "items/" + prompt_file.name.replace(".txt", ".json")
                )
                with data_file.open("r") as f:
                    backend_data = f.read()
                    # validate backend data JSON
                    try:
                        json.loads(backend_data)
                    except json.decoder.JSONDecodeError as e:
                        print(f"Backend data in '{data_file}' are not valid JSON")
                        raise e
                    dataset_row["backend_data"] = backend_data
                dataset_row["expected_component"] = component_name
                dataset_row["src"] = {
                    "data_file": "items/" + data_file.name,
                    "prompt_file": "items/" + prompt_file.name,
                }
                dataset.append(dataset_row)

            write_dataset_file(dataset_dir_path, component_name, 0, dataset)
