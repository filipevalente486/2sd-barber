"""
Base de dados da 2SD.Barber — multi-tenant, com fidelização.
"""
import sqlite3
import bcrypt
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "marcacoes.db"
EMPRESA_ID = 1


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# =========================================================
# INICIALIZAÇÃO
# =========================================================
def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                tipo_servico TEXT NOT NULL,
                logo_path TEXT,
                cor_primaria TEXT DEFAULT '#000000',
                cor_secundaria TEXT DEFAULT '#D4AF37',
                telefone TEXT, whatsapp TEXT, email TEXT, morada TEXT,
                google_maps_url TEXT, ativa INTEGER DEFAULT 1,
                criado_em TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS utilizadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'staff')),
                nome TEXT NOT NULL, ativo INTEGER DEFAULT 1,
                UNIQUE(empresa_id, username),
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER NOT NULL,
                nome TEXT NOT NULL, descricao TEXT,
                duracao_min INTEGER NOT NULL, preco REAL,
                ativo INTEGER DEFAULT 1, ordem INTEGER DEFAULT 0,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS horarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER NOT NULL,
                dia_semana INTEGER NOT NULL,
                hora_abertura TEXT NOT NULL, hora_fecho TEXT NOT NULL,
                ativo INTEGER DEFAULT 1,
                UNIQUE(empresa_id, dia_semana),
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dias_bloqueados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER NOT NULL,
                data TEXT NOT NULL, motivo TEXT,
                UNIQUE(empresa_id, data),
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER NOT NULL,
                nome TEXT NOT NULL, telefone TEXT NOT NULL,
                email TEXT, notas TEXT,
                pontos INTEGER DEFAULT 0,
                total_visitas INTEGER DEFAULT 0,
                total_gasto REAL DEFAULT 0,
                criado_em TEXT NOT NULL,
                UNIQUE(empresa_id, telefone),
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS marcacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER NOT NULL,
                servico_id INTEGER NOT NULL,
                cliente_id INTEGER NOT NULL,
                data TEXT NOT NULL, hora TEXT NOT NULL,
                duracao_min INTEGER NOT NULL,
                estado TEXT NOT NULL DEFAULT 'pendente',
                notas TEXT, criado_em TEXT NOT NULL,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id),
                FOREIGN KEY (servico_id) REFERENCES servicos(id),
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fidelizacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER NOT NULL,
                cliente_id INTEGER NOT NULL,
                marcacao_id INTEGER,
                tipo TEXT NOT NULL CHECK(tipo IN ('ganho','resgatado','ajuste')),
                pontos INTEGER NOT NULL, descricao TEXT,
                criado_em TEXT NOT NULL,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id),
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (marcacao_id) REFERENCES marcacoes(id)
            )
        """)
        conn.commit()
    seed_inicial()


def seed_inicial():
    from config.empresa import EMPRESA
    with get_conn() as conn:
        n = conn.execute("SELECT COUNT(*) FROM empresas").fetchone()[0]
        if n == 0:
            conn.execute("""
                INSERT OR IGNORE INTO empresas
                (id, nome, tipo_servico, logo_path, cor_primaria, cor_secundaria,
                 telefone, whatsapp, email, morada, google_maps_url, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                EMPRESA["id"], EMPRESA["nome"], EMPRESA["tipo_servico"],
                EMPRESA["logo_path"], EMPRESA["cores"]["primaria"],
                EMPRESA["cores"]["secundaria"], EMPRESA["contacto"]["telefone"],
                EMPRESA["contacto"]["whatsapp"], EMPRESA["contacto"]["email"],
                f"{EMPRESA['morada']['rua']}, {EMPRESA['morada']['codigo_postal']} {EMPRESA['morada']['cidade']}",
                EMPRESA["morada"]["google_maps_url"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))
            conn.commit()

        n = conn.execute("SELECT COUNT(*) FROM utilizadores").fetchone()[0]
        if n == 0:
            h = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            conn.execute(
                "INSERT OR IGNORE INTO utilizadores (empresa_id, username, password_hash, role, nome) VALUES (?, ?, ?, ?, ?)",
                (EMPRESA_ID, "admin", h, "admin", "Administrador")
            )
            conn.commit()

        n = conn.execute("SELECT COUNT(*) FROM servicos").fetchone()[0]
        if n == 0:
            servicos = [
                ("Corte simples", "Corte clássico", 30, 12.0),
                ("Corte + barba", "Corte completo + barba", 45, 18.0),
                ("Barba", "Aparar e desenhar barba", 20, 8.0),
                ("Corte criança", "Corte para menores de 12 anos", 20, 9.0),
                ("Corte máquina", "Corte rápido à máquina", 15, 8.0),
            ]
            for i, (nome, desc, dur, preco) in enumerate(servicos):
                conn.execute(
                    "INSERT OR IGNORE INTO servicos (empresa_id, nome, descricao, duracao_min, preco, ordem) VALUES (?, ?, ?, ?, ?, ?)",
                    (EMPRESA_ID, nome, desc, dur, preco, i)
                )
            conn.commit()

        n = conn.execute("SELECT COUNT(*) FROM horarios").fetchone()[0]
        if n == 0:
            for dia, abre, fecha in [(0,"09:00","19:00"),(1,"09:00","19:00"),(2,"09:00","19:00"),(3,"09:00","19:00"),(4,"09:00","19:00"),(5,"09:00","14:00")]:
                conn.execute(
                    "INSERT OR IGNORE INTO horarios (empresa_id, dia_semana, hora_abertura, hora_fecho) VALUES (?, ?, ?, ?)",
                    (EMPRESA_ID, dia, abre, fecha)
                )
            conn.commit()


