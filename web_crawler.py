import requests
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup
import argparse
import sys
import warnings
import os

#  Removes the existing .png outputs if any
file_path = "Number.png"
file_patht ='Size.png'
if os.path.exists(file_path) and os.path.isfile(file_path):
    os.remove(file_path)
if os.path.exists(file_patht) and os.path.isfile(file_patht):
    os.remove(file_patht)

#  Ignores any unnecessary warnings while parsing HTML
warnings.filterwarnings("ignore")

#  Using argparse to add all arguments and get command line inputs
parser = argparse.ArgumentParser(description='Web Crawler')
parser.add_argument('-u', '--url', required=True, type=str,help='URl of the website to be crawled')
parser.add_argument('-t','--threshold',required=False,type=int,help='Threshold (depth of recursion)')
parser.add_argument('-o','--output',required=False,type=str,help='Output file')
parser.add_argument('-f','--filesize',required=False,type=str,help="'Y' for calculating filesize, 'n' for NO.")
parser.add_argument('-p','--progress',required=False,type=str,help="'Y' for showing progress, 'n' for NO.")
args = parser.parse_args()

site = args.url
threshold = args.threshold
#  Raises error if entered threshold value is invalid
if threshold is not None:
  if threshold<=0:
    raise ValueError("Invalid Threshold !!")
output_file = args.output
progress_display = args.progress
show_filesize = args.filesize

#  A function for obtaining the size of any file via a link
def get_file_size(url):
    try:
        response = requests.head(url, allow_redirects=True)
        size = int(response.headers.get('content-length', 0))
        return size
    except requests.exceptions.RequestException as e:
        return 0

#  Initializing all required data structures for storing appropriate manner, the names are self-explanatory
link_html = []
link_js = []
link_css = []
link_jpg = []
link_png = []
link_other = []
link_html_external = []
link_css_external = []
link_js_external = []
link_jpg_external = []
link_png_external = []
link_other_external = []
size_html = 0
size_css = 0
size_js = 0
size_jpg = 0
size_png = 0
size_other = 0
size_dict = {}

#  The main function which recursively calls the given link
def scrape_site(count, prime_link, curr_link, thresh):
  # print(1)
  if thresh is not None:
    if thresh == 0:
      count += 1
      if progress_display == "Y":
          sys.stdout.write("\r{0} links analysed till now.".format(count))
      return count
  
  if thresh is not None:
    thresh = thresh - 1
  
  static_link = []
  recurse_link = []

  # Using requests and beautifulSoup to parse the webpage
  r = requests.get(curr_link)
  s = BeautifulSoup(r.text,"lxml")
  href_tags = s.find_all(href=True)
  src_tags=s.find_all(src=True)

  # Getting all the links corresponding to href tags
  for tag in href_tags:
    
    href_value = tag['href']

    if href_value.startswith("//"):
      href_value = "http:" + href_value
    if href_value.startswith("http") and not href_value.startswith(prime_link):
      static_link.append(href_value)
    elif href_value.startswith("http") and href_value.startswith(prime_link):
      recurse_link.append(href_value)
    elif not href_value.startswith("http"):
      href_value = curr_link + href_value
      recurse_link.append(href_value)
    else:
      pass
  
  # Getting all the links corresponding to src tags
  for tag in src_tags:
    src_value = tag['src']
    if src_value.startswith("//"):
      src_value = "http:" + src_value
    elif src_value.startswith("http") and prime_link not in src_value:
      static_link.append(src_value)
    elif src_value.startswith("http") and prime_link in src_value:
      recurse_link.append(src_value)
    elif not src_value.startswith("http"):
      src_value = curr_link + src_value
      recurse_link.append(src_value)
    else:
      pass

  #  Removing multiple copies of links
  static_link = set(static_link)
  static_link = list(static_link)
  recurse_link = set(recurse_link)
  recurse_link = list(recurse_link)

  #  Appending the links to list of their respective file types
  for link in static_link:
    if ".html" in link:
      link_html_external.append(link)
    elif ".css" in link:
      link_css_external.append(link)
    elif ".js" in link:
      link_js_external.append(link)
    elif ".jpg" in link or "jpeg" in link:
      link_jpg_external.append(link)
    elif ".png" in link:
      link_png_external.append(link)
    else:
      link_other_external.append(link)
  
  # Recursively crawling through the links having the same domain as given links and which haven't been crawled before
  for link in recurse_link:
    if link not in (link_css+link_css_external+link_html+link_html_external+link_jpg+link_jpg_external+link_js+link_js_external+link_png+link_png_external+link_other+link_other_external):
      if ".html" in link:
        link_html.append(link)
      elif ".css" in link:
        link_css.append(link)
      elif ".js" in link:
        link_js.append(link)
      elif ".jpg" in link or "jpeg" in link:
        link_jpg.append(link)
      elif ".png" in link:
        link_png.append(link)
      else:
        link_other.append(link)
      try:
        count = scrape_site(count, prime_link, link, thresh)
      except:
        pass
  
  count += 1
  if progress_display == "Y":
    sys.stdout.write("\r{0} links analysed till now.".format(count))
  # Gives dynamic display of number of links analysed
  return count

