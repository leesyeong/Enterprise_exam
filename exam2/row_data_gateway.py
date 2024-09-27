import sqlite3
from enum import Enum
from datetime import datetime, timedelta

class Grant(Enum):
    ADMIN = 0
    SUB_ADMIN = 1
    USER = 2

# DB 접속 함수
def get_connection(db_name="MemberManagement.db"):
    return sqlite3.connect(db_name)

# 테이블 존재 여부 확인 데코레이터
def ensure_table_exists(table_name):
    def decorator(func):
        def wrapper(instance, *args, **kwargs):
            conn = get_connection(instance.db_name)
            cursor = conn.cursor()

            # 테이블이 존재하는지 확인하는 쿼리 실행
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            table_exists = cursor.fetchone()

            if not table_exists:
                # 테이블이 존재하지 않으면 오류 메시지 출력 후 종료
                print(f"Error: '{table_name}' table does not exsist.")
                conn.close()
                return

            conn.close()
            # 테이블이 존재하면 원래 함수 실행
            return func(instance, *args, **kwargs)

        return wrapper
    return decorator

class Finder:
    def __init__(self, db_name):
        self.db_name = db_name

    @ensure_table_exists("member")
    def find_member(self, nick_name):
        """nick_name을 기준으로 멤버를 찾음"""
        conn = get_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT kakao_nick_name, join_date, grant, last_login, score FROM member WHERE nick_name = ?", (nick_name,))
        result = cursor.fetchone()
        conn.close()
        return result

    def find_content_record(self, content_name, start_date, nick_name):
        """nick_name을 기준으로 컨텐츠 레코드를 찾음"""
        table_name = f"{content_name}_{start_date}"
        conn = get_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT score, participation_count, day FROM {table_name} WHERE nick_name = ?", (nick_name,))
        result = cursor.fetchone()
        conn.close()
        return result


# RowDataGateway 기본 클래스
class RowDataGateway:
    def __init__(self, db_name="MemberManagement.db"):
        self.db_name = db_name

# MemberGateway: 행 데이터 게이트웨이
class MemberGateway(RowDataGateway):
    def __init__(self, db_name, nick_name):
        super().__init__(db_name)

        # Key
        self.nick_name = nick_name

    @ensure_table_exists("member")
    def find(self):
        """nick_name을 기준으로 멤버를 찾음"""
        conn = get_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT kakao_nick_name, join_date, grant, last_login, score FROM member WHERE nick_name = ?", (self.nick_name,))
        result = cursor.fetchone()
        conn.close()
        return result

    @ensure_table_exists("member")
    def update_grant(self, grant):
        """grant 업데이트"""
        conn = get_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE member SET grant = ? WHERE nick_name = ?", (grant, self.nick_name))
        conn.commit()

    @ensure_table_exists("member")
    def update_last_login(self, last_login):
        """last_login 업데이트"""
        conn = get_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE member SET last_login = ? WHERE nick_name = ?", (last_login, self.nick_name))
        conn.commit()
        conn.close()

    @ensure_table_exists("member")
    def update_score(self, score):
        """점수 업데이트"""
        conn = get_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("UPDATE member SET score = ? WHERE nick_name = ?", (score, self.nick_name))
        conn.commit()
        conn.close()

    @ensure_table_exists("member")
    def delete(self):
        """멤버 삭제 (강퇴)"""
        conn = get_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM member WHERE nick_name = ?", (self.nick_name,))
        conn.commit()
        conn.close()

