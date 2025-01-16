import socket
import threading
import json
import sqlite3

SEND_PORT = 13000
RECEIVE_PORT = 13001
BUFSIZE = 4096

# 受信リクエストを時の関数
def accept_receive(server):
    try:
    # ソケットからデータを受け取って，プロトコルに従って情報を取り出す
        client, address = server.accept()
        data = client.recv(BUFSIZE)
        print(f"Raw data received (bytes): {data}")
        decoded_data = data.decode("UTF-8")
        print(f"Decoded data (str): {decoded_data}")
        request = json.loads(decoded_data)

        to_user = request["to"]
        response = read_message(to_user)
        client.sendall(response.encode("UTF-8"))
    except KeyboardInterrupt:  # Ctrl + C を押した場合の処理
        print("ソケットを解放します")
        server.close()  # ソケット接続を終了
    finally:  # その他の例外発生時の処理
        server.close()  # ソケット接続を終了


# 送信リクエストを時の関数
def accept_send(server):
    # ソケットからデータを受け取って，プロトコルに従って情報を取り出す
    try:
        client, address = server.accept()
        data = client.recv(BUFSIZE)
        print(f"Raw data received (bytes): {data}")
        decoded_data = data.decode("UTF-8")  # デコード結果を変数に代入
        print(f"Decoded data (str): {decoded_data}")
        request = json.loads(decoded_data)

        to_user = request["to"]
        from_user = request["from"]
        content = request["message"]
        response = write_message(from_user, to_user, content)
        client.sendall(response.encode("UTF-8"))
    except KeyboardInterrupt:  # Ctrl + C を押した場合の処理
        print("ソケットを解放します")
        server.close()  # ソケット接続を終了
    finally:  # その他の例外発生時の処理
        server.close()  # ソケット接続を終了


# 送信リクエストの内容を DB に書き込む関数
def write_message(from_user: str, to_user: str, content: str):
    try:
        conn = sqlite3.connect("messageing_dev.db")
        cur = conn.cursor()
        sql = "INSERT INTO messages (from_user, to_user, content) VALUES (?, ?, ?)"
        cur.execute(sql, (from_user, to_user, content))
        conn.commit()

        response = "Message received! Thank you!\n"
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        response = json.dumps({"error": str(e)})
    except Exception as e:
        print(f"Error: {e}")
        response = json.dumps({"error": str(e)})
    finally:
        cur.close()
        conn.close()
        return response


# 受信リクエストの内容を DB からメッセージを取得する関数
def read_message(to_user: str):
    conn = sqlite3.connect("message_dev.db")
    sql = "SELECT * FROM messages"
    cur = conn.cursor()
    cur.execute(sql)
    messages = cur.fetchall()
    return messages

# ソケットを開く
send_server = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM
)
receive_server = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM
)

send_server.bind(("",SEND_PORT))
receive_server.bind(("",RECEIVE_PORT))

send_server.listen()
receive_server.listen()

s_thread = threading.Thread(target=accept_send,args=(send_server,))
r_thread = threading.Thread(target=accept_receive,args=(receive_server,))
s_thread.start()
r_thread.start()
s_thread.join()
r_thread.join()