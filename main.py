import requests 
import os
import sys


token_path = os.path.join(os.path.dirname(os.path.abspath(os.path.join(sys.executable, os.pardir))), "token")
download_path = os.getcwd()

HEADERS = None

def check_token(token):
    HEADERS = {
        "Authorization": "Bearer " + token
    }
    try:
        r = requests.get("https://api.github.com/user", headers=HEADERS)
    except:
        print("Could not connect to GitHub. Please check your internet connection")
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
        print("Token is invalid or expired. Please set a new token using the command 'set-token <token>'")


def download_file(url, file_path, size=0):
    print(f'File path: {file_path}')
    save_path = os.path.join(download_path, file_path)
    file_name = save_path.split("/")[-1]
    # check if file already exists
    if os.path.exists(save_path):
        if size == os.path.getsize(save_path):
            print(f'File {file_name} already exists')
            return
        
    # DOWNLOAD FILE
    print(f'Downloading {file_path}...')
    # get file
    r = requests.get(url, headers=HEADERS, allow_redirects=True)
    # save file
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    open(save_path, 'wb').write(r.content)

def get_content(url):
    try:
        content = requests.get(url, headers=HEADERS).json()
    except:
        print("Please provide a valid url")
        sys.exit(0)
    try:
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
                # do not create a folder for the root directory
                path = path.replace(path.split("/")[0] + "/", "")
                size = i["size"]
                url = i["download_url"]
                download_file(url, path, size)
    except:
        print(content['message'])
        print("Possible solution:")
        print("1. Set a valid token using the command 'set-token <token>'")
        print("2. Wait for 60 minutes and try again (rate limit is 60 requests per hour)")
        sys.exit(0)


if __name__ == "__main__":

    # get command
    try:
        command = sys.argv[1]
        match command:
            case "get":
                try:
                    url = sys.argv[2]
                except IndexError:
                    print("Please provide a url")
                    sys.exit(0)
                       
                try:
                    ignore_files_str = sys.argv[3].replace(" ", "")
                    ignore_files = ignore_files_str.split(";")
                    print("Ignoring files: " + ", ".join(ignore_files))
                except:
                    ignore_files = None

                url = url.replace("github.com", "api.github.com/repos")
                url = url.replace("tree/main", "contents")
                
                get_content(url)

            case "set-token":
                try:
                    token = sys.argv[2]
                    token_file = open(token_path, "w")
                    token_file.write(token)
                    token_file.close()
                    print("Token set successfully")

                except Exception as e:
                    if isinstance(e, IndexError):
                        print("Please provide a token")
                    elif isinstance(e, PermissionError):
                        print("Please run the script as an administrator")
                    else:
                        pass

            case "remove-token":
                try:
                    os.remove(token_path)
                    print("Token removed successfully")
                except Exception as e:
                    if isinstance(e, FileNotFoundError):
                        print("Token not found")
                    elif isinstance(e, PermissionError):
                        print("Please run the script as an administrator")
                    else:
                        pass
            
            case "help":
                print("Commands:")
                print("get <url> <ignore-files>(split by ';', optional)")
                print("set-token <token>(optional)")
                print("remove-token")
                print("help")
            case _:
                print("Please provide a valid command")
    except IndexError:
        print("Please provide a command")

    sys.exit(0)