# ContentRecordGateway: 행 데이터 게이트웨이
class ContentRecordGateway(RowDataGateway):
    def __init__(self, db_name, table_name ,nick_name, day):
        super().__init__(db_name)
        self.table_name = table_name

        # Key
        self.nick_name = nick_name
        self.day = day

    def insert(self, score, participation_count, day):
        """개별 레코드 삽입"""
        conn = get_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {self.table_name} (nick_name, score, participation_count, day) VALUES (?, ?, ?, ?)",
                       (self.nick_name, score, participation_count, day))
        conn.commit()
        conn.close()

    def update(self, score, participation_count):
        """개별 레코드 업데이트"""
        conn = get_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {self.table_name} SET score = ?, participation_count = ? WHERE nick_name = ?",
                       (score, participation_count, self.nick_name))
        conn.commit()
        conn.close()

    def delete(self):
        """개별 레코드 삭제"""
        conn = get_connection(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {self.table_name} WHERE nick_name = ?, day = ?", (self.nick_name, self.day))
        conn.commit()
        conn.close()

# 도메인 객체
class Member:
    def __init__(self, nick_name, kakao_nick_name, join_date=None, grant=None, last_login=None, score=None):
        self.nick_name = nick_name
        self.kakao_nick_name = kakao_nick_name
        self.join_date = join_date if join_date else datetime.now()
        self.grant = grant if grant else Grant.USER
        self.last_login = last_login if last_login else 0
        self.score = score if score else 0

        self.member_gateway = MemberGateway("MemberManagement.db", self.nick_name)
        # self.fetch()

    def insert(self):
        self.member_gateway.create(self.kakao_nick_name, self.join_date, self.grant, self.last_login, self.score)

    def fetch(self):
        result = self.member_gateway.find()
        if result:
            self.kakao_nick_name, self.join_date, self.grant, self.last_login, self.score = result
            print(f"Fetched data for {self.nick_name}: {self.__dict__}")
        else:
            print(f"User {self.nick_name} not found.")

    def update(self):

        # 유효성 검사
        self.validate()

        self.member_gateway.update_grant(self.grant.value)
        self.member_gateway.update_last_login(self.last_login)
        self.member_gateway.update_score(self.score)

    # 유효성 검사 (비즈니스 로직 추가)
    def validate(self):
        if 0 > self.score:
            self.score = 0

        if self.score >= 15:
            self.score = 15

        current_date = datetime.now()

        if datetime.strptime(self.join_date, "%Y%m%d") > current_date :
            self.join_date = current_date

        if self.last_login < 0:
            self.last_login = 0

    def delete(self):
        self.member_gateway.delete()

# 도메인 객체
class ContentRecord:
    def __init__(self, nick_name, day, score=0, participation_count=0):
        self.nick_name = nick_name
        self.score = score
        self.participation_count = participation_count
        self.day = day

        self.content_record_gateway = ContentRecordGateway("MemberManagement.db", "raid", "20240925", self.nick_name)

    def insert(self):
        self.content_record_gateway.insert(self.score, self.participation_count, self.day)

    def fetch(self):
        result = self.content_record_gateway.find()
        if result:
            self.score, self.participation_count, self.day = result
            print(f"Fetched data for {self.nick_name}: {self.__dict__}")
        else:
            print(f"User {self.nick_name} not found.")

    def update(self):
        self.content_record_gateway.update(self.score, self.participation_count)

    def delete(self):
        self.content_record_gateway.delete()



# 메인 함수
def main():
    # 범용 Finder
    finder = Finder("MemberManagement.db")

    #region 1 : Row Data Gateway CRUD
    # 0. 멤버 찾기
    member_data = finder.find_member("User_0001")

    member = None

    if member_data:
        kakao_nick_name, join_date, grant, last_login, score = member_data
        member = Member("User_0001", kakao_nick_name, join_date, grant, last_login, score)
    else:
        # 1. 멤버 생성(Create)
        member = Member("User_0001", "Kakao_0001")
        member.insert()

    # 2. 멤버 정보 읽기 (Read)
    member.fetch()

    # 3. 멤버 정보 업데이트 (Update)
    member.grant = Grant.SUB_ADMIN
    member.last_login = 3 # 3일 전
    member.update()

    # 4. 멤버 삭제 (Delete)
    member.delete()
    #endregion

    #region 2 : 특정 조건에 따른 멤버 삭제
    if member.score <= 0:
        member.delete()

    if member.last_login >= 5:
        member.delete()
    #endregion

    #region 3 : Content Record CRUD
    # 0. 컨텐츠 레코드 찾기
    content_record_datas = finder.find_content_record("raid", "20240925", "User_0001")

    for content_record_data in content_record_datas:
        score, participation_count, day = content_record_data
        content_record = ContentRecord("User_0001", day, score, participation_count)
        content_record.fetch()
    #endregion

if __name__ == "__main__":
    main()
