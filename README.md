# Lutador X Samurai Plataforma

Bem-vindo ao **Fighter X Samurai Platform**! Um jogo de plataforma 2D cheio de ação, criado com o framework Pygame Zero em Python.

![Captura de tela 2025-07-04 131543](https://github.com/user-attachments/assets/bd4f7708-c02a-43b7-b62e-cea829d23a3e)
![Captura de tela 2025-07-04 131601](https://github.com/user-attachments/assets/be79c902-0f25-4bcb-b114-11a51c69564c)

---

## 📜 Sobre o Jogo

Neste jogo, você controla um herói habilidoso em uma missão para derrotar samurais inimigos em um cenário desafiador. Pule entre plataformas, desvie dos ataques e use sua própria habilidade de atirar para limpar o caminho. Colete a moeda dourada e derrote todos os inimigos para alcançar a vitória!

---

## ✨ Funcionalidades

* **Movimentação Clássica:** Controles de plataforma para andar, correr e pular.
* **Combate Dinâmico:** Ataque inimigos com projéteis e desvie de seus ataques de contato.
* **IA Inimiga:** Os inimigos patrulham, param para observar e se tornam agressivos, perseguindo você ao serem atacados ou ao vê-lo.
* **Sistema de Vida e Pontuação:** O herói tem 5 vidas. Cada inimigo derrotado vale +1 ponto e a moeda especial vale +3 pontos.
* **Animações Ricas:** Todos os personagens possuem animações de sprite para andar, correr, ficar parado e atacar.
* **Ciclo Completo de Jogo:** Menu principal, tela de jogo, tela de vitória e tela de game over.
* **Controle de Som:** Ligue ou desligue a música e os efeitos sonoros diretamente do menu.

---

## 🎮 Como Jogar

### Controles do Herói

| Tecla | Ação |
| :--- | :--- |
| **← / →** (Setas) | Mover para a Esquerda / Direita |
| **Shift** (Esquerdo ou Direito) | Correr (enquanto se move) |
| **Barra de Espaço** | Pular |
| **Z** | Atirar Projétil |

### Objetivo

Para vencer a fase, você precisa cumprir **duas condições**:
1.  Derrotar os **2 samurais** inimigos.
2.  Coletar a **moeda dourada** que está na plataforma mais alta.

Cuidado! Se um samurai tocar em você 5 vezes, ou se você cair das plataformas, é Game Over!

---

## 🛠️ Instalação e Execução

Este jogo foi desenvolvido em Python com a biblioteca PgZero, math, random e Rect do Pygame

### Pré-requisitos

-   Python 3.x
-   Pygame
-   Pygame Zero

### Como Instalar as Bibliotecas

Se você não tiver as bibliotecas necessárias, abra seu terminal (Prompt de Comando, PowerShell, etc.) e instale-as usando o `pip`:

```bash
pip install pygame pgzero
```

### Como Rodar o Jogo

1.  Clone ou baixe este repositório para o seu computador.
2.  Navegue até a pasta do projeto pelo terminal.
3.  Execute o jogo com o seguinte comando:

```bash
python Jogo.py
```

---

## 📁 Estrutura do Projeto

Para que o jogo funcione corretamente, os arquivos de assets (imagens e sons) devem estar organizados nas seguintes pastas dentro do diretório principal:

-   **/images/**: Contém todos os arquivos `.png` para os sprites (herói, inimigo, moeda, corações, etc.).
-   **/sounds/**: Contém todos os arquivos de efeitos sonoros `.wav` ou `.ogg` (pulo, tiro, dano, etc.).
-   **/music/**: Contém o arquivo da música de fundo `.ogg` ou `.mp3`.

---
*Este projeto foi desenvolvido como parte de um processo seletivo, aprendizado e exploração da criação de jogos com Python.*
