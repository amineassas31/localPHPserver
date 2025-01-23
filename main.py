import os
import socket
import subprocess


def colorful_intro():
    red = "\033[91m"
    green = "\033[92m"
    yellow = "\033[93m"
    blue = "\033[94m"
    bold = "\033[1m"
    reset = "\033[0m"

    intro = f"""
{red}{bold} █████╗ ███╗   ███╗██╗███╗   ██╗███████╗{reset}
{yellow}██╔══██╗████╗ ████║██║████╗  ██║██╔════╝{reset}
{green}███████║██╔████╔██║██║██╔██╗ ██║█████╗  {reset}
{blue}██╔══██║██║╚██╔╝██║██║██║╚██╗██║██╔══╝  {reset}
{red}██║  ██║██║ ╚═╝ ██║██║██║ ╚████║███████╗{reset}
{yellow}╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝{reset}
{bold}{green}Welcome to AMINE's localPHPserver!{reset}
"""
    print(intro)


colorful_intro()


def handle_request(client_socket):
    try:
        request = client_socket.recv(1024).decode('utf-8', errors='ignore')
        if not request:
            return

        request_line = request.split('\n')[0]
        path = request_line.split()[1] if request_line else '/'

        cleaned_path = path.split('?')[0]
        php_file_path = os.path.join('www', cleaned_path.lstrip('/'))

        if cleaned_path == '/':
            php_file_path = os.path.join('www', 'index.php')

        php_executable = 'php8.2.0/php.exe'

        if os.path.exists(php_file_path) and php_file_path.endswith('.php'):
            try:
                result = subprocess.run(
                    [php_executable, php_file_path],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                if result.returncode == 0:
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n{result.stdout}"
                else:
                    response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{result.stderr}"
            except Exception as e:
                response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{str(e)}"
        else:
            response = 'HTTP/1.1 404 Not Found\r\n\r\n'

        client_socket.send(response.encode('utf-8'))
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        client_socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8080))
server_socket.listen(5)
print("Server is running on http://localhost:8080")

try:
    while True:
        client_socket, client_address = server_socket.accept()

        handle_request(client_socket)
except KeyboardInterrupt:
    print("Shutting down the server...")
finally:
    server_socket.close()
