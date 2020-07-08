import pathlib
import sys
from tqdm import tqdm

def calculate_mapping(source, dest):
    mapping = {}
    total_size = 0
    remove = []
    for filepath in source.glob('**/*'):
        if filepath.is_file():
            relative_path = filepath.relative_to(source.parent)
            dest_path = dest / relative_path
            if not dest_path.exists() or dest_path.stat().st_size != filepath.stat().st_size:
                mapping[filepath] = dest_path
                total_size += filepath.stat().st_size
            else:
                remove.append(filepath)
    return mapping, remove, total_size

def remove_empty_tree(path):
    contents = tuple(path.iterdir())
    if len(contents) == 0:
        path.rmdir()
        remove_empty_tree(path.parent)

if __name__ == '__main__':
    source = pathlib.Path(sys.argv[1])
    dest = pathlib.Path(sys.argv[2])
    
    mapping, files_to_remove, total_size = calculate_mapping(source, dest)
    for filepath in files_to_remove:
        filepath.unlink()
        remove_empty_tree(filepath.parent)

    with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as progress_bar:
        for source_file in mapping:
            dest_file = mapping[source_file]
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            with open(source_file, 'rb') as f_in, open(dest_file, 'wb') as f_out:
                chunk = f_in.read(4 * 1024 * 1024)
                while chunk:
                    f_out.write(chunk)
                    progress_bar.update(len(chunk))
                    chunk = f_in.read(4 * 1024 * 1024)
            source_file.unlink()
            remove_empty_tree(source_file.parent)
