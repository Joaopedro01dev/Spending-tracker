import click
import csv
import os
from rich.console import Console
from rich.table import Table
from datetime import datetime

ARQUIVO = "expenses.csv"
console = Console()

def criar_arquivo():

    if not os.path.exists(ARQUIVO):

        with open(ARQUIVO, "w", newline="", encoding="utf-8") as arquivo:
            writer = csv.writer(arquivo)

            writer.writerow(["ID", "Data", "Descricao", "Valor", "Categoria"])

def proximo_id() -> int:

    with open(ARQUIVO, "r", encoding="utf-8") as arquivo:

        reader = list(csv.reader(arquivo))
        ids = []

        for linha in reader[1:]:
            if linha:
                ids.append(int(linha[0]))

        if not ids:
            return 1

        return max(ids) + 1

def validar_data(ctx, param, value):
    if value is None:
        return value
    
    try:
        datetime.strptime(value, "%m/%Y")
        return value

    except ValueError:
        raise click.BadParameter("Formato inválido. Use MM/YYYY.")
    
def pedir_data():
    while True:
        data = click.prompt("Digite a data (DD/MM/YYYY)")

        try:
            datetime.strptime(data, "%d/%m/%Y")
            return data
        
        except ValueError:
            click.echo("Data inválida!")

#add
categorias = {
    1: "Alimentação",
    2: "Transporte",
    3: "Moradia",
    4: "Saúde",
    5: "Outros"
}

@click.group()
def cli():
    pass

@cli.command(help="Adiciona uma nova despesa.")
def add():
    criar_arquivo()

    data = pedir_data()
    descricao = click.prompt("Digite a descrição:")
    valor = click.prompt("Digite o valor: ", type=float)

    click.echo("\nEscolha a categoria: ")
    for num, nome in categorias.items():
        click.echo(f"{num}. {nome}")

    categoria_numero = click.prompt("Digite o número correspondente: ", type=int)

    while categoria_numero not in categorias:
        click.echo("Categoria inválida!")
        categoria_numero = click.prompt("Digite novamente: ", type=int)

    categoria = categorias[categoria_numero]
    novo_id = proximo_id()

    with open(ARQUIVO, "a", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)

        writer.writerow([novo_id, data, descricao, valor, categoria])

    click.echo(f"\nDespesa com ID {novo_id} adicionada com sucesso!")

