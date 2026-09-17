#!/usr/bin/env python3
"""数据库 schema 导出工具

从数据库连接中读取表结构，输出为 JSON 文件，供 AI 解析生成 markdown 文档。

支持的数据库：Oracle / PostgreSQL / MySQL / SQL Server

Usage:
    pip install oracledb psycopg2-binary mysql-connector-python pyodbc
    export DB_PASSWORD='your_password'
    python dump_schema.py --db-type oracle --host db.example.com --port 1521 \
        --user myuser --password-env DB_PASSWORD \
        --service ORCLPDB1 --schema MY_SCHEMA \
        --output temp/schema_dump.json
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


# ---------- 各方言的 SQL 查询 ----------

ORACLE_QUERIES = {
    "tables": """
        SELECT owner AS schema_name, table_name, num_rows AS row_estimate,
               last_analyzed, temporary
        FROM all_tables
        WHERE owner = :schema
        ORDER BY table_name
    """,
    "tab_comments": """
        SELECT owner AS schema_name, table_name, comments AS table_comment
        FROM all_tab_comments
        WHERE owner = :schema AND comments IS NOT NULL
    """,
    "columns": """
        SELECT owner AS schema_name, table_name, column_name, data_type,
               data_length, data_precision, data_scale, nullable,
               data_default, column_id
        FROM all_tab_columns
        WHERE owner = :schema
        ORDER BY table_name, column_id
    """,
    "col_comments": """
        SELECT owner AS schema_name, table_name, column_name, comments AS column_comment
        FROM all_col_comments
        WHERE owner = :schema AND comments IS NOT NULL
    """,
    "indexes": """
        SELECT owner AS schema_name, index_name, table_name, uniqueness, index_type
        FROM all_indexes
        WHERE owner = :schema AND table_name IS NOT NULL
        ORDER BY table_name, index_name
    """,
    "index_columns": """
        SELECT index_owner AS schema_name, index_name, table_name, column_name, column_position
        FROM all_ind_columns
        WHERE index_owner = :schema
        ORDER BY table_name, index_name, column_position
    """,
    "primary_keys": """
        SELECT owner AS schema_name, constraint_name, table_name
        FROM all_constraints
        WHERE owner = :schema AND constraint_type = 'P'
    """,
    "pk_columns": """
        SELECT owner AS schema_name, constraint_name, table_name, column_name, position
        FROM all_cons_columns
        WHERE owner = :schema
          AND constraint_name IN (
              SELECT constraint_name FROM all_constraints
              WHERE owner = :schema AND constraint_type = 'P'
          )
        ORDER BY table_name, constraint_name, position
    """,
    "foreign_keys": """
        SELECT owner AS schema_name, constraint_name, table_name,
               r_owner AS ref_schema, r_constraint_name AS ref_constraint
        FROM all_constraints
        WHERE owner = :schema AND constraint_type = 'R'
    """,
    "fk_columns": """
        SELECT owner AS schema_name, constraint_name, table_name, column_name, position
        FROM all_cons_columns
        WHERE owner = :schema
          AND constraint_name IN (
              SELECT constraint_name FROM all_constraints
              WHERE owner = :schema AND constraint_type = 'R'
          )
        ORDER BY table_name, constraint_name, position
    """,
}

POSTGRESQL_QUERIES = {
    "tables": """
        SELECT table_schema AS schema_name, table_name,
               (xpath('/row/cnt/text()', xml_count))[1]::text::int AS row_estimate
        FROM (
            SELECT table_schema, table_name,
                   query_to_xml(format('SELECT COUNT(*) AS cnt FROM %%I.%%I', table_schema, table_name), false, true, '') AS xml_count
            FROM information_schema.tables
            WHERE table_schema = %(schema)s
        ) t
        ORDER BY table_name
    """,
    "tab_comments": """
        SELECT n.nspname AS schema_name, c.relname AS table_name,
               obj_description(c.oid) AS table_comment
        FROM pg_class c
        JOIN pg_namespace n ON c.relnamespace = n.oid
        WHERE n.nspname = %(schema)s AND obj_description(c.oid) IS NOT NULL
    """,
    "columns": """
        SELECT table_schema AS schema_name, table_name, column_name, data_type,
               character_maximum_length, numeric_precision, numeric_scale,
               is_nullable, column_default, ordinal_position
        FROM information_schema.columns
        WHERE table_schema = %(schema)s
        ORDER BY table_name, ordinal_position
    """,
    "col_comments": """
        SELECT c.table_schema AS schema_name, c.table_name, c.column_name,
               pg_catalog.col_description(
                   (quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass::oid,
                   c.ordinal_position
               ) AS column_comment
        FROM information_schema.columns c
        WHERE c.table_schema = %(schema)s
          AND pg_catalog.col_description(
                  (quote_ident(c.table_schema) || '.' || quote_ident(c.table_name))::regclass::oid,
                  c.ordinal_position
              ) IS NOT NULL
    """,
    "indexes": """
        SELECT schemaname AS schema_name, tablename AS table_name,
               indexname AS index_name, indexdef
        FROM pg_indexes
        WHERE schemaname = %(schema)s
        ORDER BY tablename, indexname
    """,
    "primary_keys": """
        SELECT tc.table_schema AS schema_name, tc.table_name, tc.constraint_name,
               kcu.column_name, kcu.ordinal_position AS position
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = %(schema)s AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY tc.table_name, kcu.ordinal_position
    """,
    "foreign_keys": """
        SELECT tc.table_schema AS schema_name, tc.table_name, tc.constraint_name,
               kcu.column_name, kcu.ordinal_position AS position,
               ccu.table_schema AS ref_schema, ccu.table_name AS ref_table, ccu.column_name AS ref_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON tc.constraint_name = ccu.constraint_name
            AND tc.table_schema = ccu.constraint_schema
        WHERE tc.table_schema = %(schema)s AND tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name, kcu.ordinal_position
    """,
}

MYSQL_QUERIES = {
    "tables": """
        SELECT table_schema AS schema_name, table_name, table_rows AS row_estimate,
               create_time, table_comment
        FROM information_schema.tables
        WHERE table_schema = %(db)s AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """,
    "columns": """
        SELECT table_schema AS schema_name, table_name, column_name, data_type,
               character_maximum_length, numeric_precision, numeric_scale,
               is_nullable, column_default, ordinal_position, column_comment
        FROM information_schema.columns
        WHERE table_schema = %(db)s
        ORDER BY table_name, ordinal_position
    """,
    "indexes": """
        SELECT table_schema AS schema_name, table_name, index_name,
               non_unique, seq_in_index, column_name, index_type
        FROM information_schema.statistics
        WHERE table_schema = %(db)s
        ORDER BY table_name, index_name, seq_in_index
    """,
    "primary_keys": """
        SELECT tc.table_schema AS schema_name, tc.table_name, tc.constraint_name,
               kcu.column_name, kcu.ordinal_position AS position
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = %(db)s AND tc.constraint_type = 'PRIMARY KEY'
        ORDER BY tc.table_name, kcu.ordinal_position
    """,
    "foreign_keys": """
        SELECT kcu.table_schema AS schema_name, kcu.table_name, kcu.constraint_name,
               kcu.column_name, kcu.ordinal_position AS position,
               kcu.referenced_table_schema AS ref_schema,
               kcu.referenced_table_name AS ref_table,
               kcu.referenced_column_name AS ref_column
        FROM information_schema.key_column_usage kcu
        JOIN information_schema.referential_constraints rc
            ON kcu.constraint_name = rc.constraint_name
            AND kcu.table_schema = rc.constraint_schema
        WHERE kcu.table_schema = %(db)s
          AND kcu.referenced_table_name IS NOT NULL
        ORDER BY kcu.table_name, kcu.ordinal_position
    """,
}

SQLSERVER_QUERIES = {
    "tables": """
        SELECT s.name AS schema_name, t.name AS table_name,
               p.rows AS row_estimate, t.create_date
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        JOIN sys.partitions p ON t.object_id = p.object_id AND p.index_id IN (0, 1)
        WHERE s.name = ?
        ORDER BY t.name
    """,
    "tab_comments": """
        SELECT s.name AS schema_name, t.name AS table_name,
               ep.value AS table_comment
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        LEFT JOIN sys.extended_properties ep
            ON t.object_id = ep.major_id AND ep.minor_id = 0 AND ep.name = 'MS_Description'
        WHERE s.name = ? AND ep.value IS NOT NULL
    """,
    "columns": """
        SELECT s.name AS schema_name, t.name AS table_name, c.name AS column_name,
               ty.name AS data_type, c.max_length, c.precision, c.scale,
               c.is_nullable, c.is_identity, c.column_id,
               dc.definition AS default_value,
               ep.value AS column_comment
        FROM sys.columns c
        JOIN sys.tables t ON c.object_id = t.object_id
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        JOIN sys.types ty ON c.user_type_id = ty.user_type_id
        LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id
        LEFT JOIN sys.extended_properties ep
            ON c.object_id = ep.major_id AND c.column_id = ep.minor_id AND ep.name = 'MS_Description'
        WHERE s.name = ?
        ORDER BY t.name, c.column_id
    """,
    "indexes": """
        SELECT s.name AS schema_name, t.name AS table_name, i.name AS index_name,
               i.is_unique, i.type_desc AS index_type
        FROM sys.indexes i
        JOIN sys.tables t ON i.object_id = t.object_id
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE s.name = ? AND i.is_hypothetical = 0 AND i.name IS NOT NULL
        ORDER BY t.name, i.name
    """,
    "index_columns": """
        SELECT s.name AS schema_name, t.name AS table_name, i.name AS index_name,
               c.name AS column_name, ic.key_ordinal, ic.is_descending_key
        FROM sys.index_columns ic
        JOIN sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = ic.index_id
        JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        JOIN sys.tables t ON i.object_id = t.object_id
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE s.name = ?
        ORDER BY t.name, i.name, ic.key_ordinal
    """,
    "primary_keys": """
        SELECT s.name AS schema_name, t.name AS table_name, i.name AS constraint_name,
               c.name AS column_name, ic.key_ordinal AS position
        FROM sys.indexes i
        JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        JOIN sys.columns c ON i.object_id = c.object_id AND c.column_id = c.column_id
        JOIN sys.tables t ON i.object_id = t.object_id
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE s.name = ? AND i.is_primary_key = 1
        ORDER BY t.name, ic.key_ordinal
    """,
    "foreign_keys": """
        SELECT s.name AS schema_name, t.name AS table_name, fk.name AS constraint_name,
               c1.name AS column_name, fkc.constraint_column_id AS position,
               s2.name AS ref_schema, t2.name AS ref_table, c2.name AS ref_column
        FROM sys.foreign_keys fk
        JOIN sys.tables t ON fk.parent_object_id = t.object_id
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        JOIN sys.columns c1 ON fkc.parent_object_id = c1.object_id AND fkc.parent_column_id = c1.column_id
        JOIN sys.tables t2 ON fkc.referenced_object_id = t2.object_id
        JOIN sys.schemas s2 ON t2.schema_id = s2.schema_id
        JOIN sys.columns c2 ON fkc.referenced_object_id = c2.object_id AND fkc.referenced_column_id = c2.column_id
        WHERE s.name = ?
        ORDER BY t.name, fk.name
    """,
}

QUERIES = {
    "oracle": ORACLE_QUERIES,
    "postgresql": POSTGRESQL_QUERIES,
    "mysql": MYSQL_QUERIES,
    "sqlserver": SQLSERVER_QUERIES,
}


# ---------- DB 连接 ----------

def connect(db_type: str, args):
    if db_type == "oracle":
        try:
            import oracledb  # thin 模式免装 Instant Client
            dsn = oracledb.makedsn(args.host, args.port, service_name=args.service)
            return oracledb.connect(user=args.user, password=args.password, dsn=dsn)
        except ImportError:
            import cx_Oracle
            dsn = cx_Oracle.makedsn(args.host, args.port, service_name=args.service)
            return cx_Oracle.connect(args.user, args.password, dsn)
    if db_type == "postgresql":
        import psycopg2
        return psycopg2.connect(
            host=args.host, port=args.port,
            user=args.user, password=args.password,
            dbname=args.database,
        )
    if db_type == "mysql":
        import mysql.connector
        return mysql.connector.connect(
            host=args.host, port=args.port,
            user=args.user, password=args.password,
            database=args.database,
            charset="utf8mb4",
        )
    if db_type == "sqlserver":
        import pyodbc
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={args.host},{args.port};"
            f"DATABASE={args.database};"
            f"UID={args.user};PWD={args.password}"
        )
        return pyodbc.connect(conn_str)
    raise ValueError(f"Unsupported db_type: {db_type}")


def execute(cursor, sql: str, params: dict) -> list:
    cursor.execute(sql, params)
    cols = [c[0].lower() for c in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]


def main():
    parser = argparse.ArgumentParser(description="Dump database schema to JSON")
    parser.add_argument("--db-type", required=True, choices=list(QUERIES.keys()))
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", help="Direct password (NOT recommended)")
    parser.add_argument("--password-env", default="DB_PASSWORD",
                        help="Env var name holding the password (default: DB_PASSWORD)")
    parser.add_argument("--database", help="Database name (postgres/mysql/sqlserver)")
    parser.add_argument("--service", help="Oracle service name")
    parser.add_argument("--schema", required=True,
                        help="Schema (Oracle/PostgreSQL/SQL Server) or database (MySQL) to dump")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    args = parser.parse_args()

    args.password = args.password or os.environ.get(args.password_env)
    if not args.password:
        print(f"ERROR: password not provided via --password or env {args.password_env}", file=sys.stderr)
        sys.exit(1)

    if args.db_type in ("postgresql", "mysql", "sqlserver") and not args.database:
        print(f"ERROR: --database is required for {args.db_type}", file=sys.stderr)
        sys.exit(1)
    if args.db_type == "oracle" and not args.service:
        print("ERROR: --service is required for oracle", file=sys.stderr)
        sys.exit(1)

    queries = QUERIES[args.db_type]
    if args.db_type == "sqlserver":
        bind = (args.schema,)      # pyodbc qmark 占位符：位置参数
    elif args.db_type == "mysql":
        bind = {"db": args.schema}  # mysql-connector pyformat
    else:                           # oracle(:name) / postgresql(pyformat) 都吃命名 dict
        bind = {"schema": args.schema}

    print(f"Connecting to {args.db_type}@{args.host}:{args.port or '?'} schema={args.schema}", file=sys.stderr)
    conn = connect(args.db_type, args)
    try:
        result = {
            "meta": {
                "db_type": args.db_type,
                "schema": args.schema,
                "host": args.host,
                "dumped_at": datetime.now().isoformat(),
            },
            "data": {},
        }
        failures = 0
        with conn.cursor() as cur:
            for name, sql in queries.items():
                print(f"  -> querying {name}...", file=sys.stderr)
                try:
                    result["data"][name] = execute(cur, sql, bind)
                except Exception as e:
                    print(f"  !! query {name} failed: {e}", file=sys.stderr)
                    result["data"][name] = []
                    failures += 1
        if failures:
            print(f"WARNING: {failures}/{len(queries)} queries failed - dump is incomplete", file=sys.stderr)
            if failures == len(queries):
                print("ERROR: all queries failed, dump is empty - aborting", file=sys.stderr)
                sys.exit(2)

        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(result, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        size_kb = out.stat().st_size / 1024
        total_rows = sum(len(v) for v in result["data"].values())
        print(f"OK: dumped {total_rows} rows to {args.output} ({size_kb:.1f} KB)", file=sys.stderr)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
