import os
import argparse
import requests
import json
import pandas as pd
from datetime import datetime

# Importações da biblioteca Rich (tratamento de interface de terminal rico)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
except ImportError:
    # Fallback caso a biblioteca rich não esteja instalada no ambiente
    def safe_print(text, *args, **kwargs):
        try:
            print(text, *args, **kwargs)
        except UnicodeEncodeError:
            import sys
            encoding = sys.stdout.encoding or 'ascii'
            clean_text = str(text).encode(encoding, errors='replace').decode(encoding)
            print(clean_text, *args, **kwargs)

    class Console:
        def print(self, text, *args, **kwargs):
            safe_print(text, *args, **kwargs)
        def log(self, text):
            safe_print(text)
            
    def Panel(text, title=None, border_style=None):
        return f"=== {title or ''} ===\n{text}"
        
    def Table(title=None):
        class SimpleTable:
            def __init__(self):
                self.title = title
                self.cols = []
                self.rows = []
            def add_column(self, name, *args, **kwargs):
                self.cols.append(name)
            def add_row(self, *rows, **kwargs):
                self.rows.append(rows)
            def __str__(self):
                res = []
                if self.title:
                    res.append(f"--- {self.title} ---")
                header = " | ".join(self.cols)
                res.append(header)
                res.append("-" * len(header))
                for row in self.rows:
                    res.append(" | ".join(str(r) for r in row))
                return "\n".join(res)
        return SimpleTable()
        
    def rprint(text):
        safe_print(text)

console = Console()

# ID Fixo da Planilha Google Sheets
DEFAULT_SHEET_ID = "1DmmBbprkeVmd5iHLOCigxXK7ttX0CAoGqcfpyJljuHI"

def main():
    # Banner elegante
    console.print(Panel(
        "[bold purple]📦 Picking & Arrumação - Automação CLI[/bold purple]\n"
        "[dim]Ferramenta inteligente de sincronização e exportação de inventário[/dim]",
        border_style="purple"
    ))

    # Configuração de Argumentos da Linha de Comando
    parser = argparse.ArgumentParser(description="Script para automatizar exportação e sincronização de picking.")
    parser.add_argument("-s", "--sheet-id", type=str, default=DEFAULT_SHEET_ID, help="ID da planilha do Google Sheets.")
    parser.add_argument("-o", "--output", type=str, default=None, help="Diretório de saída para o JSON. Padrão: Desktop.")
    parser.add_argument("-a", "--send-api", type=str, default=None, help="URL de API externa para enviar o JSON (POST).")
    parser.add_argument("-d", "--drop-col", type=str, default="desc_produto", help="Coluna a ser excluída no arquivo JSON final.")
    
    args = parser.parse_args()

    # Monta URL do CSV
    url_csv = f"https://docs.google.com/spreadsheets/d/{args.sheet_id}/export?format=csv"

    # Etapa 1: Leitura dos dados com animação (Spinner)
    df = None
    try:
        if 'Progress' in globals():
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                transient=True
            ) as progress:
                progress.add_task(description="Buscando dados da planilha...", total=None)
                df = pd.read_csv(url_csv, dtype=str)
        else:
            rprint("[blue]Buscando dados da planilha...[/blue]")
            df = pd.read_csv(url_csv, dtype=str)
            
        df.columns = df.columns.str.strip()
    except Exception as e:
        console.print(f"[bold red]❌ Erro ao buscar dados da planilha:[/bold red] {e}")
        return

    # Etapa 2: Exibição de Resumo
    rprint(f"[green]✓[/green] Dados obtidos com sucesso! ({len(df)} registros localizados)\n")

    # Criando tabela visual estilizada
    table = Table(title="Demonstração dos Primeiros Registros")
    for col in df.columns:
        table.add_column(col, style="cyan" if col in ["Produto", "Quantidade"] else "white")

    # Adiciona as primeiras 5 linhas para visualização rápida no terminal
    for _, row in df.head(5).iterrows():
        table.add_row(*[str(row[c]) for c in df.columns])

    console.print(table)
    rprint("\n")

    # Etapa 3: Tratamento e Limpeza
    # Drop da coluna especificada pelo argumento
    colunas_antes = list(df.columns)
    df_filtrado = df.drop(columns=[args.drop_col], errors='ignore')
    
    # Padroniza quantidade para numérico
    col_qtd = next((c for c in df_filtrado.columns if c.lower() == 'quantidade'), None)
    if col_qtd:
        df_filtrado[col_qtd] = pd.to_numeric(df_filtrado[col_qtd], errors='coerce').fillna(0).astype(int)
        total_pecas = df_filtrado[col_qtd].sum()
    else:
        total_pecas = 0

    # Etapa 4: Configuração de nome de arquivo e local de salvamento
    data_hoje = datetime.now().strftime('%d-%m-%Y')
    nome_arquivo = f"arrumação_{data_hoje}.json"

    # Define caminho de saída
    if args.output:
        caminho_saida = args.output
        if not os.path.exists(caminho_saida):
            os.makedirs(caminho_saida, exist_ok=True)
    else:
        # Padrão: Desktop (Área de Trabalho) do usuário
        caminho_saida = os.path.join(os.path.expanduser("~"), "Desktop")

    caminho_completo = os.path.join(caminho_saida, nome_arquivo)

    # Etapa 5: Exportação para JSON
    try:
        df_filtrado.to_json(caminho_completo, orient='records', force_ascii=False, indent=4)
        console.print(Panel(
            f"[green]🎉 Sucesso! Arquivo JSON salvo com sucesso![/green]\n\n"
            f"[bold]Nome do Arquivo:[/bold] {nome_arquivo}\n"
            f"[bold]Localizado em:[/bold] {caminho_completo}\n"
            f"[bold]Total de SKUs:[/bold] {len(df_filtrado)} | [bold]Total de Peças:[/bold] {total_pecas}",
            title="[bold green]Exportação Concluída[/bold green]",
            border_style="green"
        ))
    except Exception as e:
        console.print(f"[bold red]❌ Erro ao salvar arquivo JSON no destino:[/bold red] {e}")
        return

    # Etapa 6: Envio Opcional para API
    if args.send_api:
        rprint(f"\n[blue]🚀 Iniciando transmissão para API: {args.send_api}[/blue]")
        json_payload = json.loads(df_filtrado.to_json(orient='records', force_ascii=False))
        
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(args.send_api, json=json_payload, headers=headers, timeout=10)
            
            if response.status_code in [200, 201, 202]:
                console.print(Panel(
                    f"[green]✓ Carga de dados transmitida com sucesso![/green]\n"
                    f"[bold]Status HTTP:[/bold] {response.status_code}\n"
                    f"[bold]Tamanho do payload:[/bold] {len(json_payload)} itens",
                    title="[bold green]Sincronização API OK[/bold green]",
                    border_style="green"
                ))
            else:
                console.print(Panel(
                    f"[red]❌ Falha ao transmitir dados para API.[/red]\n"
                    f"[bold]Status HTTP:[/bold] {response.status_code}\n"
                    f"[bold]Resposta da API:[/bold] {response.text[:200]}",
                    title="[bold red]Erro na Sincronização[/bold red]",
                    border_style="red"
                ))
        except Exception as api_err:
            console.print(f"[bold red]❌ Falha na conexão com a API:[/bold red] {api_err}")

if __name__ == "__main__":
    main()
