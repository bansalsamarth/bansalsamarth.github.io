import os

def convert_file(input_dir, output_dir, template_path):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    source_files = os.listdir(input_dir)
    print(len(source_files), "files found in", input_dir)

    for file_name in source_files:
        source_path = os.path.join(input_dir, file_name)
        output_file_name = file_name[:-3] + ".html"
        output_path = os.path.join(output_dir, output_file_name)

        # Check if the output file needs to be updated
        if not os.path.exists(output_path) or os.path.getmtime(source_path) > os.path.getmtime(output_path):
            command = f"pandoc {source_path} -o {output_path} --template {template_path}"
            os.system(command)
            print(command)
            print(file_name, "...published\n")
        else:
            #print(file_name, "is up to date, skipping...\n")
            continue

# Adjusted directories and templates
convert_info = [
    # Assuming articles in 'drafts' are not ready for HTML conversion
    # ("SamarthBlog/drafts/", "path/to/output/for/drafts", "templates/draft-template.html"),
    ("SamarthBlog/migrations/", "blog/", "templates/post-template.html"),
    ("SamarthBlog/published/", "published/", "templates/published-article-template.html"),
]

for input_dir, output_dir, template_path in convert_info:
    convert_file(input_dir, output_dir, template_path)



pandoc {source_path} -o {output_path} --template {template_path}