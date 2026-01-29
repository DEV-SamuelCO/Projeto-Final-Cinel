# Projeto Final – Aplicação de Produtividade em Python

Este é um projeto pessoal desenvolvido como **trabalho final da Cinel**, com o objetivo de demonstrar competências em **Python**, **automação**, **interfaces gráficas**, **OCR** e **integração com APIs**.

A aplicação é um **software desktop** focado em produtividade, automação de tarefas e acessibilidade, reunindo várias ferramentas num único ambiente.

---

## 🚀 Funcionalidades Principais

### 🔹 Gestor de Atalhos
- Criação de atalhos personalizados
- Abertura rápida de:
  - Programas
  - Sites
  - Pastas
- Edição e remoção de atalhos
- Atalhos associados a cada utilizador

### 🔹 Gestor de Macros
- Gravação de ações automáticas (cliques e teclas)
- Execução e paragem de macros
- Ideal para tarefas repetitivas
- Utiliza **PyAutoGUI**

### 🔹 Tradutor Inteligente
- Captura de texto diretamente da tela
- Reconhecimento de texto via **OCR**
- Tradução automática do conteúdo capturado
- Visualização do texto original e traduzido lado a lado
- Integração com **Google Translate / Gemini API**

### 🔹 Sistema de Autenticação
- Login e registo de utilizadores
- Preferências guardadas localmente
- Atalhos, macros e histórico associados ao utilizador

---

## 🧠 Tecnologias Utilizadas

- **Python 3**
- **Flet** ou **Tkinter** (Interface gráfica)
- **SQLite** (Base de dados local)
- **PyAutoGUI** (Automação e macros)
- **EasyOCR / Pytesseract** (OCR)
- **Requests**
- **Google Translate / Gemini API**

---

## 🗂️ Estrutura do Projeto

/Projeto_Final
│
├── main.py # Ponto de entrada da aplicação
├── database.py # Gestão da base de dados SQLite
│
├── auth/ # Login e registo
├── atalhos/ # Gestão de atalhos
├── macros/ # Gravação e execução de macros
├── tradutor/ # OCR e tradução
│
├── assets/ # Recursos visuais
└── README.md
