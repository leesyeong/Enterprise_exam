# Description : 트랜잭션 스크립트 패턴을 사용한 코드

import sqlite3
from enum import Enum

class Grant(Enum):
    ADMIN = 0
    SUB_ADMIN = 1
    USER = 2

class Procedure:
    def __init__(self, db_name):
        self.db_name = db_name

    def change_grant(self, user_nick_name, grant):
        # DB에서 유저의 권한을 변경하는 코드
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE users SET grant = ? WHERE nick_name = ?", (grant.value, user_nick_name))
            conn.commit()
            print(f"User {user_nick_name} is now {grant.name}")
        except sqlite3.Error as e:
            conn.rollback()
            print(f"An error occurred: {e}")
        finally:
            conn.close()

def main():
    procedure = Procedure("MemberManagement.db")

    # 트랜잭션 1
    procedure.change_grant("User_0001", Grant.ADMIN)

if __name__ == "__main__":
    main()