# =========================================================
# SERVIÇOS
# =========================================================
def listar_servicos(só_ativos=True):
    with get_conn() as conn:
        q = "SELECT * FROM servicos WHERE empresa_id = ?"
        if só_ativos:
            q += " AND ativo = 1"
        q += " ORDER BY ordem, nome"
        return pd.read_sql_query(q, conn, params=(EMPRESA_ID,))


# =========================================================
# HORÁRIOS
# =========================================================
def obter_horario_dia(dia_semana):
    with get_conn() as conn:
        return conn.execute(
            "SELECT hora_abertura, hora_fecho FROM horarios WHERE empresa_id = ? AND dia_semana = ? AND ativo = 1",
            (EMPRESA_ID, dia_semana)
        ).fetchone()


def dia_esta_bloqueado(data_str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT motivo FROM dias_bloqueados WHERE empresa_id = ? AND data = ?",
            (EMPRESA_ID, data_str)
        ).fetchone()
        return row[0] if row else None


# =========================================================
# CLIENTES
# =========================================================
def buscar_clientes_por_nome(nome):
    with get_conn() as conn:
        return pd.read_sql_query(
            "SELECT id, nome, telefone, email FROM clientes WHERE empresa_id = ? AND LOWER(nome) = LOWER(?)",
            conn, params=(EMPRESA_ID, nome.strip())
        )


def criar_ou_atualizar_cliente(nome, telefone, email=None):
    with get_conn() as conn:
        existente = conn.execute(
            "SELECT id FROM clientes WHERE empresa_id = ? AND telefone = ?",
            (EMPRESA_ID, telefone.strip())
        ).fetchone()
        if existente:
            conn.execute(
                "UPDATE clientes SET nome = ?, email = ? WHERE id = ?",
                (nome.strip(), email, existente[0])
            )
            conn.commit()
            return existente[0]
        cur = conn.execute(
            "INSERT INTO clientes (empresa_id, nome, telefone, email, criado_em) VALUES (?, ?, ?, ?, ?)",
            (EMPRESA_ID, nome.strip(), telefone.strip(), email, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return cur.lastrowid


def buscar_cliente_por_telefone(telefone):
    with get_conn() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM clientes WHERE empresa_id = ? AND telefone = ?",
            conn, params=(EMPRESA_ID, telefone.strip())
        )
        return df.iloc[0] if not df.empty else None


def obter_info_cliente(cliente_id):
    with get_conn() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM clientes WHERE id = ? AND empresa_id = ?",
            conn, params=(int(cliente_id), EMPRESA_ID)
        )
        return df.iloc[0] if not df.empty else None


def ranking_clientes(limite=10):
    with get_conn() as conn:
        return pd.read_sql_query(
            "SELECT id, nome, telefone, pontos, total_visitas, total_gasto FROM clientes WHERE empresa_id = ? AND total_visitas > 0 ORDER BY total_visitas DESC LIMIT ?",
            conn, params=(EMPRESA_ID, limite)
        )


