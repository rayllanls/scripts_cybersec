"""
╔═══════════════════════════════════════════╗
║      SCOPA - Vassoura de Rede! 🧹         ║
║    Script de Reconhecimento de Rede       ║
║          Rayllan Leitão                   ║
╚═══════════════════════════════════════════╝
"""

import subprocess
import sys
import re
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init()

def banner():
    """Exibe o banner do Scopa com cores"""
    print(f"\n{Fore.CYAN}{'═'*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  ____   ____ ___  ____   _     {Style.RESET_ALL}")
    print(f"{Fore.YELLOW} / ___| / ___/ _ \\|  _ \\ / \\   {Style.RESET_ALL}")
    print(f"{Fore.YELLOW} \\___ \\| |  | | | | |_) / _ \\  {Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  ___) | |__| |_| |  __/ ___ \\ {Style.RESET_ALL}")
    print(f"{Fore.YELLOW} |____/ \\____\\___/|_| /_/   \\_\\ {Style.RESET_ALL}")
    print(f"\n{Fore.GREEN}    🧹 Vassoura de Rede! 🧹{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}         Rayllan Leitão{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═'*50}{Style.RESET_ALL}")

def verificar_nmap():
    """Verifica se o Nmap está instalado"""
    try:
        subprocess.run(['nmap', '--version'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def validar_subnet(subnet):
    """Valida o formato básico da sub-rede"""
    padrao = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    return re.match(padrao, subnet) is not None

def executar_scan(subnet):
    """Executa o scan Nmap na sub-rede"""
    print(f"{Fore.CYAN}[*] Iniciando varredura em: {subnet}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Isso pode levar alguns segundos ou minutos...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] Aguarde enquanto Scopa varre a rede... 🧹{Style.RESET_ALL}\n")

    try:
        resultado = subprocess.run(
            ['nmap', '-sn', '-oG', '-', subnet],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return resultado.stdout
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}[!] Erro ao executar Nmap: {e}{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.RED}[!] Erro inesperado: {e}{Style.RESET_ALL}")
        return None

def processar_resultado(saida_nmap):
    """Processa a saída do Nmap e retorna lista de hosts"""
    hosts = []

    if not saida_nmap:
        return hosts

    for linha in saida_nmap.split('\n'):
        if linha.startswith('Host:'):
            partes = linha.split()
            if len(partes) >= 2:
                ip = partes[1]
                hostname = "(Sem hostname)"
                if len(partes) >= 3:
                    hostname = partes[2].strip('()')
                hosts.append({'ip': ip, 'hostname': hostname})

    return hosts

def exibir_tabela(hosts):
    """Exibe os resultados em formato de tabela com cores"""
    if not hosts:
        print(f"{Fore.RED}[!] Nenhum host ativo encontrado na sub-rede.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.CYAN}{'═'*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'ENDEREÇO IP':<20} | {'HOSTNAME':<45}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")

    for host in hosts:
        print(f"{Fore.WHITE}{host['ip']:<20} | {host['hostname']:<45}{Style.RESET_ALL}")

    print(f"{Fore.CYAN}{'═'*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[✓] Total de hosts ativos encontrados: {len(hosts)}{Style.RESET_ALL}")

def salvar_txt(hosts, subnet, nome_arquivo):
    """Salva os resultados em formato TXT na pasta /resultados"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    diretorio = "resultados"
    os.makedirs(diretorio, exist_ok=True)  # Cria a pasta se não existir

    nome_base = f"scopa_scan_{timestamp}" if not nome_arquivo else nome_arquivo
    if not nome_base.endswith('.txt'):
        nome_base += '.txt'

    arquivo = os.path.join(diretorio, nome_base)

    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(f"SCOPA - Scan de Rede\n")
        f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Sub-rede: {subnet}\n")
        f.write(f"Total de hosts: {len(hosts)}\n")
        f.write("="*70 + "\n\n")

        for host in hosts:
            f.write(f"IP: {host['ip']:<20} | Hostname: {host['hostname']}\n")

    print(f"{Fore.GREEN}[Checkmark] Resultados salvos em: {arquivo}{Style.RESET_ALL}")
    return arquivo

def salvar_xml(hosts, subnet, nome_arquivo):
    """Salva os resultados em formato XML na pasta /resultados"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    diretorio = "resultados"
    os.makedirs(diretorio, exist_ok=True)

    nome_base = f"scopa_scan_{timestamp}" if not nome_arquivo else nome_arquivo
    if not nome_base.endswith('.xml'):
        nome_base += '.xml'

    arquivo = os.path.join(diretorio, nome_base)

    root = ET.Element("scopa_scan")
    metadata = ET.SubElement(root, "metadata")
    ET.SubElement(metadata, "datetime").text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ET.SubElement(metadata, "subnet").text = subnet
    ET.SubElement(metadata, "total_hosts").text = str(len(hosts))

    hosts_elem = ET.SubElement(root, "hosts")
    for host in hosts:
        host_elem = ET.SubElement(hosts_elem, "host")
        ET.SubElement(host_elem, "ip").text = host['ip']
        ET.SubElement(host_elem, "hostname").text = host['hostname']

    xml_str = minidom.parseString(ET.tostring(root, encoding='unicode')).toprettyxml(indent="    ")

    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(xml_str)

    print(f"{Fore.GREEN}[Checkmark] Resultados salvos em: {arquivo}{Style.RESET_ALL}")
    return arquivo

def main():
    """Função principal"""
    banner()

    if not verificar_nmap():
        print(f"{Fore.RED}[!] ERRO: Nmap não está instalado!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[i] Instale com: sudo apt install nmap (Debian/Ubuntu){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[i]            ou: sudo yum install nmap (RedHat/CentOS){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[i]            ou: brew install nmap (macOS){Style.RESET_ALL}")
        sys.exit(1)

    print(f"\n{Fore.CYAN}[?] Exemplos de sub-rede: 192.168.1.0/24, 10.0.0.0/24{Style.RESET_ALL}")
    subnet = input(f"{Fore.CYAN}[>] Informe a sub-rede: {Style.RESET_ALL}").strip()

    if not subnet:
        print(f"{Fore.RED}[!] Erro: Nenhuma sub-rede informada. Saindo.{Style.RESET_ALL}")
        sys.exit(1)

    if not validar_subnet(subnet):
        print(f"{Fore.RED}[!] Erro: Formato de sub-rede inválido!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[i] Use o formato: 192.168.1.0/24{Style.RESET_ALL}")
        sys.exit(1)

    saida = executar_scan(subnet)

    if saida:
        hosts = processar_resultado(saida)
        exibir_tabela(hosts)

        print(f"\n{Fore.CYAN}[?] Deseja salvar os resultados em arquivos TXT e XML? (s/N): {Style.RESET_ALL}", end="")
        salvar = input().strip().lower()

        if salvar == 's':
            print(f"{Fore.CYAN}[>] Informe o nome base do arquivo (ou pressione Enter para nome padrão): {Style.RESET_ALL}", end="")
            nome_arquivo = input().strip()
            salvar_txt(hosts, subnet, nome_arquivo)
            salvar_xml(hosts, subnet, nome_arquivo)

    print(f"\n{Fore.GREEN}[✓] Varredura concluída. Até logo! 🧹{Style.RESET_ALL}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Varredura interrompida pelo usuário. Saindo...{Style.RESET_ALL}")
        sys.exit(0)
