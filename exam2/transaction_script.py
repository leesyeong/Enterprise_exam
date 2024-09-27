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

def main():
    db_name = "MemberManagement.db"
    conn = get_connection(db_name)
    cursor = conn.cursor()

    # 테이블 확인 (member 테이블이 존재하는지 확인)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='member';")
    if not cursor.fetchone():
        print("Error: 'member' table does not exist.")
        return

    # 테이블 확인 (content_schedule 테이블이 존재하는지 확인)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='content_schedule';")
    if not cursor.fetchone():
        print("Error: 'content_schedule' table does not exist.")
        return

    # 멤버 찾기
    nick_name = "User_0001"
    cursor.execute("SELECT kakao_nick_name, join_date, grant, last_login, score FROM member WHERE nick_name = ?", (nick_name,))
    member_data = cursor.fetchone()

    if member_data:
        print(f"Member found: {member_data}")
        kakao_nick_name, join_date, grant, last_login, score = member_data
    else:
        # 멤버 생성 (Create)
        kakao_nick_name = "Kakao_0001"
        join_date = "20210101"
        grant = Grant.USER.value
        last_login = 0
        score = 10
        cursor.execute("INSERT INTO member (nick_name, kakao_nick_name, join_date, grant, last_login, score) VALUES (?, ?, ?, ?, ?, ?)",
                       (nick_name, kakao_nick_name, join_date, grant, last_login, score))
        conn.commit()
        print("Member created.")

    # 멤버 정보 업데이트 (Update)
    grant = Grant.SUB_ADMIN.value
    last_login = 5
    score = 15
    cursor.execute("UPDATE member SET grant = ?, last_login = ?, score = ? WHERE nick_name = ?",
                   (grant, last_login, score, nick_name))
    conn.commit()
    print("Member updated.")

    # 멤버 삭제 (Delete)
    cursor.execute("DELETE FROM member WHERE nick_name = ?", (nick_name,))
    conn.commit()
    print(f"Member {nick_name} deleted.")

    # 컨텐츠 레코드 처리
    content_name = "raid"
    start_date = "20240925"
    table_name = f"{content_name}_{start_date}"

    # 테이블 확인 (content 테이블 존재 여부 확인)
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    if cursor.fetchone():
        # 컨텐츠 레코드 조회
        cursor.execute(f"SELECT score, participation_count, day FROM {table_name} WHERE nick_name = ?", (nick_name,))
        content_data = cursor.fetchall()

        if content_data:
            print(f"Content records found for {nick_name}: {content_data}")
        else:
            # 컨텐츠 레코드 생성 (Create)
            cursor.execute(f"INSERT INTO {table_name} (nick_name, score, participation_count, day) VALUES (?, ?, ?, ?)",
                           (nick_name, 10, 1, 1))
            conn.commit()
            print(f"Content record for {nick_name} created.")

        # 컨텐츠 레코드 업데이트 (Update)
        cursor.execute(f"UPDATE {table_name} SET score = ?, participation_count = ? WHERE nick_name = ? AND day = ?",
                       (12, 2, nick_name, 1))
        conn.commit()
        print(f"Content record for {nick_name} updated.")

        # 컨텐츠 레코드 삭제 (Delete)
        cursor.execute(f"DELETE FROM {table_name} WHERE nick_name = ? AND day = ?", (nick_name, 1))
        conn.commit()
        print(f"Content record for {nick_name} deleted.")
    else:
        print(f"Error: '{table_name}' table does not exist for the given content.")

    conn.close()

if __name__ == "__main__":
    main()