# =========================================================
# MARCAÇÕES
# =========================================================
def criar_marcacao(servico_id, cliente_id, data_str, hora_str, duracao_min, notas=None):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO marcacoes (empresa_id, servico_id, cliente_id, data, hora, duracao_min, estado, notas, criado_em) VALUES (?, ?, ?, ?, ?, ?, 'pendente', ?, ?)",
            (EMPRESA_ID, servico_id, cliente_id, data_str, hora_str, duracao_min, notas, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return cur.lastrowid


def listar_marcacoes_por_data(data_str):
    with get_conn() as conn:
        return pd.read_sql_query("""
            SELECT m.id, m.hora, m.duracao_min, m.estado, m.notas,
                   s.nome AS servico, s.preco,
                   c.nome AS cliente, c.telefone, c.email,
                   c.pontos AS cliente_pontos, m.cliente_id
            FROM marcacoes m
            LEFT JOIN servicos s ON s.id = m.servico_id
            LEFT JOIN clientes c ON c.id = m.cliente_id
            WHERE m.empresa_id = ? AND m.data = ?
            ORDER BY m.hora
        """, conn, params=(EMPRESA_ID, data_str))


def cancelar_marcacao(marcacao_id):
    with get_conn() as conn:
        conn.execute("UPDATE marcacoes SET estado = 'cancelada' WHERE id = ? AND empresa_id = ?", (int(marcacao_id), EMPRESA_ID))
        conn.commit()


# =========================================================
# GERAÇÃO DE SLOTS
# =========================================================
def gerar_slots_disponiveis(data_str, duracao_min):
    data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
    dia_semana = data_obj.weekday()

    motivo = dia_esta_bloqueado(data_str)
    if motivo:
        return [], f"Fechado: {motivo or 'dia bloqueado'}"

    horario = obter_horario_dia(dia_semana)
    if not horario:
        return [], "Fechado neste dia"

    hora_abre = datetime.strptime(horario[0], "%H:%M").time()
    hora_fecha = datetime.strptime(horario[1], "%H:%M").time()

    with get_conn() as conn:
        marcacoes = conn.execute(
            "SELECT hora, duracao_min FROM marcacoes WHERE empresa_id = ? AND data = ? AND estado != 'cancelada'",
            (EMPRESA_ID, data_str)
        ).fetchall()

    bloqueados = set()
    for m_hora, m_dur in marcacoes:
        m_ini = datetime.strptime(m_hora, "%H:%M")
        m_fim = m_ini + timedelta(minutes=m_dur)
        cursor = m_ini
        while cursor < m_fim:
            bloqueados.add(cursor.strftime("%H:%M"))
            cursor += timedelta(minutes=15)

    slots = []
    cursor = datetime.combine(data_obj, hora_abre)
    fim_dia = datetime.combine(data_obj, hora_fecha)
    duracao = timedelta(minutes=duracao_min)
    agora = datetime.now()

    while cursor + duracao <= fim_dia:
        if cursor >= agora:
            slot_str = cursor.strftime("%H:%M")
            conflito = False
            check = cursor
            while check < cursor + duracao:
                if check.strftime("%H:%M") in bloqueados:
                    conflito = True
                    break
                check += timedelta(minutes=15)
            if not conflito:
                slots.append(slot_str)
        cursor += timedelta(minutes=15)

    if not slots:
        return [], "Sem horários disponíveis neste dia"
    return slots, None


# =========================================================
# FIDELIZAÇÃO
# =========================================================
from config.empresa import EMPRESA

CONFIG_FID = EMPRESA.get("fidelizacao", {})
PONTOS_POR_VISITA = CONFIG_FID.get("pontos_por_visita", 1)
PONTOS_PARA_PREMIO = CONFIG_FID.get("pontos_para_premio", 5)
DESCRICAO_PREMIO = CONFIG_FID.get("descricao_premio", "Prémio")


def obter_pontos_cliente(cliente_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT pontos FROM clientes WHERE id = ? AND empresa_id = ?",
            (int(cliente_id), EMPRESA_ID)
        ).fetchone()
        return row[0] if row else 0


def adicionar_pontos(cliente_id, pontos, descricao, marcacao_id=None):
    with get_conn() as conn:
        conn.execute(
            "UPDATE clientes SET pontos = pontos + ? WHERE id = ? AND empresa_id = ?",
            (int(pontos), int(cliente_id), EMPRESA_ID)
        )
        conn.execute(
            "INSERT INTO fidelizacao (empresa_id, cliente_id, marcacao_id, tipo, pontos, descricao, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (EMPRESA_ID, int(cliente_id), marcacao_id, "ganho" if pontos > 0 else "resgatado", int(pontos), descricao, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()


def concluir_marcacao(marcacao_id):
    with get_conn() as conn:
        row = conn.execute("""
            SELECT m.cliente_id, s.preco FROM marcacoes m
            LEFT JOIN servicos s ON s.id = m.servico_id
            WHERE m.id = ? AND m.empresa_id = ? AND m.estado = 'pendente'
        """, (int(marcacao_id), EMPRESA_ID)).fetchone()

        if not row:
            return None

        cliente_id, preco = row
        preco = preco or 0

        conn.execute("UPDATE marcacoes SET estado = 'concluida' WHERE id = ? AND empresa_id = ?", (int(marcacao_id), EMPRESA_ID))
        conn.execute(
            "UPDATE clientes SET total_visitas = total_visitas + 1, total_gasto = total_gasto + ? WHERE id = ? AND empresa_id = ?",
            (preco, cliente_id, EMPRESA_ID)
        )

        pontos = PONTOS_POR_VISITA
        if pontos > 0:
            conn.execute(
                "INSERT INTO fidelizacao (empresa_id, cliente_id, marcacao_id, tipo, pontos, descricao, criado_em) VALUES (?, ?, ?, 'ganho', ?, ?, ?)",
                (EMPRESA_ID, cliente_id, int(marcacao_id), pontos, f"Serviço concluído ({preco:.2f}€)", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.execute("UPDATE clientes SET pontos = pontos + ? WHERE id = ?", (pontos, cliente_id))

        conn.commit()
        novo_saldo = conn.execute("SELECT pontos FROM clientes WHERE id = ?", (cliente_id,)).fetchone()[0]

        return {
            "cliente_id": cliente_id,
            "pontos_ganhos": pontos,
            "novo_saldo": novo_saldo,
            "premio_disponivel": novo_saldo >= PONTOS_PARA_PREMIO,
        }


def resgatar_premio(cliente_id):
    saldo = obter_pontos_cliente(cliente_id)
    if saldo < PONTOS_PARA_PREMIO:
        return False, f"Pontos insuficientes ({saldo}/{PONTOS_PARA_PREMIO})"
    adicionar_pontos(cliente_id, -PONTOS_PARA_PREMIO, f"Resgate: {DESCRICAO_PREMIO}")
    return True, f"✅ {DESCRICAO_PREMIO} resgatado!"


def historico_cliente(cliente_id):
    with get_conn() as conn:
        return pd.read_sql_query(
            "SELECT tipo, pontos, descricao, criado_em FROM fidelizacao WHERE empresa_id = ? AND cliente_id = ? ORDER BY criado_em DESC",
            conn, params=(EMPRESA_ID, int(cliente_id))
        )

# =========================================================
# HORÁRIOS (admin)
# =========================================================
def listar_horarios():
    with get_conn() as conn:
        return conn.execute(
            "SELECT dia_semana, hora_abertura, hora_fecho, ativo "
            "FROM horarios WHERE empresa_id = ? ORDER BY dia_semana",
            (EMPRESA_ID,),
        ).fetchall()


def guardar_horario(dia_semana, hora_abertura, hora_fecho, ativo):
    with get_conn() as conn:
        existe = conn.execute(
            "SELECT id FROM horarios WHERE empresa_id = ? AND dia_semana = ?",
            (EMPRESA_ID, dia_semana),
        ).fetchone()
        if existe:
            conn.execute(
                "UPDATE horarios SET hora_abertura = ?, hora_fecho = ?, ativo = ? "
                "WHERE empresa_id = ? AND dia_semana = ?",
                (hora_abertura, hora_fecho, int(ativo), EMPRESA_ID, dia_semana),
            )
        else:
            conn.execute(
                "INSERT INTO horarios (empresa_id, dia_semana, hora_abertura, hora_fecho, ativo) "
                "VALUES (?, ?, ?, ?, ?)",
                (EMPRESA_ID, dia_semana, hora_abertura, hora_fecho, int(ativo)),
            )
        conn.commit()


def listar_dias_bloqueados():
    with get_conn() as conn:
        return conn.execute(
            "SELECT data, motivo FROM dias_bloqueados WHERE empresa_id = ? ORDER BY data",
            (EMPRESA_ID,),
        ).fetchall()


def adicionar_dia_bloqueado(data_str, motivo):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO dias_bloqueados (empresa_id, data, motivo) VALUES (?, ?, ?)",
            (EMPRESA_ID, data_str, motivo),
        )
        conn.commit()


def remover_dia_bloqueado(data_str):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM dias_bloqueados WHERE empresa_id = ? AND data = ?",
            (EMPRESA_ID, data_str),
        )
        conn.commit()