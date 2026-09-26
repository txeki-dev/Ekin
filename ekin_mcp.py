"""
Punto de entrada de línea de comandos (CLI) para MCP vía transporte STDIO.

Permite conectar clientes MCP como Claude Desktop, Claude Code o Antigravity
directamente a través de tuberías stdin/stdout:
    python -m ekin_mcp --board-uuid <UUID> [--token <TOKEN>] [--db-path <PATH>]
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

import database
from mcp_server import McpProtocolHandler, authenticate_and_get_board


def main(argv: Optional[List[str]] = None):
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Ekin Kanban MCP Stdio Server")
    parser.add_argument("--board-uuid", required=True, help="UUID del tablero de Ekin")
    parser.add_argument("--token", default=None, help="Token secreto de autenticación MCP")
    parser.add_argument("--db-path", default=None, help="Ruta alternativa a la base de datos de Ekin")
    args = parser.parse_args(argv)

    database.init_db(args.db_path)

    try:
        board = authenticate_and_get_board(args.board_uuid, args.token, db_path=args.db_path)
    except Exception as exc:
        sys.stderr.write(f"Error de autenticación MCP: {exc}\n")
        sys.exit(1)

    handler = McpProtocolHandler(board, db_path=args.db_path, client_name="Agente IA (stdio)")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        resp = handler.handle(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
