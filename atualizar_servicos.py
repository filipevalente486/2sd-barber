from database import get_conn, EMPRESA_ID

# Lista final de servicos da 2SD.Barber.
# NOTA: o ultimo servico veio sem preco no pedido -> 20.00 EUR provisorio.
servicos = [
    ("Corte",                              "Corte com acabamento profissional.",       30, 12.0),
    ("Corte + Barba",                      "Corte, contorno e definicao da barba.",    45, 15.0),
    ("Corte + Barboterapia",               "Servico completo.",                        45, 17.0),
    ("Barba",                              "Definicao e acabamento.",                  20,  5.0),
    ("Barboterapia",                       "Lavagem e preparacao.",                    20,  7.0),
    ("Sobrancelha",                        "Limpeza e definicao.",                     10,  3.0),
    ("Corte + Sobrancelha",                "Acabamento e limpeza.",                    40, 14.0),
    ("Corte + Barba + Sobrancelha",        "Pacote completo.",                         55, 17.0),
    ("Corte + Barboterapia + Sobrancelha", "Pacote completo com barboterapia.",        60, 20.0),  # <- PRECO POR CONFIRMAR
]

with get_conn() as conn:
    conn.execute("DELETE FROM servicos WHERE empresa_id = ?", (EMPRESA_ID,))
    for i, (nome, desc, dur, preco) in enumerate(servicos):
        conn.execute(
            "INSERT INTO servicos (empresa_id, nome, descricao, duracao_min, preco, ordem) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (EMPRESA_ID, nome, desc, dur, preco, i),
        )
    conn.commit()

    print("Servicos atualizados:\n")
    print(f"{'#':<3}{'Servico':<40}{'Dur':>6}{'Preco':>10}")
    print("-" * 60)
    for row in conn.execute(
        "SELECT nome, duracao_min, preco FROM servicos WHERE empresa_id = ? ORDER BY ordem",
        (EMPRESA_ID,),
    ):
        print(f"{'':<3}{row[0]:<40}{row[1]:>4} m{row[2]:>9.2f} EUR")
    print(f"\nTotal: {len(servicos)} servicos")
