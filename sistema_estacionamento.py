import sqlite3
import re
from datetime import datetime
import pytz  

class Estacionamento:
    def __init__(self):
        self.db = "patio.db"
        self.fuso_brasil = pytz.timezone('America/Sao_Paulo')
        self._criar_banco()

    def _conectar(self):
        return sqlite3.connect(self.db)

    def _criar_banco(self):
        with self._conectar() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS veiculos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    placa TEXT NOT NULL,
                    entrada DATETIME NOT NULL,
                    saida DATETIME,
                    valor_pago REAL,
                    ativo INTEGER DEFAULT 1
                )
            ''')

    def obter_hora_atual(self):
        """Retorna a data e hora atual no fuso horário de Brasília"""
        return datetime.now(self.fuso_brasil)

    def validar_placa(self, placa):
        placa = placa.upper().replace("-", "").replace(" ", "")
        padrao = r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$'
        if re.match(padrao, placa):
            return placa
        return None

    def registrar_entrada(self, placa_crua):
        placa = self.validar_placa(placa_crua)
        if not placa:
            print("❌ ERRO: Placa inválida! Use o padrão ABC1234 ou ABC1D23.")
            return

        if self._buscar_veiculo_ativo(placa):
            print(f"⚠️ AVISO: Veículo {placa} já está no pátio.")
            return

        
        hora_entrada = self.obter_hora_atual()
        
        try:
            with self._conectar() as conn:
                conn.execute("INSERT INTO veiculos (placa, entrada) VALUES (?, ?)", 
                             (placa, hora_entrada.isoformat()))
            print(f"✅ Entrada: {placa} às {hora_entrada.strftime('%H:%M:%S')} (Horário de Brasília)")
        except sqlite3.Error as e:
            print(f"❌ Erro de banco de dados: {e}")

    def registrar_saida(self, placa_crua):
        placa = self.validar_placa(placa_crua)
        if not placa:
            print("❌ ERRO: Placa inválida.")
            return

        registro = self._buscar_veiculo_ativo(placa)
        if not registro:
            print(f"🔍 Veículo {placa} não encontrado no pátio.")
            return

        id_registro, entrada_str = registro
        
        entrada = datetime.fromisoformat(entrada_str)
        saida = self.obter_hora_atual()
        
        duracao = saida - entrada
        segundos_totais = duracao.total_seconds()
        horas = max(1, segundos_totais / 3600)
        
        valor = 10.0 + (max(0, int(horas) - 1) * 5.0)

        with self._conectar() as conn:
            conn.execute('''
                UPDATE veiculos 
                SET saida = ?, valor_pago = ?, ativo = 0 
                WHERE id = ?
            ''', (saida.isoformat(), round(valor, 2), id_registro))
        
        print(f"🏁 Saída: {placa}")
        print(f"⏳ Permanência: {duracao.seconds // 3600}h {(duracao.seconds // 60) % 60}min")
        print(f"💰 Total: R$ {valor:.2f}")

    def _buscar_veiculo_ativo(self, placa):
        with self._conectar() as conn:
            cursor = conn.execute("SELECT id, entrada FROM veiculos WHERE placa = ? AND ativo = 1", 
                                  (placa,))
            return cursor.fetchone()

    def listar_patio(self):
        print("\n" + "="*40)
        print(f"🚗 PÁTIO - {self.obter_hora_atual().strftime('%d/%m/%Y %H:%M')}")
        print("="*40)
        with self._conectar() as conn:
            cursor = conn.execute("SELECT placa, entrada FROM veiculos WHERE ativo = 1")
            dados = cursor.fetchall()
            if not dados:
                print("Pátio vazio.")
            for linha in dados:
                dt_entrada = datetime.fromisoformat(linha[1])
                print(f"🔹 {linha[0]} | Entrada: {dt_entrada.strftime('%H:%M:%S')}")
        print("="*40 + "\n")

estacionamento = Estacionamento()

while True:
    print("1. Entrada | 2. Saída | 3. Listar | 4. Sair")
    opcao = input("👉 Escolha: ")

    if opcao == "1":
        p = input("Placa: ")
        estacionamento.registrar_entrada(p)
    elif opcao == "2":
        p = input("Placa: ")
        estacionamento.registrar_saida(p)
    elif opcao == "3":
        estacionamento.listar_patio()
    elif opcao == "4":
        break
    else:
        print("Opção inválida.")