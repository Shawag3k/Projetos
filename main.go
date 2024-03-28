package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	tasks := []string{}

	for {
		fmt.Println("\n1. Adicionar tarefa")
		fmt.Println("2. Exibir tarefas")
		fmt.Println("3. Sair")
		fmt.Print("Escolha uma opção: ")

		var choice int
		fmt.Scanln(&choice)

		switch choice {
		case 1:
			fmt.Print("Digite a tarefa: ")
			scanner := bufio.NewScanner(os.Stdin)
			scanner.Scan()
			task := scanner.Text()
			tasks = append(tasks, task)
			fmt.Println("Tarefa adicionada com sucesso!")
		case 2:
			fmt.Println("\n--- Tarefas ---")
			for i, task := range tasks {
				fmt.Printf("%d. %s\n", i+1, task)
			}
		case 3:
			fmt.Println("Saindo...")
			return
		default:
			fmt.Println("Opção inválida. Por favor, escolha novamente.")
		}
	}
}