#  Function used for getting the file sizes corresponding to all links
#  It can also dynamically updatee the user about the progress
def link_file_size(size_dict, size_html, size_css, size_js, size_jpg, size_png, size_other):
  for link in link_html:
    size_dict[link] = get_file_size(link)
    size_html = size_html + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\rSizes of internal HTML files found")
  for link in link_css:
    size_dict[link] = get_file_size(link)
    size_css = size_css + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\rSizes of internal HTML, CSS files found")
  for link in link_js:
    size_dict[link] = get_file_size(link)
    size_js = size_js + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\rSizes of internal HTML, CSS, JS files found")
  for link in link_jpg:
    size_dict[link] = get_file_size(link)
    size_jpg = size_jpg + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\rSizes of internal HTML, CSS, JS, JPG files found")
  for link in link_png:
    size_dict[link] = get_file_size(link)
    size_png = size_png + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\rSizes of internal HTML, CSS, JS, JPG, PNG files found")
  for link in link_other:
    size_dict[link] = get_file_size(link)
    size_other = size_other + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\nSizes of all internal files found\n")

  for link in link_html_external:
    size_dict[link] = get_file_size(link)
    size_html = size_html + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\rSizes of external HTML files found")
  for link in link_css_external:
    size_dict[link] = get_file_size(link)
    size_css = size_css + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\rSizes of external HTML, CSS files found")
  for link in link_js_external:
    size_dict[link] = get_file_size(link)
    size_js = size_js + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\rSizes of external HTML, CSS, JS files found")
  for link in link_jpg_external:
    size_dict[link] = get_file_size(link)
    size_jpg = size_jpg + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\rSizes of external HTML, CSS, JS, JPG files found")
  for link in link_png_external:
    size_dict[link] = get_file_size(link)
    size_png = size_png + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\rSizes of external HTML, CSS, JS, JPG, PNG files found")
  for link in link_other_external:
    size_dict[link] = get_file_size(link)
    size_other = size_other + size_dict[link]
  if progress_display == "Y":
    sys.stdout.write("\nSizes of all external files found")
  return size_dict, size_html, size_css, size_js, size_jpg, size_png, size_other

# Calling the main web crawling function
scrape_site(0, site, site, threshold)
if progress_display == "Y":
   sys.stdout.write("\nScraping done\n")

#  Determines file size if instructed to do so
if show_filesize == "Y":
  size_dict, size_html, size_css, size_js, size_jpg, size_png, size_other = link_file_size(size_dict, size_html, size_css, size_js, size_jpg, size_png, size_other)
  if progress_display == "Y":
    sys.stdout.write("\nFile size done\n")


# Removing multiple copies of links

link_html = set(link_html)
link_html = list(link_html)
link_css = set(link_css)
link_css = list(link_css)
link_js = set(link_js)
link_js = list(link_js)
link_jpg = set(link_jpg)
link_jpg = list(link_jpg)
link_png = set(link_png)
link_png = list(link_png)
link_other = set(link_other)
link_other = list(link_other)

