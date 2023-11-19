import requests 
import os
import sys
import re
from colorama import Fore, init
from tqdm import tqdm

init(autoreset=True)

token_path = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "token")
download_path = os.getcwd()
ignore_files = None
HEADERS = None
IS_SUBDIR = False

def check_token(token):
    HEADERS = {
        "Authorization": "Bearer " + token
    }
    try:
        r = requests.get("https://api.github.com/user", headers=HEADERS)
    except:
        print(Fore.LIGHTRED_EX + "Could not connect to GitHub. Please check your internet connection")
        sys.exit(0)
    if r.status_code == 200:
        return True
    else:
        return False

# update headers if token exists
if os.path.exists(os.path.join(os.path.dirname(token_path), "token")):
    token_file = open(os.path.join(os.path.dirname(token_path), "token"), "r")
    token = token_file.read()
    token_file.close()
    if check_token(token):
        HEADERS = {
            "Authorization": "Bearer " + token
        }
    else:
        print(Fore.LIGHTRED_EX + "Token is invalid or expired. Please set a new token using the command 'set-token <token>'")



def download_file(url, file_path, size=0):
    save_path = os.path.join(download_path, file_path)
    # check if file already exists
    if os.path.exists(save_path):
        if size == os.path.getsize(save_path):
            print(f'{Fore.GREEN}File {Fore.RESET}{file_path}{Fore.GREEN} already exists')
            return

    # DOWNLOAD FILE
    print(f'{Fore.LIGHTGREEN_EX}Downloading {Fore.RESET + file_path}...')
    # get file
    r = requests.get(url, headers=HEADERS, stream=True)


    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    if r.status_code == 200:
        with open(save_path, 'wb') as f:
            progress_bar = tqdm(total=size, unit='iB', unit_scale=True, colour="green")
            for data in r.iter_content(chunk_size=1024):
                f.write(data)
                progress_bar.update(len(data))
            progress_bar.close()
            if size != 0 and progress_bar.n != size:
                print(Fore.LIGHTRED_EX + "ERROR, something went wrong")
    else:
        print(f'{Fore.LIGHTRED_EX}Failed to download {file_path}. Status code: {r.status_code}')

def get_content(url):
    try:
        content = requests.get(url, headers=HEADERS).json()
    except:
        print(Fore.LIGHTYELLOW_EX + "Please provide a valid url")
        sys.exit(0)

    # if content is list(multiple files)
    try:
        if isinstance(content, list):
            for i in content:
                if ignore_files:
                    # remove the root folder from the path
                    ignore_path = "/".join(i["path"].split("/")[1:])
                    if ignore_path in ignore_files:
                        continue
                if i["type"] == "dir":
                    get_content(i["url"])
                else:
                    path = i["path"]

                    # replace the root folder with the current directory, only if it is a subdirectory of a repository
                    if IS_SUBDIR:
                        path = path.replace(path.split("/")[0] + "/", "")

                    size = i["size"]
                    url = i["download_url"]
                    download_file(url, path, size)

        # if content is dict(single file)
        elif isinstance(content, dict):
            if ignore_files:
                # remove the root folder from the path
                ignore_path = "/".join(content["path"].split("/")[1:])
                if ignore_path in ignore_files:
                    return
            path = content["path"]
            # replace the root folder with the current directory, only if it is a subdirectory of a repository
            path = path.split('/')[-1]
                
            print(path)
            # path = path.replace(path.split("/")[0] + "/", "")
            size = content["size"]
            url = content["download_url"]
            download_file(url, path, size)
    except:
        try:
            print(Fore.LIGHTRED_EX + f'Error occured:' + content['message'])
        except:
            print(Fore.LIGHTRED_EX + "An unknown error occured")
        
        print(Fore.LIGHTYELLOW_EX + "Possible solution:")
        print(Fore.LIGHTYELLOW_EX + "1. Set a valid token using the command 'set-token <token>'")
        print(Fore.LIGHTYELLOW_EX + "2. Wait for 60 minutes and try again (rate limit is 60 requests per hour)")
        sys.exit(0)

def main():
    global ignore_files, IS_SUBDIR


    # get command
    try:
        command = sys.argv[1]
        match command:
            case "get":
                try:
                    url = sys.argv[2]
                except IndexError:
                    print(Fore.LIGHTYELLOW_EX + "Please provide a url")
                    sys.exit(0)
                       
                try:
                    # get the ignore files
                    ignore_files_str = sys.argv[3].replace(" ", "")
                    ignore_files = ignore_files_str.split(";")
                    print(Fore.LIGHTYELLOW_EX + "Ignoring files: "+ Fore.RESET + ", ".join(ignore_files) + Fore.RESET)
                except:
                    ignore_files = None

                url = url.replace("github.com", "api.github.com/repos")

                try:
                    # get the name of the repository
                    tree_name = re.findall(r"\/tree\/[^\/]*\/?", url)[0]
                    tree_pos = url.find(tree_name)

                    # check if the url is a subdirectory of a repository, used to remove the root folder from the path
                    IS_SUBDIR = tree_pos+len(tree_name) != len(url)
                    # replace tree/BRANCH/ with contents/
                    url = re.sub(r"tree\/.*?\/", "contents/", url)
                except:
                    # single file
                    url = re.sub(r"blob\/.*?\/", "contents/", url)

                get_content(url)
                print(Fore.LIGHTGREEN_EX + "Download complete")

            case "set-token":
                try:
                    token = sys.argv[2]
                    token_file = open(token_path, "w")
                    token_file.write(token)
                    token_file.close()
                    print(Fore.LIGHTYELLOW_EX + "Token set successfully")

                except Exception as e:
                    if isinstance(e, IndexError):
                        print(Fore.LIGHTYELLOW_EX + "Please provide a token")
                    elif isinstance(e, PermissionError):
                        print(Fore.LIGHTYELLOW_EX + "Please run the script as an administrator")
                    else:
                        pass

            case "remove-token":
                try:
                    os.remove(token_path)
                    print(Fore.LIGHTYELLOW_EX + "Token removed successfully")
                except Exception as e:
                    if isinstance(e, FileNotFoundError):
                        print(Fore.LIGHTYELLOW_EX + "Token not found")
                    elif isinstance(e, PermissionError):
                        print(Fore.LIGHTYELLOW_EX + "Please run the script as an administrator")
                    else:
                        pass
            
            case "help":
                print(Fore.LIGHTYELLOW_EX + "Commands:")
                print(Fore.LIGHTYELLOW_EX + "get <url> <ignore-files>(split by ';', optional)")
                print(Fore.LIGHTYELLOW_EX + "set-token <token>(optional)")
                print(Fore.LIGHTYELLOW_EX + "remove-token")
                print(Fore.LIGHTYELLOW_EX + "help")
            case _:
                print(Fore.LIGHTYELLOW_EX + "Please provide a valid command, type 'downgit help' for more info")
    except IndexError:
        print(Fore.LIGHTYELLOW_EX + "Please provide a command, type 'downgit help' for more info")

    sys.exit(0)


if __name__ == "__main__":
    main()
    