import sqlite3
import pandas as pd
from datetime import datetime

class GeradorRelatorio:
    def __init__(self, db_name="patio.db"):
        self.db_name = db_name

    def gerar_faturamento_json(self):
        with sqlite3.connect(self.db_name) as conn:
            query = "SELECT placa, entrada, saida, valor_pago FROM veiculos WHERE ativo = 0"
            df = pd.read_sql(query, conn)

        if df.empty:
            return {"status": "erro", "mensagem": "Nenhum dado financeiro encontrado."}

        relatorio = {
            "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "total_arrecadado": round(df["valor_pago"].sum(), 2),
            "quantidade_veiculos": len(df),
            "ticket_medio": round(df["valor_pago"].mean(), 2),
            "detalhes": df.to_dict(orient="records")
        }
        return relatorio

    def exportar_para_excel(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                df = pd.read_sql("SELECT * FROM veiculos", conn)
                
            nome_arquivo = f"relatorio_estacionamento_{datetime.now().strftime('%Y%m%d')}.xlsx"
            df.to_excel(nome_arquivo, index=False)
            print(f"✅ Relatório exportado com sucesso: {nome_arquivo}")
        except Exception as e:
            print(f"❌ Erro ao exportar Excel: {e}")


if __name__ == "__main__":
    gerador = GeradorRelatorio()
    
    print("Gerando resumo financeiro...")
    resumo = gerador.gerar_faturamento_json()
    
    if "total_arrecadado" in resumo:
        print(f"💰 Faturamento Total: R$ {resumo['total_arrecadado']}")
        print(f"🚗 Veículos Atendidos: {resumo['quantidade_veiculos']}")
        
        import json
        with open("faturamento.json", "w") as f:
            json.dump(resumo, f, indent=4)
            print("📄 Arquivo faturamento.json criado.")
            
        gerador.exportar_para_excel()