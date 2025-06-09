import requests
import csv
from datetime import datetime

def baixar_selic_formato_usuario(arquivo="selic_atualizada.csv"):
    """
    Baixa SELIC no formato exato do usuário:
    - Mais recente para mais antigo
    - Acumulada atual = 1.0
    - Acumulada = selic_atual + acumulada_próximo_mês
    """
    
    print("🏦 Baixando SELIC no formato do usuário...")
    
    try:
        # 1. Busca dados da API
        response = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json", timeout=30)
        response.raise_for_status()
        dados = response.json()
        
        print(f"✅ Baixados {len(dados)} registros")
        
        # 2. Ordena do mais recente para o mais antigo
        dados.sort(key=lambda x: datetime.strptime(x['data'], '%d/%m/%Y'), reverse=True)
        
        # 3. Calcula acumulada (do presente para o passado)
        registros = []
        
        for i, item in enumerate(dados):
            competencia = datetime.strptime(item['data'], '%d/%m/%Y').date()
            
            # Referência = competencia - 2 meses
            if competencia.month <= 2:
                ref_mes = competencia.month + 10
                ref_ano = competencia.year - 1
            else:
                ref_mes = competencia.month - 2
                ref_ano = competencia.year
            referencia = competencia.replace(year=ref_ano, month=ref_mes, day=1)
            
            selic = float(item['valor'])
            
            # Cálculo da acumulada
            if i == 0:
                # Primeiro (mais recente): acumulada = 1.0
                acumulada = 1.0
            else:
                # Demais: acumulada = selic_atual + acumulada_anterior
                acumulada = selic + registros[i-1]['acumulada']
            
            registros.append({
                'competencia': competencia.strftime('%Y-%m-%d'),
                'referencia': referencia.strftime('%Y-%m-%d'),
                'selic': f"{selic:.2f}",
                'acumulada': acumulada
            })
        
        # 4. Salva CSV
        with open(arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            
            # Header com aspas (formato do usuário)
            writer.writerow(['competencia', 'referencia', 'selic', 'selicacumulada'])
            
            # Dados
            for reg in registros:
                acum_formatada = "1.0" if reg['acumulada'] == 1.0 else f"{reg['acumulada']:.2f}"
                writer.writerow([reg['competencia'], reg['referencia'], reg['selic'], acum_formatada])
        
        # 5. Resumo
        print(f"\n📊 Arquivo gerado: {arquivo}")
        print(f"📈 Registros: {len(registros)}")
        print(f"📅 Período: {registros[-1]['competencia']} até {registros[0]['competencia']}")
        print(f"💹 SELIC atual: {registros[0]['selic']}% (acumulada: {registros[0]['acumulada']})")
        
        # Mostra primeiros registros para validação
        print(f"\n🔍 Primeiros 5 registros:")
        for i in range(min(5, len(registros))):
            r = registros[i]
            print(f"  {r['competencia']}: {r['selic']}% → {r['acumulada']}")
        
        print("\n✅ Download concluído!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

# Uso direto
if __name__ == "__main__":
    baixar_selic_formato_usuario()