link_html_external = set(link_html_external)
link_html_external = list(link_html_external)
link_css_external = set(link_css_external)
link_css_external = list(link_css_external)
link_js_external = set(link_js_external)
link_js_external = list(link_js_external)
link_jpg_external = set(link_jpg_external)
link_jpg_external = list(link_jpg_external)
link_png_external = set(link_png_external)
link_png_external = list(link_png_external)
link_other_external = set(link_other_external)
link_other_external = list(link_other_external)


#  Printing or storing appropriately 
if show_filesize == "Y" and output_file is not None:
    with open(args.output, "w") as file:

        file.write(f"\nTotal number of files found at {args.threshold} recursion: {len(link_html) + len(link_css) + len(link_js) + len(link_jpg) + len(link_png) + len(link_other) + len(link_html_external) + len(link_css_external) + len(link_js_external) + len(link_jpg_external) + len(link_png_external) + len(link_other_external)} (Internal : {len(link_html) + len(link_css) + len(link_js) + len(link_jpg) + len(link_png) + len(link_other)}, External : {len(link_html_external) + len(link_css_external) + len(link_js_external) + len(link_jpg_external) + len(link_png_external) + len(link_other_external)})")
        
        file.write(f"\n\nInternal HTML ({len(link_html)}) :")
        for i in link_html:
            file.write(f"\n{i} : {size_dict[i]}")
        file.write(f"\n\nInternal CSS ({len(link_css)}) :")
        for i in link_css:
            file.write(f"\n{i} : {size_dict[i]}")
        file.write(f"\n\nInternal JS ({len(link_js)}) :")
        for i in link_js:
            file.write(f"\n{i} : {size_dict[i]}")
        file.write(f"\n\nInternal JPG and JPEG ({len(link_jpg)}) :")
        for i in link_jpg:
            file.write(f"\n{i} : {size_dict[i]}")
        file.write(f"\n\nInternal PNG ({len(link_png)}) :")
        for i in link_png:
            file.write(f"\n{i} : {size_dict[i]}")
        file.write(f"\n\nInternal Others ({len(link_other)}) :")
        for i in link_other:
            file.write(f"\n{i} : {size_dict[i]}")

        file.write(f"\n\nExternal HTML ({len(link_html_external)}) :")
        for i in link_html_external:
            file.write(f"\n{i} : {size_dict[i]}")
        file.write(f"\n\nExternal CSS ({len(link_css_external)}) :")
        for i in link_css_external:
            file.write(f"\n{i} : {size_dict[i]}")
        file.write(f"\n\nExternal JS ({len(link_js_external)}) :")
        for i in link_js_external:
            file.write(f"\n{i} : {size_dict[i]}")
        file.write(f"\n\nExternal JPG and JPEG ({len(link_jpg_external)}) :")
        for i in link_jpg_external:
            file.write(f"\n{i} : {size_dict[i]}")
        file.write(f"\n\nExternal PNG ({len(link_png_external)}) :")
        for i in link_png_external:
            file.write(f"\n{i} : {size_dict[i]}")
        file.write(f"\n\nExternal Others ({len(link_other_external)}) :")
        for i in link_other_external:
            file.write(f"\n{i} : {size_dict[i]}")
