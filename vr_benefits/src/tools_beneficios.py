import os, re
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from util import parse_date, month_bounds, intersect_days

STATE = {
    "frames": {},   # nome_base -> DataFrame
    "config": {
        "key": "matricula",
        "key_regex": r"^\d{5,12}$",
        "cutoff_day": 15,
        "competencia": None,  # 'YYYY-MM'
    },
    "logs": {"avisos": [], "exclusoes": [], "pendencias": []},
    "artifacts": {},
}

EXPECTED_FILES = [
    "ATIVOS.xlsx",
    "ADMISSÃO ABRIL.xlsx",
    "DESLIGADOS.xlsx",
    "FÉRIAS.xlsx",
    "AFASTAMENTOS.xlsx",
    "EXTERIOR.xlsx",
    "APRENDIZ.xlsx",
    "ESTÁGIO.xlsx",
    "Base sindicato x valor.xlsx",
    "Base dias uteis.xlsx",
]

# ---------------- Loading ----------------
def _read_excel_safe(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    return df

def load_sources(input_dir: str) -> Dict:
    loaded = 0
    for fname in EXPECTED_FILES:
        path = os.path.join(input_dir, fname)
        if os.path.exists(path):
            try:
                df = _read_excel_safe(path)
                STATE["frames"][fname] = df
                loaded += 1
            except Exception as e:
                STATE["logs"]["avisos"].append(f"Erro ao ler {fname}: {e}")
        else:
            STATE["logs"]["avisos"].append(f"Não encontrado: {fname}")
    return {"ok": True, "loaded": loaded, "avisos": STATE["logs"]["avisos"]}

def set_config(competencia: str, key: str = "matricula", key_regex: str = r"^\d{5,12}$", cutoff_day:int=15) -> Dict:
    STATE["config"]["competencia"] = competencia
    STATE["config"]["key"] = key
    STATE["config"]["key_regex"] = key_regex
    STATE["config"]["cutoff_day"] = int(cutoff_day)
    return {"ok": True, "config": STATE["config"]}

# ---------------- Harmonization ----------------
def _ensure_key(df: pd.DataFrame, key: str) -> pd.DataFrame:
    if key in df.columns:
        return df
    for c in df.columns:
        # Trata "Cadastro" como matrícula para arquivos EXTERIOR
        if c.lower() in ["cadastro"]:
            df = df.rename(columns={c: key})
            return df
        # Trata variações de matrícula
        if c.lower().startswith("matric"):
            df = df.rename(columns={c: key})
            return df
    return df

def validate_and_clean() -> Dict:
    key = STATE["config"]["key"]
    regex = re.compile(STATE["config"]["key_regex"])

    for name, df in STATE["frames"].items():
        df = _ensure_key(df, key)
        if key not in df.columns:
            STATE["logs"]["avisos"].append(f"{name}: sem coluna-chave '{key}'")
            continue
        # normaliza chave só dígitos
        df[key] = df[key].astype(str).str.replace(r"\D", "", regex=True)
        mask = df[key].str.match(regex)
        removed = int((~mask).sum())
        if removed:
            STATE["logs"]["avisos"].append(f"{name}: removidos {removed} registros com chave inválida")
        STATE["frames"][name] = df[mask].drop_duplicates().reset_index(drop=True)
    return {"ok": True, "avisos": STATE["logs"]["avisos"]}

def _build_base_elegiveis() -> pd.DataFrame:
    key = STATE["config"]["key"]
    ativos = STATE["frames"].get("ATIVOS.xlsx", pd.DataFrame())
    adm = STATE["frames"].get("ADMISSÃO ABRIL.xlsx", pd.DataFrame())

    ativos = _ensure_key(ativos, key)
    adm = _ensure_key(adm, key)

    base = pd.concat([ativos, adm], ignore_index=True) if not adm.empty else ativos.copy()
    base = base.drop_duplicates(subset=[key]).reset_index(drop=True)

    # Normaliza nomes candidatos
    ren = {}
    for c in base.columns:
        cl = c.lower()
        if cl in ["nome completo", "nome_colaborador", "colaborador", "funcionario"]:
            ren[c] = "nome"
        if cl in ["sind", "sindicato_col", "sindicato nome"]:
            ren[c] = "sindicato"
        if cl in ["admissao", "data admissao", "data de admissão", "dt_adm"]:
            ren[c] = "data_admissao"
        if cl in ["desligamento", "data desligamento", "dt_desl"]:
            ren[c] = "data_desligamento"
    if ren:
        base = base.rename(columns=ren)

    # Parse datas se presentes
    if "data_admissao" in base.columns:
        base["data_admissao"] = base["data_admissao"].apply(parse_date)
    if "data_desligamento" in base.columns:
        base["data_desligamento"] = base["data_desligamento"].apply(parse_date)

    return base

def exclude_non_eligible() -> Dict:
    key = STATE["config"]["key"]
    base = _build_base_elegiveis()

    excl = set()
    # Exclusão por arquivos específicos
    for src in ["APRENDIZ.xlsx", "ESTÁGIO.xlsx", "EXTERIOR.xlsx"]:
        df = STATE["frames"].get(src, pd.DataFrame())
        df = _ensure_key(df, key)
        if key in df.columns:
            excl.update(df[key].dropna().unique().tolist())
    
    # Exclusão de diretores por cargo
    diretores_excl = set()
    if key in base.columns:
        # Procura colunas que podem conter cargo/função
        cargo_cols = []
        for col in base.columns:
            col_lower = col.lower().strip()
            if any(termo in col_lower for termo in ['cargo', 'funcao', 'função', 'titulo', 'posicao', 'position']):
                cargo_cols.append(col)
        
        # Identifica diretores pelas colunas de cargo
        for cargo_col in cargo_cols:
            if cargo_col in base.columns:
                mask_diretores = base[cargo_col].astype(str).str.upper().str.contains(
                    'DIRETOR|DIRETORA|CEO|PRESIDENTE|PRESIDENTA|VP |VICE.PRESIDENTE', 
                    regex=True, na=False
                )
                diretores_matriculas = base.loc[mask_diretores, key].dropna().unique().tolist()
                diretores_excl.update(diretores_matriculas)
                if diretores_matriculas:
                    STATE["logs"]["exclusoes"].append(f"Identificados {len(diretores_matriculas)} diretores em coluna '{cargo_col}'")
    
    # Combina todas as exclusões
    total_excl = excl.union(diretores_excl)

    before = len(base)
    if key in base.columns and len(total_excl) > 0:
        base = base[~base[key].isin(list(total_excl))].reset_index(drop=True)
    after = len(base)

    STATE["artifacts"]["ELEGIVEIS_BASE"] = base
    STATE["logs"]["exclusoes"].append(f"Removidos {before-after} total (aprendiz/estágio/exterior: {len(excl)}, diretores: {len(diretores_excl)})")
    return {"ok": True, "removidos": before-after}

# ---------------- Feriados por Região ----------------
def _get_feriados_nacionais(year: int) -> List[datetime]:
    """Retorna lista de feriados nacionais fixos para o ano"""
    feriados = [
        datetime(year, 1, 1),   # Confraternização Universal
        datetime(year, 4, 21),  # Tiradentes  
        datetime(year, 5, 1),   # Dia do Trabalhador
        datetime(year, 9, 7),   # Independência do Brasil
        datetime(year, 10, 12), # Nossa Senhora Aparecida
        datetime(year, 11, 2),  # Finados
        datetime(year, 11, 15), # Proclamação da República
        datetime(year, 12, 25), # Natal
    ]
    return feriados

def _get_feriados_regionais(year: int, estado: str) -> List[datetime]:
    """Retorna lista de feriados específicos por estado"""
    feriados_regionais = {
        "São Paulo": [
            datetime(year, 1, 25),  # Aniversário de São Paulo (cidade)
            datetime(year, 7, 9),   # Revolução Constitucionalista (estado)
        ],
        "Rio de Janeiro": [
            datetime(year, 4, 23),  # São Jorge
            datetime(year, 10, 28), # Dia do Servidor Público (se estadual)
        ],
        "Paraná": [
            datetime(year, 12, 19), # Emancipação do Paraná
        ],
        "Rio Grande do Sul": [
            datetime(year, 9, 20),  # Revolução Farroupilha
        ]
    }
    return feriados_regionais.get(estado, [])

def _calcular_dias_uteis_com_feriados(year: int, month: int, dias_base: int, estado: str = None) -> int:
    """Calcula dias úteis considerando feriados nacionais e regionais"""
    mstart, mend = month_bounds(year, month)
    
    # Feriados nacionais
    feriados = _get_feriados_nacionais(year)
    
    # Feriados regionais se estado fornecido
    if estado:
        feriados.extend(_get_feriados_regionais(year, estado))
    
    # Conta feriados que caem em dias úteis no mês
    feriados_no_mes = 0
    current_date = mstart
    while current_date <= mend:
        # Se é dia útil (segunda a sexta) e é feriado
        if current_date.weekday() < 5 and current_date in feriados:
            feriados_no_mes += 1
        current_date += timedelta(days=1)
    
    # Ajusta dias úteis subtraindo feriados
    dias_ajustados = max(0, dias_base - feriados_no_mes)
    return dias_ajustados

# ---------------- Workdays ----------------
def derive_workdays() -> Dict:
    from util import parse_date, month_bounds
    comp = STATE["config"]["competencia"]
    year, month = map(int, comp.split("-"))
    mstart, mend = month_bounds(year, month)

    key = STATE["config"]["key"]
    eleg = STATE["artifacts"].get("ELEGIVEIS_BASE", pd.DataFrame()).copy()
    if eleg.empty:
        return {"ok": True, "rows": 0}

    # Normaliza nome da coluna Sindicato para minúsculo
    for col in eleg.columns:
        if col.lower() == "sindicato":
            eleg = eleg.rename(columns={col: "sindicato"})
            break

    # Normaliza datas do eleg
    for col in ["admissao","data_admissao","desligamento","data_desligamento","comunicado_ok_data"]:
        if col in eleg.columns:
            eleg[col] = eleg[col].apply(parse_date)

    # Base dias uteis
    base_du = STATE["frames"].get("Base dias uteis.xlsx", pd.DataFrame()).copy()
    
    # Trata arquivo Base dias uteis com estrutura específica
    if not base_du.empty:
        # Se a primeira linha tem "SINDICADO" e "DIAS UTEIS", use-a como header
        if len(base_du.columns) >= 2:
            first_row = base_du.iloc[0] if not base_du.empty else pd.Series()
            if any("SINDICAD" in str(val).upper() for val in first_row.values):
                # Usa primeira linha como header
                base_du.columns = base_du.iloc[0]
                base_du = base_du.drop(base_du.index[0]).reset_index(drop=True)
            
            # Identifica colunas baseado no conteúdo
            sindicato_col = None
            dias_col = None
            
            for col in base_du.columns:
                col_str = str(col).upper()
                if "SINDICAD" in col_str:
                    sindicato_col = col
                elif "DIAS" in col_str:
                    dias_col = col
            
            # Se não encontrou pelas cabeçalhos, usa posição (primeira e segunda colunas)
            if not sindicato_col and len(base_du.columns) >= 1:
                sindicato_col = base_du.columns[0]
            if not dias_col and len(base_du.columns) >= 2:
                dias_col = base_du.columns[1]
            
            if sindicato_col and dias_col:
                base_du = base_du.rename(columns={sindicato_col: "sindicato", dias_col: "dias_uteis"})
                # Remove linhas vazias
                base_du = base_du.dropna(subset=["sindicato", "dias_uteis"])
                base_du = base_du[base_du["sindicato"].astype(str).str.strip() != ""]
    
    du_map = {}
    if "sindicato" in base_du.columns and "dias_uteis" in base_du.columns:
        for _, r in base_du.iterrows():
            try:
                sindicato_name = str(r["sindicato"]).strip()
                dias_val = str(r["dias_uteis"]).strip()
                if sindicato_name and dias_val and dias_val.replace('.','').replace(',','').isdigit():
                    du_map[sindicato_name] = int(float(dias_val.replace(',', '.')))
            except Exception:
                pass

    # Primeiro, cria a coluna dias_uteis_base
    if "sindicato" in eleg.columns and du_map:
        eleg["dias_uteis_base"] = eleg["sindicato"].map(du_map).fillna(22).astype(int)
    else:
        eleg["dias_uteis_base"] = 22  # fallback

    # Aplicar ajuste de feriados por região
    def _extrair_estado_sindicato(sindicato_str):
        """Extrai estado do nome do sindicato"""
        if pd.isna(sindicato_str):
            return None
        sindicato_upper = str(sindicato_str).upper()
        if " PR " in sindicato_upper or "PARANÁ" in sindicato_upper or "CURITIBA" in sindicato_upper:
            return "Paraná"
        elif " RJ " in sindicato_upper or "RIO DE JANEIRO" in sindicato_upper:
            return "Rio de Janeiro"
        elif " RS " in sindicato_upper or "RIO GRANDE DO SUL" in sindicato_upper:
            return "Rio Grande do Sul"
        elif " SP " in sindicato_upper or "SÃO PAULO" in sindicato_upper or "SAO PAULO" in sindicato_upper:
            return "São Paulo"
        return None

    # Agora ajusta dias úteis considerando feriados regionais
    if "sindicato" in eleg.columns:
        for i, row in eleg.iterrows():
            estado = _extrair_estado_sindicato(row.get("sindicato"))
            if estado:
                dias_base = int(row["dias_uteis_base"])
                dias_ajustados = _calcular_dias_uteis_com_feriados(year, month, dias_base, estado)
                eleg.at[i, "dias_uteis_base"] = dias_ajustados

    # Janela considerada: admissão/desligamento
    def _first_day(row):
        da = row.get("admissao") or row.get("data_admissao")
        return max(da, mstart) if da and da > mstart else mstart
    def _last_day(row):
        dd = row.get("desligamento") or row.get("data_desligamento")
        return min(dd, mend) if dd and dd < mend else mend

    eleg["first_day"] = eleg.apply(_first_day, axis=1)
    eleg["last_day"]  = eleg.apply(_last_day, axis=1)

    total_days_month = (mend - mstart).days + 1
    def prop_days(row):
        span = (row["last_day"] - row["first_day"]).days + 1
        if span <= 0:
            return 0
        return int(round(row["dias_uteis_base"] * (span / total_days_month)))
    eleg["dias_uteis_calc"] = eleg.apply(prop_days, axis=1)

    # Férias e Afastamentos
    def _prep_intervals(df):
        if df.empty:
            return pd.DataFrame(columns=[key, "dt_ini", "dt_fim"])
        df = df.copy()
        df = _ensure_key(df, key)
        ren = {}
        for c in df.columns:
            cl = c.lower()
            if any(w in cl for w in ["inicio","início","data_inicial","ini"]):
                ren[c] = "dt_ini"
            if any(w in cl for w in ["fim","final","data_final","term"]):
                ren[c] = "dt_fim"
        if ren:
            df = df.rename(columns=ren)
        if "dt_ini" in df.columns:
            df["dt_ini"] = df["dt_ini"].apply(parse_date)
        if "dt_fim" in df.columns:
            df["dt_fim"] = df["dt_fim"].apply(parse_date)
        return df[[c for c in [key,"dt_ini","dt_fim"] if c in df.columns]]

    ferias = _prep_intervals(STATE["frames"].get("FÉRIAS.xlsx", pd.DataFrame()))
    afast  = _prep_intervals(STATE["frames"].get("AFASTAMENTOS.xlsx", pd.DataFrame()))

    def subtract(df_interv):
        if df_interv.empty or not {"dt_ini","dt_fim"}.issubset(df_interv.columns):
            return
        by_mat = {}
        for _, r in df_interv.iterrows():
            mat = str(r.get(key, "")).strip()
            if not mat: continue
            by_mat.setdefault(mat, []).append((r["dt_ini"], r["dt_fim"]))
        for i, row in eleg.iterrows():
            mat = str(row.get(key, "")).strip()
            if not mat or mat not in by_mat: continue
            inter_days = 0
            for (a,b) in by_mat[mat]:
                inter_days += intersect_days(row["first_day"], row["last_day"], a, b)
            if inter_days > 0:
                delta = int(round(row["dias_uteis_base"] * (inter_days / total_days_month)))
                eleg.at[i,"dias_uteis_calc"] = max(0, int(eleg.at[i,"dias_uteis_calc"]) - delta)

    subtract(ferias)
    subtract(afast)

    # Desligados + Regra do dia 15
    deslig = STATE["frames"].get("DESLIGADOS.xlsx", pd.DataFrame()).copy()
    if not deslig.empty:
        deslig = _ensure_key(deslig, key)
        for c in list(deslig.columns):
            cl = c.lower()
            if "deslig" in cl and "data_desligamento" not in deslig.columns:
                deslig = deslig.rename(columns={c: "data_desligamento"})
            if "comunic" in cl and "comunicado_ok_data" not in deslig.columns:
                deslig = deslig.rename(columns={c: "comunicado_ok_data"})
        if "data_desligamento" in deslig.columns:
            deslig["data_desligamento"] = deslig["data_desligamento"].apply(parse_date)
        if "comunicado_ok_data" in deslig.columns:
            deslig["comunicado_ok_data"] = deslig["comunicado_ok_data"].apply(parse_date)

        join_cols = [c for c in ["matricula","data_desligamento","comunicado_ok_data"] if c in deslig.columns]
        if join_cols:
            eleg = eleg.merge(deslig[join_cols].drop_duplicates(), how="left", on=key)

        cutoff = STATE["config"]["cutoff_day"]
        for i, row in eleg.iterrows():
            cod = row.get("comunicado_ok_data")
            if pd.notna(cod) and hasattr(cod, "day") and cod.day <= cutoff and cod.month == month and cod.year == year:
                eleg.at[i, "dias_uteis_calc"] = 0
            elif "data_desligamento" in eleg.columns and pd.notna(row.get("data_desligamento")):
                # Proporcional até a data de desligamento já foi contemplado pela janela first/last_day
                pass
            else:
                # Sem comunicado para um desligamento no mês => pendência
                pass

    STATE["artifacts"]["WORKDAYS"] = eleg
    return {"ok": True, "rows": len(eleg)}

# ---------------- Validações de Integridade ----------------
def validate_integrity() -> Dict:
    """Executa validações automáticas de integridade dos dados processados"""
    validacoes = []
    warnings = []
    errors = []
    
    # Validação 1: Verifica se todos os arquivos esperados foram carregados
    missing_files = []
    for expected_file in EXPECTED_FILES:
        if expected_file not in STATE["frames"] or STATE["frames"][expected_file].empty:
            missing_files.append(expected_file)
    
    if missing_files:
        warnings.append(f"Arquivos não encontrados/vazios: {missing_files}")
    else:
        validacoes.append("✓ Todos os arquivos esperados foram carregados")
    
    # Validação 2: Verifica se há funcionários elegíveis
    elegiveis = STATE["artifacts"].get("ELEGIVEIS_BASE", pd.DataFrame())
    if elegiveis.empty:
        errors.append("❌ Nenhum funcionário elegível encontrado")
    else:
        validacoes.append(f"✓ {len(elegiveis)} funcionários elegíveis identificados")
    
    # Validação 3: Verifica consistência de datas
    workdays = STATE["artifacts"].get("WORKDAYS", pd.DataFrame())
    if not workdays.empty:
        # Admissões futuras
        comp = STATE["config"]["competencia"]
        year, month = map(int, comp.split("-"))
        mstart, mend = month_bounds(year, month)
        
        if "data_admissao" in workdays.columns:
            admissoes_futuras = workdays[
                (workdays["data_admissao"].notna()) & 
                (workdays["data_admissao"] > mend)
            ]
            if len(admissoes_futuras) > 0:
                warnings.append(f"⚠️ {len(admissoes_futuras)} funcionários com data de admissão futura")
        
        # Desligamentos no passado sem comunicado
        if "data_desligamento" in workdays.columns and "comunicado_ok_data" in workdays.columns:
            deslig_sem_comunicado = workdays[
                (workdays["data_desligamento"].notna()) & 
                (workdays["data_desligamento"] < mstart) &
                (workdays["comunicado_ok_data"].isna())
            ]
            if len(deslig_sem_comunicado) > 0:
                warnings.append(f"⚠️ {len(deslig_sem_comunicado)} desligamentos antigos sem data de comunicado")
    
    # Validação 4: Verifica cálculos financeiros
    finished = STATE["artifacts"].get("FINISHED", pd.DataFrame())
    if not finished.empty:
        # Valores zerados
        vr_zerado = finished[finished["VR Total"] == 0]
        if len(vr_zerado) > 0:
            validacoes.append(f"ℹ️ {len(vr_zerado)} funcionários com VR Total = 0 (normal para desligados/afastados)")
        
        # Valores muito altos (possível erro)
        valor_alto_limite = 2000  # R$ 2000 por mês
        vr_alto = finished[finished["VR Total"] > valor_alto_limite]
        if len(vr_alto) > 0:
            warnings.append(f"⚠️ {len(vr_alto)} funcionários com VR Total > R$ {valor_alto_limite} - verificar")
        
        # Verificação de proporção empresa/funcionário
        prop_incorreta = finished[
            abs(finished["Custo Empresa"] - finished["VR Total"] * 0.8) > 0.01
        ]
        if len(prop_incorreta) > 0:
            errors.append(f"❌ {len(prop_incorreta)} registros com proporção empresa incorreta (deve ser 80%)")
        else:
            validacoes.append("✓ Proporção empresa/funcionário (80%/20%) correta")
    
    # Validação 5: Verifica mapeamento de sindicatos
    if not finished.empty and "valor_diario" in finished.columns:
        sem_valor = finished[finished["valor_diario"] == 0]
        if len(sem_valor) > 0:
            warnings.append(f"⚠️ {len(sem_valor)} funcionários sem valor diário mapeado (sindicato não encontrado)")
        
        valores_unicos = finished["valor_diario"].value_counts()
        validacoes.append(f"ℹ️ Valores diários únicos encontrados: {dict(valores_unicos)}")
    
    # Compilar resultado
    resultado = {
        "ok": len(errors) == 0,
        "validacoes_ok": len(validacoes),
        "warnings": len(warnings),
        "errors": len(errors),
        "detalhes": {
            "validacoes": validacoes,
            "warnings": warnings,
            "errors": errors
        }
    }
    
    # Adiciona ao log
    STATE["logs"]["avisos"].extend(validacoes + warnings)
    if errors:
        STATE["logs"]["pendencias"].extend(errors)
    
    return resultado

# ---------------- Financials ----------------
def compute_financials() -> Dict:
    df = STATE["artifacts"].get("WORKDAYS", pd.DataFrame()).copy()
    base_val = STATE["frames"].get("Base sindicato x valor.xlsx", pd.DataFrame()).copy()

    if not df.empty and "sindicato" in df.columns and not base_val.empty:
        # Identifica a coluna de estado/sindicato na base de valores
        estado_col = None
        valor_col = None
        
        for c in list(base_val.columns):
            cl = str(c).lower().replace('\xa0', '').strip()  # Remove caracteres especiais
            if "estado" in cl:
                estado_col = c
            if "valor" in cl:
                valor_col = c
        
        if estado_col and valor_col:
            # Renomeia as colunas para padronizar
            base_val = base_val.rename(columns={estado_col: "estado", valor_col: "valor_diario"})
            
            # Remove linhas vazias ou com dados inválidos
            base_val = base_val.dropna(subset=["estado", "valor_diario"])
            base_val = base_val[base_val["estado"].astype(str).str.strip() != ""]
            base_val = base_val[base_val["valor_diario"].astype(str).str.strip() != ""]
            
            # Mapeia estado para valor
            valor_map = {}
            for _, r in base_val.iterrows():
                try:
                    estado = str(r["estado"]).strip()
                    valor_str = str(r["valor_diario"]).replace(",", ".")
                    if estado and valor_str and valor_str.replace('.','').isdigit():
                        valor_map[estado] = float(valor_str)
                except Exception:
                    continue
            
            # Para funcionários, mapeia sindicato para estado e depois para valor
            def get_valor_por_sindicato(sindicato_str):
                if pd.isna(sindicato_str):
                    return 0.0
                    
                sindicato_str = str(sindicato_str).strip()
                
                # Extrai estado do nome do sindicato
                sindicato_upper = sindicato_str.upper()
                if " PR " in sindicato_upper or "PARANÁ" in sindicato_upper or "CURITIBA" in sindicato_upper:
                    return valor_map.get("Paraná", 0.0)
                elif " RJ " in sindicato_upper or "RIO DE JANEIRO" in sindicato_upper:
                    return valor_map.get("Rio de Janeiro", 0.0)
                elif " RS " in sindicato_upper or "RIO GRANDE DO SUL" in sindicato_upper:
                    return valor_map.get("Rio Grande do Sul", 0.0)
                elif " SP " in sindicato_upper or "SÃO PAULO" in sindicato_upper or "SAO PAULO" in sindicato_upper:
                    return valor_map.get("São Paulo", 0.0)
                else:
                    # Valor padrão se não conseguir identificar o estado
                    return list(valor_map.values())[0] if valor_map else 0.0
            
            df["valor_diario"] = df["sindicato"].apply(get_valor_por_sindicato)
            
            # Log dos valores mapeados para debug
            valores_encontrados = df["valor_diario"].value_counts()
            STATE["logs"]["avisos"].append(f"Valores mapeados: {dict(valores_encontrados)}")
            
        else:
            STATE["logs"]["avisos"].append("Base sindicato x valor.xlsx: colunas de estado e valor não identificadas; usando 0.")
            df["valor_diario"] = 0.0
    else:
        df["valor_diario"] = 0.0

    def to_float(x):
        if x is None or (isinstance(x, float) and pd.isna(x)):
            return 0.0
        s = str(x).replace(",", ".")
        try:
            return float(s)
        except Exception:
            return 0.0

    df["valor_diario"] = df["valor_diario"].apply(to_float).fillna(0.0)
    df["dias_uteis_calc"] = df["dias_uteis_calc"].fillna(0).astype(int)

    df["VR Total"] = (df["dias_uteis_calc"] * df["valor_diario"]).round(2)
    df["Custo Empresa"] = (df["VR Total"] * 0.8).round(2)
    df["Desconto Colaborador"] = (df["VR Total"] * 0.2).round(2)

    STATE["artifacts"]["FINISHED"] = df
    return {"ok": True, "rows": len(df)}

# ---------------- Export ----------------
def export_layout(output_dir: str, template_path: str) -> Dict:
    os.makedirs(output_dir, exist_ok=True)
    df = STATE["artifacts"].get("FINISHED", pd.DataFrame()).copy()
    if df.empty:
        return {"ok": False, "error": "Nada para exportar"}
    comp = STATE["config"]["competencia"]
    y, m = comp.split("-")
    out_xlsx = os.path.join(output_dir, f"VR_Mensal_{y}{m}.xlsx")

    # Determina nome da aba baseado no template
    out_sheet = "VR Mensal"
    try:
        xls = pd.ExcelFile(template_path)
        if xls.sheet_names:
            out_sheet = xls.sheet_names[0]
    except Exception:
        pass

    # Preparação do DataFrame para exportação
    df_export = df.copy()
    key = STATE["config"]["key"]
    
    # Busca e aplica datas de admissão em todos os arquivos
    admissao_map = {}
    
    # Busca em TODOS os arquivos carregados
    for arquivo, arquivo_data in STATE["frames"].items():
        if arquivo_data.empty:
            continue
            
        # Procura por qualquer coluna que possa conter data de admissão
        colunas_data_possiveis = []
        for col in arquivo_data.columns:
            col_lower = col.lower().strip()
            # Verifica termos relacionados a admissão/contratação
            if any(termo in col_lower for termo in [
                "admiss", "adm", "contrata", "entrada", "inicio", "ingresso", 
                "data", "dt_", "date"
            ]):
                # Exclui colunas que são claramente de demissão/saída
                if not any(termo_exclusao in col_lower for termo_exclusao in [
                    "demiss", "saida", "sai", "deslig", "fim", "termino", "rescis"
                ]):
                    colunas_data_possiveis.append(col)
        
        # Se encontrou colunas potenciais
        for col_admissao in colunas_data_possiveis:
            # Prepara dados para mapeamento
            admissao_clean = arquivo_data.copy()
            admissao_clean = _ensure_key(admissao_clean, key)
            
            if key in admissao_clean.columns:
                # Normaliza matrícula (remove caracteres não numéricos, mas mantém formato original)
                admissao_clean[key] = admissao_clean[key].astype(str).str.replace(r"\D", "", regex=True).astype('int64')
                
                # Tenta converter para data
                try:
                    admissao_clean[col_admissao] = pd.to_datetime(admissao_clean[col_admissao], errors='coerce')
                    
                    # Conta quantas datas válidas encontrou
                    datas_validas = admissao_clean[col_admissao].notna().sum()
                    
                    if datas_validas > 0:
                        # Procura coluna que indica status (demitido, não recebe VR, etc.)
                        coluna_status = None
                        for col in admissao_clean.columns:
                            if col.lower() in ['status', 'situacao', 'situação'] or 'unnamed' in col.lower():
                                valores_status = admissao_clean[col].value_counts(dropna=False)
                                # Se tem valores como "demitido" ou "não recebe", é uma coluna de status
                                if any(termo in str(v).lower() for v in valores_status.index 
                                      for termo in ['demitido', 'não recebe', 'nao recebe', 'excluir']):
                                    coluna_status = col
                                    break
                        
                        # Adiciona ao mapeamento aplicando regras de negócio
                        for _, row in admissao_clean.iterrows():
                            if pd.notna(row[col_admissao]):
                                # Verifica regra de negócio
                                deve_receber = True
                                
                                if coluna_status and pd.notna(row[coluna_status]):
                                    status = str(row[coluna_status]).lower()
                                    if any(termo in status for termo in ['demitido', 'não recebe', 'nao recebe']):
                                        deve_receber = False
                                
                                if deve_receber:
                                    matricula_str = str(int(row[key]))
                                    if matricula_str not in admissao_map:
                                        admissao_map[matricula_str] = row[col_admissao].strftime('%d/%m/%Y')
                        
                except Exception as e:
                    pass
    
    # Aplica mapeamento se encontrou dados
    if admissao_map:
        df_export["Data Admissão"] = df_export[key].map(admissao_map)
    
    # Log dos arquivos verificados para debug
    STATE["logs"]["avisos"].append(f"Arquivos verificados para datas: {list(STATE['frames'].keys())}")
    STATE["logs"]["avisos"].append(f"Funcionários com data de admissão: {len(admissao_map)}")

    # Mapeamentos para padronizar nomes das colunas
    mapping = {
        "matricula": "Matricula",
        "sindicato": "Sindicato do Colaborador", 
        "dias_uteis_calc": "Dias",
        "valor_diario": "VALOR DIÁRIO VR",
        "VR Total": "TOTAL",
        "Custo Empresa": "Custo empresa",
        "Desconto Colaborador": "Desconto profissional",
        # REMOVIDO: "Admissão": "Data Admissão",  # Conflitava com nossa função
        "admissao": "Data Admissão", 
        "data_admissao": "Data Admissão",
        "TITULO DO CARGO": "Cargo"
    }
    
    # Aplica mapeamentos
    for k, v in mapping.items():
        if k in df_export.columns:
            df_export = df_export.rename(columns={k: v})

    # Define colunas principais para exportação (baseado no template visualizado)
    export_order = [
        "Matricula",
        "Data Admissão", 
        "Sindicato do Colaborador",
        "Competencia",  # Será adicionada
        "Dias",
        "VALOR DIÁRIO VR", 
        "TOTAL",
        "Custo empresa",
        "Desconto profissional",
        "OBS GERAL"  # Será adicionada
    ]
    
    # Adiciona colunas faltantes
    df_export["Competencia"] = f"{y}-{m}-01"
    df_export["OBS GERAL"] = None
    
    # Seleciona colunas existentes na ordem preferida
    final_cols = []
    for col in export_order:
        if col in df_export.columns:
            final_cols.append(col)
    
    # Adiciona outras colunas importantes que não estão na lista
    other_important = [col for col in df_export.columns 
                      if col not in final_cols and col not in ['EMPRESA', 'DESC. SITUACAO', 'Cargo', 'Unnamed: 3', 'dias_uteis_base', 'first_day', 'last_day', 'data_desligamento']]
    final_cols.extend(other_important)

    # Salva o Excel no formato padrão
    with pd.ExcelWriter(out_xlsx, engine='openpyxl') as writer:
        # Aba principal com dados organizados
        df_final = df_export[final_cols].copy()
        df_final.to_excel(writer, sheet_name=out_sheet, index=False)
        
        # Abas de LOG
        pd.DataFrame(STATE["logs"]["avisos"], columns=["avisos"]).to_excel(writer, sheet_name="LOG_AVISOS", index=False)
        pd.DataFrame(STATE["logs"]["exclusoes"], columns=["exclusoes"]).to_excel(writer, sheet_name="LOG_EXCLUSOES", index=False)
        pd.DataFrame(STATE["logs"]["pendencias"], columns=["pendencias"]).to_excel(writer, sheet_name="LOG_PENDENCIAS", index=False)

    return {"ok": True, "file": out_xlsx}
