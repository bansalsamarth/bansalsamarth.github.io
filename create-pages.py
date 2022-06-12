import os

pub_file_list = os.listdir("SamarthBlog/published/")
print(len(pub_file_list))

for file_name in pub_file_list:
    os.system("pandoc SamarthBlog/published/" + file_name + " -o blog/" + file_name[:-3] + ".html --template templates/post-template.html")
    print("pandoc SamarthBlog/published/" + file_name + "-o blog/" + file_name[:-3] + ".html --template templates/post-template.html")
    print(file_name, "...published", "\n\n")

migration_file_list = os.listdir("SamarthBlog/migrations/")
print(len(migration_file_list))

for file_name in migration_file_list:
    os.system("pandoc SamarthBlog/migrations/" + file_name + " -o ./" + file_name[:-3] + ".html --template templates/post-template.html")
    print("pandoc SamarthBlog/migrations/" + file_name + " -o ./" + file_name[:-3] + ".html --template templates/post-template.html")
    print(file_name, "...published", "\n\n")

published_file_list = os.listdir("SamarthBlog/published-articles/")
print(len(published_file_list))

for file_name in published_file_list:
    os.system("pandoc SamarthBlog/published-articles/" + file_name + " -o published/" + file_name[:-3] + ".html --template templates/published-article-template.html")
    print("pandoc SamarthBlog/published-articles/" + file_name + " -o published/" + file_name[:-3] + ".html --template templates/published-article-template.html")
    print(file_name, "...published", "\n\n")
