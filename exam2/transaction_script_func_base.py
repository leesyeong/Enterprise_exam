import sqlite3
from enum import Enum
from datetime import datetime

# 권한 Enum
class Grant(Enum):
    ADMIN = 0
    SUB_ADMIN = 1
    USER = 2

# DB 접속 함수
def get_connection(db_name="MemberManagement.db"):
    return sqlite3.connect(db_name)

# 테이블 존재 여부 확인 함수
def ensure_table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    table_exists = cursor.fetchone()
    return table_exists is not None

# 트랜잭션 스크립트: 멤버 관련
def find_member(conn, nick_name):
    cursor = conn.cursor()
    cursor.execute("SELECT kakao_nick_name, join_date, grant, last_login, score FROM member WHERE nick_name = ?", (nick_name,))
    return cursor.fetchone()

def create_member(conn, nick_name, kakao_nick_name, join_date, grant, last_login, score):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO member (nick_name, kakao_nick_name, join_date, grant, last_login, score) VALUES (?, ?, ?, ?, ?, ?)", 
                   (nick_name, kakao_nick_name, join_date, grant, last_login, score))
    conn.commit()

def update_grant(conn, nick_name, grant):
    cursor = conn.cursor()
    cursor.execute("UPDATE member SET grant = ? WHERE nick_name = ?", (grant.value, nick_name))
    conn.commit()

def update_last_login(conn, nick_name, last_login):
    cursor = conn.cursor()
    cursor.execute("UPDATE member SET last_login = ? WHERE nick_name = ?", (last_login, nick_name))
    conn.commit()

def update_score(conn, nick_name, score):
    cursor = conn.cursor()
    cursor.execute("UPDATE member SET score = ? WHERE nick_name = ?", (score, nick_name))
    conn.commit()

def delete_member(conn, nick_name):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM member WHERE nick_name = ?", (nick_name,))
    conn.commit()

# 트랜잭션 스크립트: 컨텐츠 레코드 관련
def find_content_record(conn, content_name, start_date, nick_name):
    table_name = f"{content_name}_{start_date}"
    cursor = conn.cursor()
    cursor.execute(f"SELECT score, participation_count, day FROM {table_name} WHERE nick_name = ?", (nick_name,))
    return cursor.fetchall()

def insert_content_record(conn, content_name, start_date, nick_name, score, participation_count, day):
    table_name = f"{content_name}_{start_date}"
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table_name} (nick_name, score, participation_count, day) VALUES (?, ?, ?, ?)", 
                   (nick_name, score, participation_count, day))
    conn.commit()

def update_content_record(conn, content_name, start_date, nick_name, score, participation_count, day):
    table_name = f"{content_name}_{start_date}"
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table_name} SET score = ?, participation_count = ? WHERE nick_name = ? AND day = ?", 
                   (score, participation_count, nick_name, day))
    conn.commit()

def delete_content_record(conn, content_name, start_date, nick_name, day):
    table_name = f"{content_name}_{start_date}"
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE nick_name = ? AND day = ?", (nick_name, day))
    conn.commit()

# 메인 함수: 트랜잭션 스크립트 실행
def main():
    db_name = "MemberManagement.db"
    conn = get_connection(db_name)

    # 테이블 확인
    if not ensure_table_exists(conn, "member"):
        print("Error: 'member' table does not exist.")
        return

    if not ensure_table_exists(conn, "content_schedule"):
        print("Error: 'content_schedule' table does not exist.")
        return

    # 멤버 관련 트랜잭션 스크립트
    nick_name = "User_0001"
    member_data = find_member(conn, nick_name)

    if member_data:
        print(f"Member found: {member_data}")
    else:
        # 멤버 생성 (Create)
        create_member(conn, nick_name, "Kakao_0001", "20210101", Grant.USER.value, 0, 10)
        print("Member created.")

    # 멤버 정보 업데이트 (Update)
    update_grant(conn, nick_name, Grant.SUB_ADMIN)
    update_last_login(conn, nick_name, 5)
    update_score(conn, nick_name, 15)

    # 멤버 삭제 (Delete)
    delete_member(conn, nick_name)

    # 컨텐츠 관련 트랜잭션 스크립트
    content_name = "raid"
    start_date = "20240925"
    content_data = find_content_record(conn, content_name, start_date, nick_name)

    if content_data:
        print(f"Content records found: {content_data}")
    else:
        # 컨텐츠 레코드 삽입 (Create)
        insert_content_record(conn, content_name, start_date, nick_name, score=10, participation_count=1, day=1)
        print("Content record created.")

    # 컨텐츠 레코드 업데이트 (Update)
    update_content_record(conn, content_name, start_date, nick_name, score=12, participation_count=2, day=1)

    # 컨텐츠 레코드 삭제 (Delete)
    delete_content_record(conn, content_name, start_date, nick_name, day=1)

    conn.close()

if __name__ == "__main__":
    main()
