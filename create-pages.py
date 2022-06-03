import os

file_list = os.listdir("SamarthBlog/published/")
print(len(file_list))

for file_name in file_list:
    os.system("pandoc SamarthBlog/published/" + file_name + " -o blog/" + file_name[:-3] + ".html --template templates/post-template.html")
    print("pandoc SamarthBlog/published/" + file_name + "-o blog/" + file_name[:-3] + ".html --template templates/post-template.html")
    print(file_name, "...published", "\n\n")
