import json
import os
from datetime import datetime
from typing import Dict, List, Optional

DATA_FILE = "mercearia_data.json"


class Mercearia:
    def __init__(self):
        self.produtos: Dict[str, dict] = {}
        self.caixa: float = 0.0
        self.historico: List[dict] = []
        self.carregar_dados()

    def normalizar_nome(self, nome: str) -> str:
        return nome.strip().lower()

    def salvar_dados(self):
        dados = {
            "produtos": self.produtos,
            "caixa": self.caixa,
            "historico": self.historico
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)

    def carregar_dados(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    self.produtos = dados.get("produtos", {})
                    self.caixa = dados.get("caixa", 0.0)
                    self.historico = dados.get("historico", [])
            except Exception:
                print("Erro ao carregar dados. Iniciando novo sistema.")

    def adicionar_produto(self):
        nome = input("Nome do produto: ").strip()
        if not nome:
            print("Nome inválido!")
            return

        nome_norm = self.normalizar_nome(nome)
        if nome_norm in self.produtos:
            print("Produto já existe! Use 'Adicionar estoque' para aumentar quantidade.")
            return

        try:
            preco = float(input("Preço de venda (R$): "))
            estoque_inicial = int(input("Estoque inicial: "))
            if preco < 0 or estoque_inicial < 0:
                print("Valores não podem ser negativos!")
                return
        except ValueError:
            print("Valor inválido!")
            return

        self.produtos[nome_norm] = {
            "nome": nome,
            "preco": preco,
            "estoque": estoque_inicial
        }
        self.registrar_transacao(
            "Cadastro de produto", f"Produto: {nome}", 0.0)
        print(f"Produto '{nome}' cadastrado com sucesso!")
        self.salvar_dados()

    def adicionar_estoque(self):
        self.listar_produtos()
        nome = input("\nNome do produto para adicionar estoque: ").strip()
        nome_norm = self.normalizar_nome(nome)

        if nome_norm not in self.produtos:
            print("Produto não encontrado!")
            return

        try:
            quantidade = int(input("Quantidade a adicionar: "))
            if quantidade <= 0:
                print("Quantidade deve ser positiva!")
                return
        except ValueError:
            print("Quantidade inválida!")
            return

        self.produtos[nome_norm]["estoque"] += quantidade
        print(
            f"Estoque atualizado! Novo estoque: {self.produtos[nome_norm]['estoque']}")
        self.registrar_transacao(
            "Entrada de estoque", f"{quantidade}x {self.produtos[nome_norm]['nome']}", 0.0)
        self.salvar_dados()

    def registrar_transacao(self, tipo: str, descricao: str, valor: float):
        transacao = {
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "tipo": tipo,
            "descricao": descricao,
            "valor": valor
        }
        self.historico.append(transacao)

    def vender(self):
        if not self.produtos:
            print("Nenhum produto cadastrado!")
            return

        self.listar_produtos()
        itens_venda = []
        total_venda = 0.0

        while True:
            nome = input(
                "\nNome do produto (ou 'fim' para finalizar venda): ").strip()
            if nome.lower() == "fim":
                break

            nome_norm = self.normalizar_nome(nome)
            if nome_norm not in self.produtos:
                print("Produto não encontrado!")
                continue

            prod = self.produtos[nome_norm]
            try:
                qtd = int(
                    input(f"Quantidade (estoque disponível: {prod['estoque']}): "))
                if qtd <= 0:
                    print("Quantidade inválida!")
                    continue
                if qtd > prod['estoque']:
                    print("Estoque insuficiente!")
                    continue
            except ValueError:
                print("Quantidade inválida!")
                continue

            subtotal = prod['preco'] * qtd
            itens_venda.append((prod['nome'], qtd, subtotal))
            total_venda += subtotal
            prod['estoque'] -= qtd

        if not itens_venda:
            print("Nenhum item vendido.")
            return

        print("\n" + "="*40)
        print("RESUMO DA VENDA")
        print("="*40)
        for nome_item, qtd, sub in itens_venda:
            print(f"{qtd:2d}x {nome_item:<20} R$ {sub:8.2f}")
        print("-" * 40)
        print(f"Total da venda:          R$ {total_venda:8.2f}")

        # Pagamento
        while True:
            try:
                pago = float(input("\nValor recebido (R$): "))
                if pago < total_venda:
                    print("Valor insuficiente!")
                    continue
                troco = pago - total_venda
                break
            except ValueError:
                print("Valor inválido!")

        self.caixa += total_venda
        print(f"Troco: R$ {troco:.2f}")

        # Registrar transação
        descricao_itens = ", ".join([f"{q}x {n}" for n, q, _ in itens_venda])
        self.registrar_transacao("Venda", descricao_itens, total_venda)
        self.salvar_dados()
        print("Venda registrada com sucesso!")

    def registrar_saida_caixa(self):
        try:
            valor = float(input("Valor da saída (R$): "))
            if valor <= 0:
                print("Valor deve ser positivo!")
                return
            motivo = input(
                "Motivo da saída (ex: pagamento fornecedor, despesa): ").strip()
        except ValueError:
            print("Valor inválido!")
            return

        if valor > self.caixa:
            print("Saldo insuficiente no caixa!")
            return

        self.caixa -= valor
        self.registrar_transacao("Saída de caixa", motivo, -valor)
        self.salvar_dados()
        print("Saída registrada!")

    def ver_caixa(self):
        print("\n" + "="*40)
        print("SITUAÇÃO DO CAIXA")
        print("="*40)
        print(f"Saldo atual: R$ {self.caixa:.2f}")
        print("="*40)

    def listar_produtos(self):
        if not self.produtos:
            print("Nenhum produto cadastrado.")
            return

        print("\n" + "="*60)
        print(f"{'Produto':<25} {'Preço':>10} {'Estoque':>10}")
        print("="*60)
        for prod in self.produtos.values():
            print(
                f"{prod['nome']:<25} R$ {prod['preco']:>8.2f} {prod['estoque']:>10}")
        print("="*60)

    def ver_historico(self):
        if not self.historico:
            print("Nenhum registro ainda.")
            return

        print("\n" + "="*80)
        print("HISTÓRICO DE TRANSAÇÕES")
        print("="*80)
        for trans in reversed(self.historico[-50:]):  
            sinal = "+" if trans['valor'] > 0 else ""
            print(
                f"{trans['data']} | {trans['tipo']:<15} | {trans['descricao']:<40} | {sinal}R$ {trans['valor']:>8.2f}")
        print("="*80)

    def menu(self):
        while True:
            print("\n" + "="*50)
            print("          SISTEMA DE MERCEARIA")
            print("="*50)
            print("1. Cadastrar novo produto")
            print("2. Adicionar estoque")
            print("3. Realizar venda")
            print("4. Registrar saída de caixa")
            print("5. Ver situação do caixa")
            print("6. Listar produtos e estoque")
            print("7. Ver histórico de transações")
            print("8. Sair")
            print("="*50)

            opcao = input("\nEscolha uma opção: ").strip()

            if opcao == "1":
                self.adicionar_produto()
            elif opcao == "2":
                self.adicionar_estoque()
            elif opcao == "3":
                self.vender()
            elif opcao == "4":
                self.registrar_saida_caixa()
            elif opcao == "5":
                self.ver_caixa()
            elif opcao == "6":
                self.listar_produtos()
            elif opcao == "7":
                self.ver_historico()
            elif opcao == "8":
                print("Salvando dados e encerrando...")
                self.salvar_dados()
                break
            else:
                print("Opção inválida!")


if __name__ == "__main__":
    print("Iniciando Sistema de Mercearia...")
    sistema = Mercearia()
    sistema.menu()