#edit
@cli.command(help="Editar uma despesa existente.")
@click.argument("id", type=int)
def edit(id):
    lista = []
    despesa_encontrada = False

    with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
        reader = csv.reader(arquivo)

        for linha in reader:
            lista.append(linha)

    for i in range(1, len(lista)):
        linha = lista[i]

        id_atual = int(linha[0])

        if id_atual == id:
            despesa_encontrada = True

            click.echo(f"Editando despesa com ID: {id}")
            nova_data = click.prompt(f"Data atual: {linha[1]}. Digite a nova data (DD/MM/YYYY) ou pressione Enter para manter", default=linha[1])
            nova_descricao = click.prompt(f"Descrição atual: {linha[2]}. Digite a nova descrição ou pressione Enter para manter", default=linha[2])
            novo_valor = click.prompt(f"Valor atual: {linha[3]}. Digite o novo valor ou pressione Enter para manter", type=float, default=float(linha[3]))
            click.echo(f"Categoria atual: {linha[4]}. Escolha uma nova categoria ou pressione Enter para manter:")

            click.echo("\nEscolha a categoria: ")
            for num, nome in categorias.items():
                click.echo(f"{num}. {nome}")

            categoria_atual = linha[4]
            numero_categoria_atual = None

            for num, nome in categorias.items():
                if nome == categoria_atual:
                    numero_categoria_atual = num
                    break
            

            categoria_numero = click.prompt("Digite o número correspondente", type=int, default=numero_categoria_atual)

            while categoria_numero not in categorias:
                click.echo("Categoria inválida!")
                categoria_numero = click.prompt("Digite novamente: ", type=int)

            categoria = categorias[categoria_numero]

            lista[i] = [id, nova_data, nova_descricao, novo_valor, categoria]
            break

    if not despesa_encontrada:
        click.echo(f"Despesa com o ID {id} não encontrada!")
        return
    
    with open(ARQUIVO, "w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)

        writer.writerows(lista)

    click.echo(f"\nDespesa com ID {id} atualizada com sucesso!")

#delete           
@cli.command(help="Deletar uma despesa existente.")
@click.argument("id", type=int)
def delete(id):
    lista = []
    despesa_encontrada = False

    with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
        reader = csv.reader(arquivo)

        for linha in reader:
            lista.append(linha)

    for i in range(1, len(lista)):
        linha = lista[i]

        id_atual = int(linha[0])

        if id_atual == id:
            despesa_encontrada = True
            lista.pop(i)

            break
    
    if not despesa_encontrada:
        click.echo(f"Despesa com o ID {id} não encontrada!")
        return
    
    with open(ARQUIVO, "w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerows(lista)

    click.echo(f"\nDespesa com ID {id} deletada com sucesso!")

#list       
@cli.command(name="list", help="Exibe todas as despesas registradas no sistema.")
@click.option("--category", help="Filtra as despesas por categoria.", type=click.Choice(["Alimentação", "Transporte", "Moradia", "Saúde", "Outros"], case_sensitive=False))
@click.option("--month-year", callback=validar_data ,help="Filtra as despesas de um mês/ano específico (formato MM/YYYY).")
def listar(category, month_year):
    criar_arquivo()

    tabela = Table(title="Despesas")

    tabela.add_column("ID", style="blue", justify="center")
    tabela.add_column("Data", style="green")
    tabela.add_column("Descrição", style="white")
    tabela.add_column("Valor", style="yellow")
    tabela.add_column("Categoria", style="red")

    possui_dados = False
    total = 0.0

    with open(ARQUIVO, "r", encoding="utf-8") as arquivo:

        reader = csv.reader(arquivo)
        next(reader, None)

        for linha in reader:

            if not linha:
                continue

            id_despesa = linha[0]
            data = linha[1]
            descricao = linha[2]
            valor = linha[3]
            categoria_despesa = linha[4]

            if category:
                if categoria_despesa.lower() != category.lower():
                    continue

            if month_year:
                mes_ano = data[3:]
                if mes_ano != month_year:
                    continue

            possui_dados = True
            total += float(valor)
            tabela.add_row(id_despesa, data, descricao, f"R$ {valor}", categoria_despesa)

    if not possui_dados:
        console.print("[red]Nenhuma despesa encontrada.[/red]")
        return

    tabela.add_row("Total", "", "", f"{total:.2f}", "")
    console.print(tabela)

#resume
@cli.command(name="resume", help="Exibir o resumo financeiro mensal.")
@click.argument("data_resume", callback=validar_data)
def resume(data_resume):
    criar_arquivo()

    gastos_categoria = {}
    total_geral = 0

    with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
        reader = csv.reader(arquivo)
        next(reader)

        for linha in reader:
            if not linha: 
                continue
        
            data = linha[1]
            valor = float(linha[3])
            categoria = linha[4]

            mes_ano = data[3:]
            if mes_ano != data_resume:
                continue

            total_geral += valor
            if categoria not in gastos_categoria:
                gastos_categoria[categoria] = 0

            gastos_categoria[categoria] += valor

    if total_geral == 0:
        console.print("[red]Nenhuma despesa encontrada para este período.[/red]")
        return
    
    data_obj = datetime.strptime(data_resume, "%m/%Y")
    nome_mes = data_obj.strftime("%B/%Y")

    tabela = Table(title=f"Resumo fincanceiro: {nome_mes.capitalize()}")
    tabela.add_column("Categori", style="cyan")
    tabela.add_column("Valor", style="green")
    tabela.add_column("Percentual", style="yellow")

    for categoria, valor in gastos_categoria.items():
        percentual = (valor / total_geral) * 100

        tabela.add_row(categoria, f"{valor:.2f}", f"{percentual:.2f}%")

    tabela.add_section()
    tabela.add_row(
        "[green]Total Geral[/green]",
        f"[green]{total_geral:.2f}[/green]",
        "[green]100.0%[/green]"
    )

    console.print(tabela)

if __name__ == "__main__":
    cli()