elif output_file is not None:
    with open(args.output, "w") as file:

        file.write(f"\nTotal number of files found at {args.threshold} recursion: {len(link_html) + len(link_css) + len(link_js) + len(link_jpg) + len(link_png) + len(link_other) + len(link_html_external) + len(link_css_external) + len(link_js_external) + len(link_jpg_external) + len(link_png_external) + len(link_other_external)} (Internal : {len(link_html) + len(link_css) + len(link_js) + len(link_jpg) + len(link_png) + len(link_other)}, External : {len(link_html_external) + len(link_css_external) + len(link_js_external) + len(link_jpg_external) + len(link_png_external) + len(link_other_external)})")
        
        file.write(f"\n\nInternal HTML ({len(link_html)}) :")
        for i in link_html:
            file.write(f"\n{i}")
        file.write(f"\n\nInternal CSS ({len(link_css)}) :")
        for i in link_css:
            file.write(f"\n{i}")
        file.write(f"\n\nInternal JS ({len(link_js)}) :")
        for i in link_js:
            file.write(f"\n{i}")
        file.write(f"\n\nInternal JPG and JPEG ({len(link_jpg)}) :")
        for i in link_jpg:
            file.write(f"\n{i}")
        file.write(f"\n\nInternal PNG ({len(link_png)}) :")
        for i in link_png:
            file.write(f"\n{i}")
        file.write(f"\n\nInternal Others ({len(link_other)}) :")
        for i in link_other:
            file.write(f"\n{i}")

        file.write(f"\n\nExternal HTML ({len(link_html_external)}) :")
        for i in link_html_external:
            file.write(f"\n{i}")
        file.write(f"\n\nExternal CSS ({len(link_css_external)}) :")
        for i in link_css_external:
            file.write(f"\n{i}")
        file.write(f"\n\nExternal JS ({len(link_js_external)}) :")
        for i in link_js_external:
            file.write(f"\n{i}")
        file.write(f"\n\nExternal JPG and JPEG ({len(link_jpg_external)}) :")
        for i in link_jpg_external:
            file.write(f"\n{i}")
        file.write(f"\n\nExternal PNG ({len(link_png_external)}) :")
        for i in link_png_external:
            file.write(f"\n{i}")
        file.write(f"\n\nExternal Others ({len(link_other_external)}) :")
        for i in link_other_external:
            file.write(f"\n{i}")
elif show_filesize == "Y" and output_file is None:

        print(f"\nTotal number of files found at {args.threshold} recursion: {len(link_html) + len(link_css) + len(link_js) + len(link_jpg) + len(link_png) + len(link_other) + len(link_html_external) + len(link_css_external) + len(link_js_external) + len(link_jpg_external) + len(link_png_external) + len(link_other_external)} (Internal : {len(link_html) + len(link_css) + len(link_js) + len(link_jpg) + len(link_png) + len(link_other)}, External : {len(link_html_external) + len(link_css_external) + len(link_js_external) + len(link_jpg_external) + len(link_png_external) + len(link_other_external)})")
        
        print(f"\n\nInternal HTML ({len(link_html)}) :")
        for i in link_html:
            print(f"\n{i} : {size_dict[i]}")
        print(f"\n\nInternal CSS ({len(link_css)}) :")
        for i in link_css:
            print(f"\n{i} : {size_dict[i]}")
        print(f"\n\nInternal JS ({len(link_js)}) :")
        for i in link_js:
            print(f"\n{i} : {size_dict[i]}")
        print(f"\n\nInternal JPG and JPEG ({len(link_jpg)}) :")
        for i in link_jpg:
            print(f"\n{i} : {size_dict[i]}")
        print(f"\n\nInternal PNG ({len(link_png)}) :")
        for i in link_png:
            print(f"\n{i} : {size_dict[i]}")
        print(f"\n\nInternal Others ({len(link_other)}) :")
        for i in link_other:
            print(f"\n{i} : {size_dict[i]}")

        print(f"\n\nExternal HTML ({len(link_html_external)}) :")
        for i in link_html_external:
            print(f"\n{i} : {size_dict[i]}")
        print(f"\n\nExternal CSS ({len(link_css_external)}) :")
        for i in link_css_external:
            print(f"\n{i} : {size_dict[i]}")
        print(f"\n\nExternal JS ({len(link_js_external)}) :")
        for i in link_js_external:
            print(f"\n{i} : {size_dict[i]}")
        print(f"\n\nExternal JPG and JPEG ({len(link_jpg_external)}) :")
        for i in link_jpg_external:
            print(f"\n{i} : {size_dict[i]}")
        print(f"\n\nExternal PNG ({len(link_png_external)}) :")
        for i in link_png_external:
            print(f"\n{i} : {size_dict[i]}")
        print(f"\n\nExternal Others ({len(link_other_external)}) :")
        for i in link_other_external:
            print(f"\n{i} : {size_dict[i]}")
