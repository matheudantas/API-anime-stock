from typing import Tuple
import psycopg2
from environs import Env

env = Env()
env.read_env()


class Animes:
    FIELDNAMES = ["id", "anime", "released_date", "seasons"]

    @staticmethod
    def start_connection() -> Tuple:
        conn = psycopg2.connect(env("DATABASE_URL"), sslmode='require')

        cur = conn.cursor()

        return(conn, cur)

    @staticmethod
    def close_connection(conn, cur) -> None:
        conn.commit()
        conn.close()
        cur.close()

    def create_table(self) -> None:
        conn, cur = self.start_connection()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS  animes(
                id BIGSERIAL PRIMARY KEY,
                anime VARCHAR(100) NOT NULL UNIQUE,
                released_date DATE NOT NULL,
                seasons INTEGER NOT NULL
            )
            """
        )

        self.close_connection(conn, cur)

    def missing_fields(self, data: dict) -> list:
        fieldnames = list(self.FIELDNAMES)

        return [resp_json for resp_json in data if resp_json not in fieldnames]

    def check_fields(self, data: dict, fields: list):
        received_keys = data.keys()

        return [received for received in received_keys if received not in fields]

    def insert_anime(self, data: dict) -> dict:
        conn, cur = self.start_connection()

        invalid_keys = self.missing_fields(data)

        if invalid_keys:
            raise KeyError(
                {
                    "available_keys": self.FIELDNAMES[1:],
                    "wrong_keys_sended": invalid_keys
                }

            )

        data['anime'] = data['anime'].title()

        cur.execute(
            """
                    INSERT INTO animes
                        (anime, released_date, seasons)
                    VALUES
                        (%(anime)s, %(released_date)s, %(seasons)s)
                    RETURNING *
                    """, data
        )
        query = cur.fetchone()

        processed_data = dict(zip(self.FIELDNAMES, query))
        processed_data['released_date'] = processed_data['released_date'].strftime(
            "%d/%m/%Y")

        self.close_connection(conn, cur)

        return processed_data

    def select_animes(self) -> dict:
        conn, cur = self.start_connection()
        self.create_table()

        cur.execute(
            """
                SELECT *
                FROM animes;
                """
        )

        query = cur.fetchall()

        if not query:
            raise Exception(
                {"error": "Not Found"}
            )

        processed_data = [dict(zip(self.FIELDNAMES, data)) for data in query]
        for p in processed_data:
            p['released_date'] = p['released_date'].strftime("%d/%m/%Y")

        self.close_connection(conn, cur)

        return processed_data

    def select_by_id(self, id: int) -> dict:
        conn, cur = self.start_connection()

        cur.execute(
            """
                SELECT *
                FROM animes
                WHERE id = %(id)s;
            """,
            {"id": id}
        )

        query = cur.fetchone()

        if not query:
            raise Exception(
                {"data": []}
            )

        processed_data = dict(zip(self.FIELDNAMES, query))
        processed_data['released_date'] = processed_data['released_date'].strftime(
            "%d/%m/%Y")

        self.close_connection(conn, cur)

        return processed_data

    def update_by_id(self, data: dict, anime_id: int) -> dict:
        conn, cur = self.start_connection()

        check_fields = self.check_fields(data, ['anime'])

        if check_fields:
            raise KeyError(
                {
                    "available fields": self.FIELDNAMES[1:],
                    "recieved fields": check_fields,
                }
            )

        data["anime_id"] = anime_id
        data['anime'] = data['anime'].title()

        cur.execute(
            """
                UPDATE animes
                SET anime = %(anime)s
                WHERE id = %(anime_id)s
                RETURNING *
            """,
            data
        )

        query = cur.fetchone()

        if not query:
            raise Exception(
                {"data": []}
            )

        processed_data = dict(zip(self.FIELDNAMES, query))
        processed_data['released_date'] = processed_data['released_date'].strftime(
            "%d/%m/%Y")

        self.close_connection(conn, cur)
        return processed_data

    def delete_by_id(self, anime_id: int):
        conn, cur = self.start_connection()
        self.create_table()

        cur.execute(
            """
           DELETE FROM animes
           WHERE id = %(anime_id)s
           RETURNING *
            """,
            {"anime_id": anime_id}
        )

        if not cur.fetchone():
            raise Exception(
                {"error": "Not Found"}
            )

        self.close_connection(conn, cur)

        return {"data": "No content"}
