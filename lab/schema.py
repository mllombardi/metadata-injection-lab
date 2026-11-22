"""Read table/column definitions and their comments from Postgres.

This is the step where metadata enters the prompt, so it is the
step to point at on your slide.
"""
import psycopg

SCHEMA_SQL = """
SELECT c.table_schema,
       c.table_name,
       c.column_name,
       c.data_type,
       obj_description(format('%I.%I', c.table_schema, c.table_name)::regclass) AS table_comment,
       col_description(format('%I.%I', c.table_schema, c.table_name)::regclass,
                       c.ordinal_position)                                  AS column_comment
FROM information_schema.columns c
WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY c.table_schema, c.table_name, c.ordinal_position;
"""


def load_schema(conn: psycopg.Connection) -> dict:
    """Return {"schema.table": {"comment": str|None, "columns": [(name, type, comment)]}}."""
    tables: dict = {}
    for schema, table, col, dtype, tcomment, ccomment in conn.execute(SCHEMA_SQL):
        key = f"{schema}.{table}"
        t = tables.setdefault(key, {"comment": tcomment, "columns": []})
        t["columns"].append((col, dtype, ccomment))
    return tables


def render_schema(tables: dict, spotlight: bool = False) -> str:
    """Format the schema as text for the prompt.

    spotlight=True wraps every comment in explicit data markers (defense D2).
    """
    def fmt(comment):
        if not comment:
            return ""
        if spotlight:
            return f"  <<metadata>>{comment}<</metadata>>"
        return f"  -- {comment}"

    lines = []
    for name, t in tables.items():
        lines.append(f"TABLE {name}{fmt(t['comment'])}")
        for col, dtype, comment in t["columns"]:
            lines.append(f"    {col} {dtype}{fmt(comment)}")
        lines.append("")
    return "\n".join(lines)