else:

        print(f"\nTotal number of files found at {args.threshold} recursion: {len(link_html) + len(link_css) + len(link_js) + len(link_jpg) + len(link_png) + len(link_other) + len(link_html_external) + len(link_css_external) + len(link_js_external) + len(link_jpg_external) + len(link_png_external) + len(link_other_external)} (Internal : {len(link_html) + len(link_css) + len(link_js) + len(link_jpg) + len(link_png) + len(link_other)}, External : {len(link_html_external) + len(link_css_external) + len(link_js_external) + len(link_jpg_external) + len(link_png_external) + len(link_other_external)})")
        
        print(f"\n\nInternal HTML ({len(link_html)}) :")
        for i in link_html:
            print(f"\n{i}")
        print(f"\n\nInternal CSS ({len(link_css)}) :")
        for i in link_css:
            print(f"\n{i}")
        print(f"\n\nInternal JS ({len(link_js)}) :")
        for i in link_js:
            print(f"\n{i}")
        print(f"\n\nInternal JPG and JPEG ({len(link_jpg)}) :")
        for i in link_jpg:
            print(f"\n{i}")
        print(f"\n\nInternal PNG ({len(link_png)}) :")
        for i in link_png:
            print(f"\n{i}")
        print(f"\n\nInternal Others ({len(link_other)}) :")
        for i in link_other:
            print(f"\n{i}")

        print(f"\n\nExternal HTML ({len(link_html_external)}) :")
        for i in link_html_external:
            print(f"\n{i}")
        print(f"\n\nExternal CSS ({len(link_css_external)}) :")
        for i in link_css_external:
            print(f"\n{i}")
        print(f"\n\nExternal JS ({len(link_js_external)}) :")
        for i in link_js_external:
            print(f"\n{i}")
        print(f"\n\nExternal JPG and JPEG ({len(link_jpg_external)}) :")
        for i in link_jpg_external:
            print(f"\n{i}")
        print(f"\n\nExternal PNG ({len(link_png_external)}) :")
        for i in link_png_external:
            print(f"\n{i}")
        print(f"\n\nExternal Others ({len(link_other_external)}) :")
        for i in link_other_external:
            print(f"\n{i}")


#  Storing the graphs generated in .png files

lists = [len(link_html)+len(link_html_external), len(link_css) + len(link_css_external), len(link_js)+len(link_js_external), len(link_jpg)+len(link_jpg_external), len(link_png)+len(link_png_external), len(link_other)+len(link_other_external)]
labels = ['HTML', 'CSS', 'JS', 'JPG', 'PNG', 'OTHERS']

sorted_indices = np.argsort(lists)[::-1]
lists = np.array(lists)[sorted_indices]
labels = np.array(labels)[sorted_indices]

fig, ax = plt.subplots(figsize=(8, 6))
y_pos = np.arange(len(lists))
bars = ax.barh(y_pos, lists, align='center', alpha=0.8)

for i, bar in enumerate(bars):
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
            labels[i], ha='left', va='center')

ax.set_xlabel('Number of Files')
ax.set_ylabel('File Types')
ax.set_title('Distribution of Different Files')

ax.invert_yaxis()

plt.tight_layout()
plt.savefig("Number.png")


# ******************************************************************************************************* #

if show_filesize == "Y":
    lists = [size_html, size_css, size_js, size_jpg, size_png, size_other]
    labels = ['HTML', 'CSS', 'JS', 'JPG', 'PNG', 'OTHERS']

    sorted_indices = np.argsort(lists)[::-1]
    lists = np.array(lists)[sorted_indices]
    labels = np.array(labels)[sorted_indices]

    fig, ax = plt.subplots(figsize=(8, 6))
    y_pos = np.arange(len(lists))
    bars = ax.barh(y_pos, lists, align='center', alpha=0.8)

    for i, bar in enumerate(bars):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                labels[i], ha='left', va='center')

    ax.set_xlabel('Total Size of Files')
    ax.set_ylabel('File Types')
    ax.set_title('Size Distribution of Different Files')

    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig("Size.png")
