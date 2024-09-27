import sqlite3
from enum import Enum

class Grant(Enum):
    ADMIN = 0
    SUB_ADMIN = 1
    USER = 2

class MemberGateway:
    def __init__(self, db_name, nick_name):
        self.db_name = db_name
        self.nick_name = nick_name
        self.kakao_nick_name = None
        self.join_date = None
        self.grant = None
        self.last_login = None
        self.score = None

    def create(self, kakao_nick_name, join_date, grant, last_login, score):
        """새로운 유저 정보를 DB에 삽입 (C)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO member (nick_name, kakao_nick_name, join_date, grant, last_login, score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.nick_name, kakao_nick_name, join_date, grant.value, last_login, score))
            conn.commit()
            print(f"User {self.nick_name} created successfully.")
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Failed to create user. Rolled back. Error: {e}")
        finally:
            conn.close()

    def fetch(self):
        """유저 정보를 DB에서 가져옴 (R)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT kakao_nick_name, join_date, grant, last_login, score
                FROM member WHERE nick_name = ?
            """, (self.nick_name,))
            result = cursor.fetchone()
            if result:
                self.kakao_nick_name, self.join_date, grant_value, self.last_login, self.score = result
                self.grant = Role(grant_value)
                print(f"Fetched data for {self.nick_name}: {self.__dict__}")
            else:
                print(f"User {self.nick_name} not found.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

    def update(self, kakao_nick_name=None, join_date=None, grant=None, last_login=None, score=None):
        """유저 정보를 DB에서 수정 (U)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            if kakao_nick_name:
                cursor.execute("UPDATE member SET kakao_nick_name = ? WHERE nick_name = ?", (kakao_nick_name, self.nick_name))
            if join_date:
                cursor.execute("UPDATE member SET join_date = ? WHERE nick_name = ?", (join_date, self.nick_name))
            if grant:
                cursor.execute("UPDATE member SET grant = ? WHERE nick_name = ?", (grant.value, self.nick_name))
            if last_login:
                cursor.execute("UPDATE member SET last_login = ? WHERE nick_name = ?", (last_login, self.nick_name))
            if score is not None:
                cursor.execute("UPDATE member SET score = ? WHERE nick_name = ?", (score, self.nick_name))

            conn.commit()
            print(f"User {self.nick_name}'s data updated successfully.")
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Failed to update user data. Rolled back. Error: {e}")
        finally:
            conn.close()

    def delete(self):
        """유저 정보를 DB에서 삭제 (D)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM member WHERE nick_name = ?", (self.nick_name,))
            conn.commit()
            print(f"User {self.nick_name} deleted successfully.")
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Failed to delete user. Rolled back. Error: {e}")
        finally:
            conn.close()

# 테스트용 메인 함수
def main():
    db_name = "MemberManagement.db"

    # 새 유저 생성 (C)
    user = Member(db_name, "User_0001")
    user.create("Kakao_0001", "20230101", Role.USER)

    # 유저 정보 읽기 (R)
    user.fetch()

    # 유저 정보 수정 (U)
    user.update(grant=Grant.ADMIN)

    # 유저 정보 다시 읽기 (R)
    user.fetch()

    # 유저 정보 삭제 (D)
    user.delete()

if __name__ == "__main__":
    main()
